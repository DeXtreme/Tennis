import graphene
from graphene_django import DjangoObjectType

from courts.models import Court

from utils.query_response import QueryResponse
from utils.pagination import PaginatedModelList

class CourtType(DjangoObjectType):

    class Meta:
        model = Court
        exclude = ["bookings"]


class CourtOutput(QueryResponse):
    data = graphene.Field(CourtType)

class CourtListOutput(PaginatedModelList):
    data = graphene.List(CourtType)