from rest_framework import serializers

from .models import Court,Booking

class CourtListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ["court_id", "name", "location"]


class BookedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["start_time", "end_time"]


class CourtSerializer(serializers.ModelSerializer):
    booked = BookedSerializer(source="bookings", many=True)
    class Meta:
        model = Court
        fields = ["court_id", "name", "location", "open", "close", "booked"]