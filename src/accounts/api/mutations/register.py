import graphene

from accounts.models.account import Account
from accounts.models.user import User

from accounts.api.schema.account import AccountType
from accounts.api.schema.register import RegisterInput

from utils.query_response import QueryResponse
from utils.model_helpers import retrieve_object_by_id

from utils.logging import logger

class RegisterMutation(graphene.Mutation, QueryResponse):
    
    data = graphene.Field(AccountType)
    
    class Arguments:
        payload = RegisterInput(required=True)

    @classmethod
    def mutate(cls, root, info, payload):
        user = User.objects.create_user(email=payload["email"], 
                                        password=payload["password"])

        account = Account.objects.create(user=user,
                                         first_name=payload["first_name"],
                                         last_name=payload["last_name"])


        return cls.success(data=account)