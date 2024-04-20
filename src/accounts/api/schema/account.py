import graphene
from graphene_django import DjangoObjectType

from accounts.models import Account

from utils.query_response import QueryResponse

class AccountType(DjangoObjectType):
    """
    User account type
    """
    email = graphene.String(required=True, source="email")
    #bookings = graphene.List(BookingType)
    
    class Meta:
        model = Account
        fields = ["account_id","first_name","last_name","email"]


class AccountOutput(QueryResponse):
    data = graphene.Field(AccountType)


class UpdateAccountInput(graphene.InputObjectType):
    first_name = graphene.String()
    last_name = graphene.String()