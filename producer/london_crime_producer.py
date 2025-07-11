# london_crime_producer.py

import requests, time, json
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Retrieves latest crimes within a central London bounding box
URL = ("https://data.police.uk/api/crimes-street/all-crime?"
       "poly=51.515,-0.1:51.52,-0.1:51.52,0.0:51.515,0.0")

def fetch_latest_crimes():
    try:
        resp = requests.get(URL)
        if resp.status_code == 200:
            for record in resp.json():
                dt_str = record.get("month") + "-01T00:00:00"
                crime = {
                    "crime_id": str(record['id']),
                    "primary_type": record.get("category"),
                    "description": record.get("street", {}).get("name", ""),
                    "date": dt_str,
                    "latitude": float(record['location']['latitude']),
                    "longitude": float(record['location']['longitude']),
                    "location_description": record['location']['street']['name'],
                    "block": record['location']['street']['name'],
                    "city": "London"
                }
                producer.send("crime-events", crime)
                print(f"🇬🇧 Sent: {crime['primary_type']} at {crime['block']}")
        else:
            print("❌ London fetch failed:", resp.status_code)
    except Exception as e:
        print("❌ London error:", e)

while True:
    fetch_latest_crimes()
    time.sleep(10)
