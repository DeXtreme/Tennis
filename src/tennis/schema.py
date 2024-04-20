import graphene

import accounts.api.queries
import accounts.api.mutations
import bookings.api.queries
import bookings.api.mutations
import courts.api.queries
import equipment.api.queries

accounts.api.queries
class Query(accounts.api.queries.Query,
            courts.api.queries.Query,
            bookings.api.queries.Query,
            equipment.api.queries.Query,
            graphene.ObjectType):
    ...

class Mutation(accounts.api.mutations.Mutation,
               bookings.api.mutations.Mutation,
               graphene.ObjectType):
    ...

schema = graphene.Schema(query=Query,mutation=Mutation)