from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Count
from .models import CrimeEvent

def crime_data_api(request):
    crimes = CrimeEvent.objects.filter(latitude__isnull=False, longitude__isnull=False).order_by('-date')[:500]
    data = [
        {
            'latitude': c.latitude,
            'longitude': c.longitude,
            'primary_type': c.primary_type,
            'block': c.block,
            'city': c.city,
        }
        for c in crimes
    ]
    return JsonResponse(data, safe=False)

def crime_map_view(request):
    return render(request, 'crime/map.html')

def top_hotspots_api(request):
    top_blocks = (
        CrimeEvent.objects
        .filter(latitude__isnull=False, longitude__isnull=False)
        .values('block', 'city')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )

    hotspot_data = []

    for block in top_blocks:
        crime_with_coords = (
            CrimeEvent.objects
            .filter(block=block['block'], city=block['city'])
            .values('latitude', 'longitude')
            .annotate(count=Count('id'))
            .order_by('-count')
            .first()
        )

        if crime_with_coords:
            hotspot_data.append({
                'block': block['block'],
                'total': block['total'],
                'latitude': crime_with_coords['latitude'],
                'longitude': crime_with_coords['longitude'],
                'city': block['city']
            })

    return JsonResponse(hotspot_data, safe=False)
