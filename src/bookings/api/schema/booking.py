import graphene
from  graphene_django import DjangoObjectType

from bookings.models import Booking

from courts.api.schema import CourtType

from utils.query_response import QueryResponse
from utils.pagination import PaginatedModelList

class BookingType(DjangoObjectType):
    #account = graphene.Field(AccountType)
    court = graphene.Field(CourtType)

    class Meta:
        model = Booking
        fields = "__all__"


class BookingOutput(QueryResponse):
    data = graphene.Field(BookingType)


class BookingListOutput(PaginatedModelList):
    data = graphene.List(BookingType)


class CreateBookingInput(graphene.InputObjectType):
    court = graphene.Int(required=True)
    start_time = graphene.DateTime(required=True)
    duration = graphene.Int(required=True)