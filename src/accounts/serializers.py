import re
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.username")
    class Meta:
        model = Account
        exclude = ["user","created_at","updated_at"]


class CreateAccountSerializer(serializers.Serializer):
    class PasswordField(serializers.CharField):
        default_error_messages = {
            "too_short": "The password must be a minimum of 8 characters long",
            "no_uppercase": "The password must contain at least one uppercase character",
            "no_number": "The password must contain at least one number"}

        def run_validation(self, data=...):
            data = super().run_validation(data)
            if data:
                if not len(data) >= 8:
                    self.fail("too_short")
                elif not re.search(r"[A-Z]", data):
                    self.fail("no_uppercase")
                elif not re.search(r"[0-9]", data):
                    self.fail("no_number")

    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = PasswordField()
    

class RetrieveTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


