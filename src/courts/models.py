import uuid
from django.db import models

from accounts.models import Account

class Court(models.Model):
    """ Court model """

    court_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    open = models.TimeField()
    close = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Court:{self.court_id} | {self.name}"


class Booking(models.Model):
    """ Booking model """

    booking_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name="bookings")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"<Booking:{self.booking_id}"

