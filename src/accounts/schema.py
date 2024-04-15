import graphene
import graphql_jwt
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoFormMutation
from graphql_jwt.decorators import login_required
import graphql_jwt.middleware

from .models import Account
from .forms import RegisterForm

class AccountType(DjangoObjectType):
    """
    User account type
    """
    email = graphene.String(required=True)
    # bookings = graphene.Field()

    def resolve_email(self, info):
        return self.user.username
    
    class Meta:
        model = Account
        fields = ["account_id","first_name","last_name","email"]


class RegisterMutation(DjangoFormMutation):
    class Meta:
        form_class = RegisterForm
    
    success = graphene.Boolean(default_value=False)

    @classmethod
    def perform_mutate(cls, form, info):
        data=form.cleaned_data
        user = User.objects.create_user(data["email"], 
                                        password=data["password"])

        account = Account.objects.create(user=user,
                                         first_name=data["first_name"],
                                         last_name=data["last_name"])


        return cls(errors=None, success=True, **data)
    

class Query(graphene.ObjectType):
    me = graphene.Field(AccountType,
                        description="Get account details")

    @login_required
    def resolve_me(root, info):
        return info.context.user.account


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()

    register = RegisterMutation.Field(description="Create new account")