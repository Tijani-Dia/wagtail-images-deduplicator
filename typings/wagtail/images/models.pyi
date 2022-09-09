import typing
from contextlib import contextmanager

from django.db import models
from wagtail.models import CollectionMember
from wagtail.search import index

class ImageFileMixin:
    @contextmanager
    def open_file(self) -> typing.BinaryIO: ...

class AbstractImage(ImageFileMixin, CollectionMember, index.Indexed, models.Model):
    file_hash: typing.Optional[str]
