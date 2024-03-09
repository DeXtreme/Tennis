import uuid
from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    """ Account information model """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    account_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"<Account:{self.account_id} | {self.first_name} {self.last_name}>"
