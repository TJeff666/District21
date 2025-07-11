# toronto_crime_producer.py

import requests, time, json
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

URL = "https://services.arcgis.com/S9th0jAJ7bqgIRjw/arcgis/rest/services/Neighbourhood_Crime_Rates_Open_Data/FeatureServer/0/query?where=1=1&outFields=OFFENCE,REPORT_DATE,geometry&f=json"

def fetch():
    resp = requests.get(URL)
    if resp.status_code != 200:
        print("❌ Toronto fetch failed:", resp.status_code)
        return
    for feat in resp.json().get("features", []):
        attrs = feat.get("attributes", {})
        geom = feat.get("geometry", {})
        crime = {
            "crime_id": str(attrs.get("OBJECTID")),
            "primary_type": attrs.get("OFFENCE"),
            "description": None,
            "date": attrs.get("REPORT_DATE"),
            "latitude": geom.get("y"),
            "longitude": geom.get("x"),
            "location_description": attrs.get("Neighbourhood"),
            "block": attrs.get("Neighbourhood"),
            "city": "Toronto"
        }
        producer.send("crime-events", crime)
        print(f"🍁 Sent Toronto: {crime['primary_type']} in {crime['block']}")

while True:
    fetch()
    time.sleep(300)
