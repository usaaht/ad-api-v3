from rest_framework import serializers
from .models import Ad, Location, DailyVisitor

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class DailyVisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyVisitor
        fields = '__all__'

class AdSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)
    daily_visitors = DailyVisitorSerializer(many=True, read_only=True)

    class Meta:
        model = Ad
        fields = '__all__'

    def create(self, validated_data):
        locations_data = validated_data.pop('locations', []) 
        ad = Ad.objects.create(**validated_data)

        for location_data in locations_data:
            Location.objects.create(ad=ad, **location_data)

        return ad

class DailyVisitorReportSerializer(serializers.Serializer):
    location_name = serializers.CharField(source='location.name')
    date = serializers.DateField()
    visitor_count = serializers.IntegerField(source='count')
