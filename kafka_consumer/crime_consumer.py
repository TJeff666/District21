import os
import sys
import django
import json
from kafka import KafkaConsumer

# Step 1: Add Django project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Step 2: Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "district21_backend.settings")

# Step 3: Setup Django
django.setup()

# Step 4: Import your model
from crime.models import CrimeEvent

# Step 5: Setup Kafka consumer
consumer = KafkaConsumer(
    'crime-events',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Step 6: Consume messages and save to DB
for message in consumer:
    data = message.value
    try:
        if not CrimeEvent.objects.filter(crime_id=data.get('id')).exists():
            CrimeEvent.objects.create(
                crime_id=data.get('id'),
                primary_type=data.get('primary_type'),
                description=data.get('description'),
                date=data.get('date'),
                latitude=float(data['latitude']) if data.get('latitude') else None,
                longitude=float(data['longitude']) if data.get('longitude') else None,
                location_description=data.get('location_description'),
                block=data.get('block')
            )
            print(f"🟢 Saved: {data.get('primary_type')} at {data.get('block')}")
    except Exception as e:
        print("❌ Error saving crime event:", e)
