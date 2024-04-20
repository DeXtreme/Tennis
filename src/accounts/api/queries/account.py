import graphene
from graphql_jwt.decorators import login_required

from accounts.models.account import Account
from accounts.api.schema.account import AccountOutput
from utils.model_helpers import retrieve_object_by_id

class AccountQuery(graphene.ObjectType):
    me = graphene.Field(AccountOutput,
                        description="Get account details")

    @login_required
    def resolve_me(root, info):
        account = retrieve_object_by_id(model=Account,id=info.context.user.account.id)
        return AccountOutput.response(**account)
