import graphene

from .account import AccountQuery

class Query(AccountQuery, graphene.ObjectType):
    ...