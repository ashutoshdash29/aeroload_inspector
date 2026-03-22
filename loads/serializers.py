from rest_framework import serializers
from .models import Aircraft

class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = ['name', 'registration', 'aircraft_type', 'max_takeoff_weight']
        