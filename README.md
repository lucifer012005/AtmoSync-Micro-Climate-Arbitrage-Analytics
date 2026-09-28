# AtmoSync – Micro-Climate Arbitrage Analytics
## Architecture

```text
Python IoT Simulator
        ↓
      Kafka
        ↓
    Snowflake
        ↓
       dbt
        ↓
 Apache Superset
```

## Tech Stack

- Python
- Apache Kafka
- Snowflake
- dbt
- Apache Superset
- Git & GitHub
- uv for Python environment/dependency management

## Project Structure

```text
AtmoSync/
│
├── simulator/       # IoT sensor data generator
├── kafka/           # Kafka producer/consumer
├── snowflake/       # Snowflake SQL and ingestion
├── dbt_atmosync/    # dbt transformations
├── superset/        # Dashboard-related files
├── data/            # Reference/sample data
│
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd AtmoSync-Micro-Climate-Arbitrage-Analytics
```

### 2. Install uv

Make sure `uv` is installed on your system.

### 3. Set up the project environment

```bash
uv sync
```

This automatically creates `.venv` and installs the required dependencies.

You do **not** need to manually create a virtual environment.

### 4. Run Python scripts

Example:

```bash
uv run python simulator/sensor_simulator.py
```

## Team Workflow

Create a separate branch for your assigned component.

```bash
git checkout -b feature/your-feature
```

After making changes:

```bash
git add .
git commit -m "Describe your changes"
git push -u origin feature/your-feature
```

Then create a Pull Request to merge your branch into `main`.

### Suggested Branches

```text
feature/iot-simulator
feature/kafka-pipeline
feature/snowflake-dbt
feature/superset-dashboard
```

## Important

Do not commit:

```text
.venv/
.env
credentials
API keys
```

If new dependencies are added, commit the updated `pyproject.toml` and `uv.lock`.

Other team members should then run:

```bash
git pull
uv sync
```

## Project Goal

Build an end-to-end streaming pipeline:

**IoT Telemetry → Kafka → Snowflake → dbt → Superset**

The final dashboard should help identify **at-risk containers and potential rerouting opportunities before commodity quality degrades**.
