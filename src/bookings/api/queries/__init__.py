import graphene
from .booking import BookingQuery

class Query(BookingQuery, graphene.ObjectType):
    ...

