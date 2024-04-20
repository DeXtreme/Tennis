import graphene
from .equipment import EquipmentQuery

class Query(EquipmentQuery, graphene.ObjectType):
    ...