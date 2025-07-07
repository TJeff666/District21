from django.urls import path
from . import views

urlpatterns = [
    path('', views.crime_map_view, name='crime_map'),
    path('api/crimes/', views.crime_data_api, name='crime_data_api'),
    path('api/hotspots/', views.top_hotspots_api, name='top_hotspots_api'),
]
