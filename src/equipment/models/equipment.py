import uuid
from django.db import models

from accounts.models import Account

class Equipment(models.Model):

    equipment_id = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=50)
    users = models.ManyToManyField(Account, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<Equipment: {self.name}>"
