import requests
import time
from kafka import KafkaProducer
import json

# Kafka producer setup
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Chicago crime API endpoint (fetching latest records)
URL = "https://data.cityofchicago.org/resource/ijzp-q8t2.json?$limit=10&$order=date DESC"

def fetch_latest_crimes():
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            data = response.json()
            for record in data:
                producer.send('crime-events', record)
                print(f"🔴 Sent: {record.get('primary_type')} at {record.get('block')}")
        else:
            print("Failed to fetch data:", response.status_code)
    except Exception as e:
        print("Error:", e)

# Stream every 10 seconds
while True:
    fetch_latest_crimes()
    time.sleep(10)
