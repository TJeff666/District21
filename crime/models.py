from django.db import models

class CrimeEvent(models.Model):
    crime_id = models.CharField(max_length=100, unique=True)
    primary_type = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_description = models.CharField(max_length=255, null=True, blank=True)
    block = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.primary_type} at {self.block}"
