import os
import sys
import django
import json
from kafka import KafkaConsumer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "district21_backend.settings")
django.setup()

from crime.models import CrimeEvent

consumer = KafkaConsumer(
    'crime-events',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    data = message.value
    print("📦 Incoming Kafka data:", data)

    crime_id = data.get('crime_id') or data.get('id') or data.get('case_number') or data.get('incident_id')
    print("🧾 Using crime_id:", crime_id)

    if not crime_id:
        print("⚠️ Skipping record — no crime_id found:", data)
        continue

    try:
        if not CrimeEvent.objects.filter(crime_id=crime_id).exists():
            CrimeEvent.objects.create(
                crime_id=crime_id,
                primary_type=data.get('primary_type'),
                description=data.get('description'),
                date=data.get('date'),
                latitude=float(data['latitude']) if data.get('latitude') else None,
                longitude=float(data['longitude']) if data.get('longitude') else None,
                location_description=data.get('location_description'),
                block=data.get('block'),
                city=data.get('city', 'Unknown')
            )
            print(f"🟢 Saved: {data.get('primary_type')} at {data.get('block')} in {data.get('city', 'Unknown')}")
    except Exception as e:
        print("❌ Error saving crime event:", e)
