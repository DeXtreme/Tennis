import uuid
from django.db import models

class Court(models.Model):
    """ Court model """

    court_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    open = models.TimeField()
    close = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"<Court:{self.court_id} | {self.name}"


