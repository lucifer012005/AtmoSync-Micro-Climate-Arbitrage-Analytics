import json
import random
import time
from datetime import datetime, timezone

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


def generate_sensor_data():

    container_id = random.choice(CONTAINERS)
    commodity = random.choice(COMMODITIES)

    origin, destination = random.choice(ROUTES)

    temperature = round(random.uniform(4, 12), 2)
    humidity = round(random.uniform(60, 95), 2)
    vibration = round(random.uniform(0.1, 5.0), 2)

    # Occasionally generate abnormal conditions
    if random.random() < 0.15:
        temperature = round(random.uniform(13, 20), 2)

    if random.random() < 0.15:
        humidity = round(random.uniform(90, 100), 2)

    data = {
        "container_id": container_id,
        "commodity": commodity,
        "origin": origin,
        "destination": destination,
        "temperature_c": temperature,
        "humidity_pct": humidity,
        "vibration_g": vibration,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return data


if __name__ == "__main__":

    print("AtmoSync IoT Simulator Started")

    while True:

        sensor_data = generate_sensor_data()

        print(json.dumps(sensor_data, indent=2))

        time.sleep(2)

