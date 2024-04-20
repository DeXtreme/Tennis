import uuid
from django.db import models

from courts.models.court import Court

class Worker(models.Model):
    """ Worker models """

    worker_id = models.UUIDField(default=uuid.uuid4)
    name = models.CharField()
    email = models.EmailField()
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name="workers")


    def __str__(self):
        return f"<Worker: {self.worker_id} | {self.name}>"