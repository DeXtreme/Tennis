import graphene
from graphql_jwt.decorators import login_required
from accounts.models.account import Account

from accounts.api.schema.account import UpdateAccountInput,AccountType
from accounts.permissions import is_account_active
from utils.common_mutations import Update
from utils.common import ExceptionHandlers

class Base:
    model = Account
    permissions = [is_account_active]
    data = graphene.Field(AccountType)

class UpdateAccount(Base, Update):

    class Arguments:
        payload = UpdateAccountInput(required=True)

    @classmethod
    @login_required
    @ExceptionHandlers.mutation(Base.model.__name__)
    def mutate(cls, root, info, id=None, payload=None):
        id = info.context.user.account.id
        return super().mutate(root, info, id, payload, token=None)
   
