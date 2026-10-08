from pathlib import Path
import hashlib
import json
import os
import smtplib
import ssl
from email.message import EmailMessage

import snowflake.connector
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
STATE_FILE = LOG_DIR / "email_alert_state.json"

LOG_DIR.mkdir(exist_ok=True)

load_dotenv(ROOT / ".env")


required_variables = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
    "EMAIL_SENDER",
    "EMAIL_APP_PASSWORD",
    "EMAIL_RECIPIENT",
]

missing = [name for name in required_variables if not os.getenv(name)]

if missing:
    raise RuntimeError(
        "Missing environment variables: " + ", ".join(missing)
    )


def get_alerts():
    connection = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )

    query = """
        SELECT
            CONTAINER_ID,
            COMMODITY,
            ORIGIN,
            CURRENT_DESTINATION,
            ALTERNATIVE_MARKET,
            TEMPERATURE_C,
            HUMIDITY_PCT,
            CONTAINER_STATUS,
            DISTANCE_KM,
            TRAVEL_TIME_HOURS,
            PRICE_PER_KG,
            QUALITY_PREMIUM,
            REROUTE_RECOMMENDATION
        FROM REROUTING_RECOMMENDATIONS
        WHERE REROUTE_RECOMMENDATION IN (
            'REROUTE RECOMMENDED',
            'CONSIDER REROUTE'
        )
        ORDER BY
            CASE
                WHEN REROUTE_RECOMMENDATION = 'REROUTE RECOMMENDED'
                THEN 1
                ELSE 2
            END,
            CONTAINER_ID
    """

    cursor = connection.cursor()

    try:
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]

        rows = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        return rows

    finally:
        cursor.close()
        connection.close()


def signature_for(alerts):
    content = json.dumps(
        alerts,
        sort_keys=True,
        default=str,
    )

    return hashlib.sha256(content.encode()).hexdigest()


def previous_signature():
    if not STATE_FILE.exists():
        return None

    try:
        data = json.loads(STATE_FILE.read_text())
        return data.get("signature")
    except Exception:
        return None


def save_signature(signature):
    STATE_FILE.write_text(
        json.dumps(
            {"signature": signature},
            indent=2,
        )
    )


def send_email(alerts):
    sender = os.getenv("EMAIL_SENDER")
    recipients = [
        address.strip()
        for address in os.getenv("EMAIL_RECIPIENT").split(",")
        if address.strip()
    ]

    message = EmailMessage()

    urgent = sum(
        1
        for item in alerts
        if item["REROUTE_RECOMMENDATION"] == "REROUTE RECOMMENDED"
    )

    message["Subject"] = (
        f"[AtmoSync Alert] {urgent} urgent reroute(s) "
        f"- {len(alerts)} total recommendation(s)"
    )

    message["From"] = sender
    message["To"] = ", ".join(recipients)

    body = [
        "ATMOSYNC - MICRO-CLIMATE ARBITRAGE ALERT",
        "=" * 45,
        "",
    ]

    for index, alert in enumerate(alerts, start=1):
        body.extend(
            [
                f"Alert #{index}",
                f"Container: {alert['CONTAINER_ID']}",
                f"Commodity: {alert['COMMODITY']}",
                f"Origin: {alert['ORIGIN']}",
                f"Current Destination: {alert['CURRENT_DESTINATION']}",
                f"Recommended Market: {alert['ALTERNATIVE_MARKET']}",
                f"Temperature: {alert['TEMPERATURE_C']} C",
                f"Humidity: {alert['HUMIDITY_PCT']} %",
                f"Container Status: {alert['CONTAINER_STATUS']}",
                f"Distance: {alert['DISTANCE_KM']} km",
                f"Travel Time: {alert['TRAVEL_TIME_HOURS']} hours",
                f"Price/kg: {alert['PRICE_PER_KG']}",
                f"Quality Premium: {alert['QUALITY_PREMIUM']}",
                (
                    "Recommendation: "
                    f"{alert['REROUTE_RECOMMENDATION']}"
                ),
                "-" * 45,
                "",
            ]
        )

    message.set_content("\n".join(body))

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.starttls(context=context)
        server.login(
            sender,
            os.getenv("EMAIL_APP_PASSWORD"),
        )
        server.send_message(message)


def main():
    alerts = get_alerts()

    if not alerts:
        print("No rerouting alerts found.")

        # Reset state so a future alert can be sent again.
        save_signature("")

        return

    current_signature = signature_for(alerts)

    if current_signature == previous_signature():
        print(
            "No new or changed rerouting alerts. "
            "Email not sent."
        )
        return

    send_email(alerts)

    save_signature(current_signature)

    print(
        f"Email alert sent successfully. "
        f"Alerts: {len(alerts)}"
    )


if __name__ == "__main__":
    main()