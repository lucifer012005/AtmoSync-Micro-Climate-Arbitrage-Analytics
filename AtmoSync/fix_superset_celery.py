import ast
import shutil
from datetime import datetime
from pathlib import Path

# Superset configuration location
CONFIG_FILE = Path(
    r"C:\superset\docker\pythonpath_dev\superset_config.py"
)

MISSING_MODULES = {
    "superset.tasks.deletion_retention",
    "superset.tasks.export_dashboard_excel",
}

MISSING_TASK = "deletion_retention.purge_soft_deleted"


def main():
    if not CONFIG_FILE.exists():
        print("ERROR: Superset configuration file not found.")
        return

    original = CONFIG_FILE.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)

    tree = ast.parse(original)

    celery_class = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef)
            and node.name == "CeleryConfig"
        ),
        None,
    )

    if celery_class is None:
        print("ERROR: CeleryConfig class not found.")
        return

    assignments = {}

    for node in celery_class.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = node.value

    imports = assignments.get("imports")
    schedule = assignments.get("beat_schedule")

    if not isinstance(imports, (ast.Tuple, ast.List)):
        print("ERROR: Celery imports configuration not found.")
        return

    if not isinstance(schedule, ast.Dict):
        print("ERROR: Celery beat_schedule not found.")
        return

    remove_lines = set()

    # Remove unavailable Celery modules
    for module in imports.elts:
        if (
            isinstance(module, ast.Constant)
            and module.value in MISSING_MODULES
        ):
            remove_lines.add(module.lineno)

            print("Removing module:", module.value)

    # Remove unavailable scheduled task
    for key, value in zip(schedule.keys, schedule.values):
        if (
            isinstance(key, ast.Constant)
            and key.value == MISSING_TASK
        ):
            for number in range(
                key.lineno,
                value.end_lineno + 1,
            ):
                remove_lines.add(number)

            # Remove comments belonging to this task
            previous = key.lineno - 1

            while (
                previous > 0
                and lines[previous - 1].strip().startswith("#")
            ):
                remove_lines.add(previous)
                previous -= 1

            print("Removing scheduled task:", MISSING_TASK)

    if not remove_lines:
        print("Configuration already corrected.")
        return

    updated = "".join(
        line
        for number, line in enumerate(lines, start=1)
        if number not in remove_lines
    )

    # Validate syntax before saving
    ast.parse(updated)

    # Backup original configuration
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup = CONFIG_FILE.with_name(
        f"superset_config.py.backup_{timestamp}"
    )

    shutil.copy2(CONFIG_FILE, backup)

    print("Backup created:", backup)

    # Save corrected configuration
    CONFIG_FILE.write_text(
        updated,
        encoding="utf-8",
    )

    print("=" * 45)
    print("SUPERSET CELERY CONFIGURATION FIXED")
    print("=" * 45)
    print("Missing modules removed.")
    print("Invalid scheduled task removed.")
    print("Redis and PostgreSQL settings preserved.")
    print("Original configuration backed up.")
    print("=" * 45)


if __name__ == "__main__":
    main()