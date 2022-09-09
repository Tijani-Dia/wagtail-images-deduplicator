import typing

from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet
from wagtail.images.models import AbstractImage

T = typing.TypeVar("T", bound=AbstractImage)

class BasePermissionPolicy:
    def instances_user_has_permission_for(
        self, user: AbstractUser, action: str
    ) -> QuerySet[T]: ...
