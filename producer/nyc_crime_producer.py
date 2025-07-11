import requests
import time
import json
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

NYC_API_URL = "https://data.cityofnewyork.us/resource/9s4h-37hy.json?$limit=10&$order=cmplnt_fr_dt DESC"

def safe_parse_date(record):
    date_str = record.get("cmplnt_fr_dt")
    try:
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%d").isoformat()
    except:
        pass
    # Fallback to current time
    return datetime.now().isoformat()

def is_valid_latlon(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        return 30 <= lat <= 50 and -90 <= lon <= -60
    except:
        return False

def fetch_latest_crimes():
    try:
        response = requests.get(NYC_API_URL)
        if response.status_code == 200:
            data = response.json()
            for record in data:
                lat = record.get("latitude")
                lon = record.get("longitude")

                if not is_valid_latlon(lat, lon):
                    print("⚠️ Skipped invalid lat/lon:", lat, lon)
                    continue

                crime = {
                    "crime_id": record.get("cmplnt_num"),
                    "primary_type": record.get("ofns_desc"),
                    "description": record.get("pd_desc"),
                    "date": safe_parse_date(record),
                    "latitude": float(lat),
                    "longitude": float(lon),
                    "location_description": record.get("prem_typ_desc"),
                    "block": str(record.get("addr_pct_cd")),
                    "city": "NYC"
                }

                producer.send("crime-events", crime)
                print(f"🗽 Sent: {crime['primary_type']} at block {crime['block']}")
        else:
            print("❌ Failed to fetch NYC data:", response.status_code)
    except Exception as e:
        print("❌ Error:", e)

while True:
    fetch_latest_crimes()
    time.sleep(10)
