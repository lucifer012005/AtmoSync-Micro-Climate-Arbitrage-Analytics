import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

KAFKA_SERVER = "localhost:9092"
TOPIC = "iot_telemetry"
DLQ_TOPIC = "iot_telemetry_dlq"

CONTAINERS = ["CONT-A001", "CONT-A002", "CONT-A003", "CONT-A004", "CONT-A005"]
COMMODITIES = ["Avocado", "Mango", "Banana", "Tomato"]
ROUTES = [
    ("Mumbai", "Pune"),
    ("Nashik", "Mumbai"),
    ("Bengaluru", "Hyderabad"),
    ("Delhi", "Jaipur"),
    ("Pune", "Mumbai")
]

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)

def validate_telemetry(payload):
    """Validates required keys and physical threshold ranges."""
    required_keys = {"container_id", "commodity", "origin", "destination", "temperature_c", "humidity_pct", "vibration_g", "timestamp"}
    if not required_keys.issubset(payload.keys()):
        raise ValueError(f"Missing mandatory fields: {required_keys - payload.keys()}")
    if not (-20 <= payload["temperature_c"] <= 50):
        raise ValueError(f"Temperature value out of bounds: {payload['temperature_c']}")
    return True

def generate_event():
    origin, destination = random.choice(ROUTES)

    temperature = round(random.uniform(4, 12), 2)
    humidity = round(random.uniform(60, 95), 2)
    vibration = round(random.uniform(0.1, 5.0), 2)

    if random.random() < 0.15:
        temperature = round(random.uniform(13, 20), 2)

    if random.random() < 0.15:
        humidity = round(random.uniform(90, 100), 2)

    return {
        "container_id": random.choice(CONTAINERS),
        "commodity": random.choice(COMMODITIES),
        "origin": origin,
        "destination": destination,
        "temperature_c": temperature,
        "humidity_pct": humidity,
        "vibration_g": vibration,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

print("AtmoSync Kafka Producer Started with Validation & DLQ Support")

while True:
    event = generate_event()
    try:
        validate_telemetry(event)
        producer.send(TOPIC, event)
        print("Sent:", event)
    except Exception as err:
        dlq_payload = {"corrupted_event": event, "error": str(err)}
        producer.send(DLQ_TOPIC, dlq_payload)
        print("Routed to DLQ:", dlq_payload)

    producer.flush()
    time.sleep(2)