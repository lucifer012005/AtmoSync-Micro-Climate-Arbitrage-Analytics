import json
import os

from kafka import KafkaConsumer
import snowflake.connector


# Kafka configuration
KAFKA_SERVER = "localhost:9092"
KAFKA_TOPIC = "iot_telemetry"


# Snowflake configuration
SNOWFLAKE_ACCOUNT = os.environ["SNOWFLAKE_ACCOUNT"]
SNOWFLAKE_USER = os.environ["SNOWFLAKE_USER"]
SNOWFLAKE_PASSWORD = os.environ["SNOWFLAKE_PASSWORD"]

SNOWFLAKE_DATABASE = "ATMOSYNC_DB"
SNOWFLAKE_SCHEMA = "RAW"
SNOWFLAKE_WAREHOUSE = "ATMOSYNC_WH"
SNOWFLAKE_ROLE = "ACCOUNTADMIN"


def create_snowflake_connection():
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAKE_ROLE
    )


def insert_into_snowflake(cursor, data):
    sql = """
        INSERT INTO ATMOSYNC_DB.RAW.RAW_IOT_DATA
        (
            CONTAINER_ID,
            COMMODITY,
            ORIGIN,
            DESTINATION,
            TEMPERATURE_C,
            HUMIDITY_PCT,
            VIBRATION_G,
            EVENT_TIMESTAMP
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (
            data["container_id"],
            data["commodity"],
            data["origin"],
            data["destination"],
            data["temperature_c"],
            data["humidity_pct"],
            data["vibration_g"],
            data["timestamp"]
        )
    )


def main():
    print("Connecting to Snowflake...")

    connection = create_snowflake_connection()
    cursor = connection.cursor()

    print("Snowflake connection successful.")

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="atmosync-snowflake-loader"
    )

    print("AtmoSync Kafka → Snowflake consumer started.")
    print("Waiting for telemetry messages...")

    try:
        for message in consumer:
            data = message.value

            insert_into_snowflake(cursor, data)
            connection.commit()

            print(
                f"Loaded: {data['container_id']} | "
                f"{data['commodity']} | "
                f"{data['temperature_c']}°C | "
                f"{data['humidity_pct']}%"
            )

    except KeyboardInterrupt:
        print("\nConsumer stopped.")

    finally:
        consumer.close()
        cursor.close()
        connection.close()
        print("Connections closed.")


if __name__ == "__main__":
    main()