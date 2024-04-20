import graphene
from graphene_django import DjangoObjectType

from equipment.models import Equipment

from utils.query_response import QueryResponse
from utils.pagination import PaginatedModelList

class EquipmentType(DjangoObjectType):

    class Meta:
        model = Equipment
        exclude = ["users"]


class EquipmentOutput(QueryResponse):
    data = graphene.Field(EquipmentType)

class EquipmentListOutput(PaginatedModelList):
    data = graphene.List(EquipmentType)

class UseEquipmentInput(graphene.InputObjectType):
    id = graphene.Int(required=True)