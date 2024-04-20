import graphene
import graphql_jwt
from .register import RegisterMutation
from .account import UpdateAccount

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()

    register_account = RegisterMutation.Field()
    update_account = UpdateAccount.Field()