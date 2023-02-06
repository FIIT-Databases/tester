import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.deconstruct import deconstructible


class BaseModel(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update(self, data: dict):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()


@deconstructible
class PrivateFileStorage(FileSystemStorage):
    def __init__(self):
        super(PrivateFileStorage, self).__init__(location=settings.PRIVATE_DIR)

    def __eq__(self, other):
        return self.subdir == other.subdir


private_storage = PrivateFileStorage()
