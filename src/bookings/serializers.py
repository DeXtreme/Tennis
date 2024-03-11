from rest_framework import serializers

from . import models


class BookedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Booking
        fields = ["start_time", "end_time"]


class CancelledSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Booking
        fields = ["start_time", "end_time"]


class BookingSerializer(serializers.ModelSerializer):
    court_name = serializers.CharField(source="court.name")
    class Meta:
        model = models.Booking
        fields = ["booking_id","court_name","start_time","duration","created_at"]


class ConsumerTypeSerializer(serializers.Serializer):
    type_choices = [("sub","Subscribe"),
                    ("unsub","Unsubscribe"),
                    ("book","Book"),
                    ("cancel","Cancel")]

    type = serializers.ChoiceField(type_choices)



class ConsumerSubSerializer(serializers.Serializer):
    court_id = serializers.UUIDField()


class ConsumerBookSerializer(serializers.Serializer):
    court_id = serializers.UUIDField()
    start_time = serializers.DateTimeField()
    duration = serializers.IntegerField()

class ConsumerCancelSerializer(serializers.Serializer):
    booking_id = serializers.UUIDField()