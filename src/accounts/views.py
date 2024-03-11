from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from bookings.serializers import BookingSerializer
from . import serializers,models

class AccountViewSet(GenericViewSet,
                     RetrieveModelMixin):

    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    lookup_field = "account_id"

    def get_permissions(self):
        if self.action in ["create"]:
            self.permission_classes = []
        return super().get_permissions()

    
    @extend_schema(
        request=serializers.CreateAccountSerializer,
        responses={"201":""},
        summary="Create Account",
        auth=[]
    )
    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = User.objects.create_user(data["email"],password=data["password"])

        account = models.Account.objects.create(user=user,
                                                first_name=data["first_name"],
                                                last_name=data["last_name"])
        
        return Response(status=status.HTTP_201_CREATED)
    
    
    @extend_schema(
        request=serializers.RetrieveTokenSerializer,
        responses=serializers.TokenResponseSerializer,
        summary="Retrieve token",
        auth=[]
    )
    @action(["POST"], detail=False, permission_classes=[], url_path="token")
    def token(self, request, *args, **kwargs):
        serializer = serializers.RetrieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = authenticate(username=data["email"],password=data["password"])

        if not user:
            raise ValidationError("Invalid email/password", "invalid_email_or_password")
        
        account = user.account

        token = RefreshToken.for_user(user)
        token["account_id"] = str(account.account_id)

        data = {
            "refresh": str(token),
            "access": str(token.access_token)
        }

        serializer = serializers.TokenResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return Response(data,status=status.HTTP_200_OK)
    

    @extend_schema(
        request=serializers.RefreshTokenSerializer,
        responses=serializers.TokenResponseSerializer,
        summary="Refresh token",
        auth=[]
    )
    @action(["POST"], detail=False, permission_classes=[], url_path="token/refresh")
    def refresh(self, request, *args, **kwargs):
        serializer = serializers.RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            token = RefreshToken(data["refresh"])
        except Exception:
            raise ValidationError("Invalid refresh token", "invalid_refresh_token")

        token.set_exp()

        data = {
            "refresh": str(token),
            "access": str(token.access_token)
        }

        serializer = serializers.TokenResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return Response(data,status=status.HTTP_200_OK)
        
    
    @extend_schema(
        responses=serializers.AccountSerializer,
        summary="Retrieve Account Details"
    )
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        self.queryset = models.Account.objects.filter(user=user)
        return super().retrieve(request, *args, **kwargs)


    @extend_schema(
        responses=BookingSerializer,
        summary="Retrieve Account Bookings"
    )
    @action(["GET"], detail=True, url_name="bookings-list",url_path="bookings")
    def list_bookings(self, request, *args, **kwargs):
        user = request.user
        self.queryset = models.Account.objects.filter(user=user)
        account = self.get_object()

        serializer = BookingSerializer(account.bookings, many=True)

        return Response(serializer.data)


    

    





