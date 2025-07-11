import requests
import time
import json
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

URL = "https://data.sfgov.org/resource/wg3w-h783.json?$limit=10&$order=incident_datetime DESC"

def parse_datetime(dt_str):
    try:
        return datetime.fromisoformat(dt_str).isoformat()
    except:
        return datetime.now().isoformat()

def is_valid_latlon(lat, lon):
    try:
        return 37 <= float(lat) <= 38 and -123 <= float(lon) <= -121
    except:
        return False

def fetch_latest_crimes():
    resp = requests.get(URL)
    if resp.status_code != 200:
        print("❌ SF fetch failed:", resp.status_code)
        return

    for record in resp.json():
        lat = record.get("latitude")
        lon = record.get("longitude")
        dt = record.get("incident_datetime")

        if not (lat and lon and is_valid_latlon(lat, lon)):
            print("⚠️ Skipped bad SF coords:", lat, lon)
            continue

        crime = {
            "crime_id": record.get("incident_id") or record.get("row_id"),
            "primary_type": record.get("incident_category"),
            "description": record.get("incident_description"),
            "date": parse_datetime(dt),
            "latitude": float(lat),
            "longitude": float(lon),
            "location_description": record.get("intersection"),
            "block": record.get("intersection"),
            "city": "SF"
        }

        producer.send("crime-events", crime)
        print(f"🌉 Sent: {crime['primary_type']} at {crime['block']}")

while True:
    fetch_latest_crimes()
    time.sleep(10)
