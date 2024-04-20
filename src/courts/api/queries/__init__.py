import graphene
from .courts import CourtQuery

class Query(CourtQuery,graphene.ObjectType):
    ...