import uuid
from django.db import models


from accounts.models import Account
from courts.models import Court

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
        return f"<Booking:{self.booking_id} | {self.start_time} | {self.duration} hours>"