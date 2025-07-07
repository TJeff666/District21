from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Count
from .models import CrimeEvent

def crime_data_api(request):
    crimes = CrimeEvent.objects.order_by('-date')[:100]
    data = [
        {
            'latitude': c.latitude,
            'longitude': c.longitude,
            'primary_type': c.primary_type,
            'block': c.block,
        }
        for c in crimes if c.latitude and c.longitude
    ]
    return JsonResponse(data, safe=False)
def crime_map_view(request):
    return render(request, 'crime/map.html')


def top_hotspots_api(request):
    # Get top 5 crime blocks
    top_blocks = (
        CrimeEvent.objects
        .values('block')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    hotspot_data = []

    for block in top_blocks:
        # Get the most common coordinates used for this block
        crime_with_coords = (
            CrimeEvent.objects
            .filter(block=block['block'], latitude__isnull=False, longitude__isnull=False)
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
            })

    return JsonResponse(hotspot_data, safe=False)