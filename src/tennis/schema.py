import graphene
import accounts.schema

class Query(accounts.schema.Query, graphene.ObjectType):
    ...

class Mutation(accounts.schema.Mutation, graphene.ObjectType):
    ...

schema = graphene.Schema(query=Query,mutation=Mutation)