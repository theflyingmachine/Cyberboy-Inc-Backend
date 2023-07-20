import uuid
from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    id: str = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
