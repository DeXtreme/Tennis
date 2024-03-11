from rest_framework import serializers

from bookings.serializers import BookedSerializer
from .models import Court

class CourtListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ["court_id", "name", "location"]



class CourtSerializer(serializers.ModelSerializer):
    booked = BookedSerializer(source="bookings", many=True)
    class Meta:
        model = Court
        fields = ["court_id", "name", "location", "open", "close", "booked"]