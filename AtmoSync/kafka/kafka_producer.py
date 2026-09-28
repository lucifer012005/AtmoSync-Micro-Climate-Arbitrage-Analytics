import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

KAFKA_SERVER = "localhost:9092"
TOPIC = "iot_telemetry"

CONTAINERS = [
    "CONT-A001",
    "CONT-A002",
    "CONT-A003",
    "CONT-A004",
    "CONT-A005"
]

COMMODITIES = [
    "Avocado",
    "Mango",
    "Banana",
    "Tomato"
]

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


print("AtmoSync Kafka Producer Started")

while True:
    event = generate_event()

    producer.send(TOPIC, event)
    producer.flush()

    print("Sent:", event)

    time.sleep(2)
    