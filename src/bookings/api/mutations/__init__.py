import graphene
from .booking import *

class Mutation(graphene.ObjectType):
    create_booking = CreateBookingMutation.Field()