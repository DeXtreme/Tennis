from traceback import print_exc
from datetime import timedelta
from asgiref.sync import async_to_sync
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from channels.generic.websocket import JsonWebsocketConsumer
from . import models,serializers


class BookingsConsumer(JsonWebsocketConsumer):

    def connect(self):
        self.subs = []
        self.accept()

    
    def disconnect(self, code):
        for sub in self.subs:
            async_to_sync(self.channel_layer.group_discard)(
                sub, self.channel_name
            )

    def receive_json(self, content, **kwargs):
        try:
            serializer = serializers.ConsumerTypeSerializer(data=content)
            serializer.is_valid(raise_exception=True)

            type = serializer.validated_data["type"]

            if type == "sub":
                response = self.subscribe(content)
            elif type == "unsub":
                response = self.unsubscribe(content)
            elif type == "book":
                response = self.book(content)
            elif type == "cancel":
                response = self.cancel(content)

        except ValidationError as e:
            response = {
                "status": "error",
                "details": e.get_full_details()
            }
            self.send_json(response)
        except Exception as e:
            print_exc()
            response = {
                "status": "error",
                "details": str(e)
            }
            self.send_json(response)
            
    

    def subscribe(self,content):
        serializer = serializers.ConsumerSubSerializer(data=content)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        court_id = data["court_id"]
        sub = f"court_{court_id}"

        async_to_sync(self.channel_layer.group_add)(
            sub, self.channel_name
        )

        self.subs.append(sub)

        self.send_json({"status": "success"})


    def unsubscribe(self,content):
        serializer = serializers.ConsumerSubSerializer(data=content)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        court_id = data["court_id"]
        sub = f"court_{court_id}"

        async_to_sync(self.channel_layer.group_discard)(
            sub, self.channel_name
        )

        if sub in self.subs:
            self.subs.remove(sub)

        self.send_json({"status": "success"})


    def book(self,content):
        serializer = serializers.ConsumerBookSerializer(data=content)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        
        court_id = data["court_id"]
        start_time = data["start_time"]
        duration = data["duration"]
        end_time = start_time + timedelta(hours=duration)
        
        court = models.Court.objects.get(court_id=court_id)

        if start_time < timezone.now() or (start_time.time() <= court.open or end_time.time() >= court.close):
            raise Exception("Invalid start time or duration")
        
        booked = court.bookings.filter(
            (Q(start_time__lte=start_time)&Q(end_time__gt=start_time))
            |(Q(start_time__lte=end_time)&Q(end_time__gt=end_time))
        )
        

        if booked:
            raise Exception("Slot not available")
        
        user = self.scope["user"]
        account = user.account
        booking = models.Booking.objects.create(court=court,
                                                account=account,
                                                start_time=start_time,
                                                end_time=end_time,
                                                duration=duration)

        self.send_json({"status": "success"})

        
    def cancel(self,content):
        serializer = serializers.ConsumerCancelSerializer(data=content)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        
        booking_id = data["booking_id"]
        
        user = self.scope["user"]
        account = user.account
        booking = models.Booking.objects.get(booking_id=booking_id,
                                             account=account)
        
        court_id = booking.court.court_id
        
        booking.delete()
        

        self.send_json({"status": "success"})

        

    def event(self,event):
        message = event["body"]
        self.send_json(message)