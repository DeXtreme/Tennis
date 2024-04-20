import graphene
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from graphql_jwt.decorators import login_required

from accounts.models import Account
from bookings.models import Booking
from courts.models import Court

from bookings.api.schema import BookingType, CreateBookingInput

from utils.common_mutations import Create
from utils.common import ExceptionHandlers
from utils.logging import logger

class Base:
    model = Booking

    foreign_key_fields = [("account", Account),("court", Court)]

    data = graphene.Field(BookingType)

class CreateBookingMutation(Base, Create):

    class Arguments:
        payload = CreateBookingInput(required=True)

    @classmethod
    @login_required
    @ExceptionHandlers.mutation()
    def mutate(cls, root, info, id=None, payload=None):
        payload["account"] = info.context.user.account.id
        court_id = payload["court"]
        start_time = payload["start_time"]
        start_time = start_time.replace(tzinfo=timezone.utc)
        duration = payload["duration"]
        end_time = start_time + datetime.timedelta(hours=duration)

        court = Court.objects.get(id=court_id)

        if start_time < timezone.now() or (start_time.time() <= court.open or end_time.time() >= court.close):
            raise ValidationError("Invalid start time or duration")
        
        booked = court.bookings.filter(
            (Q(start_time__lte=start_time)&Q(end_time__gt=start_time))
            |(Q(start_time__lte=end_time)&Q(end_time__gt=end_time))
        )
        
        if booked:
            raise ValidationError("Slot not available")

        payload["start_time"] = start_time
        payload["end_time"] = end_time
        return super().mutate(root, info, id, payload)
