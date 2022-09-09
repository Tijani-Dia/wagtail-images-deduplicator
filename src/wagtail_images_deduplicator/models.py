import typing
from contextlib import contextmanager

from django.db import models
from PIL import Image
from wagtail.images.models import AbstractImage
from .utils import get_custom_hash_func, get_imagehash_instance

if typing.TYPE_CHECKING:
    from imagehash import ImageHash

    _BASE = AbstractImage
else:
    _BASE = object


class DuplicateFindingMixin(_BASE, models.Model):
    custom_hash: models.CharField[typing.Optional[str], str] = models.CharField(
        max_length=40, blank=True, editable=False, db_index=True
    )

    def _set_custom_hash(self) -> None:
        hash_func = get_custom_hash_func()
        # Hash functions from the imagehash library work with PIL.Image instances.
        with self.get_pil_image() as pil_image:
            hash_value = hash_func(pil_image)
            # hash_value is an instance of imagehash.ImageHash. We save the string representation.
            # This will also allow us to load the class instance back in order to make comparisons.
            self.custom_hash = str(hash_value)

    def save(self, *args: typing.Any, **kwargs: typing.Any):
        update_fields: typing.Iterable[str] = kwargs.get("update_fields", [])
        update_file = not bool(update_fields) or ("file" in update_fields)
        update_custom_hash = not bool(update_fields) or (
            update_file or "custom_hash" in update_fields
        )
        if update_custom_hash:
            self._set_custom_hash()

        return super().save(*args, **kwargs)

    @property
    def hash_instance(self) -> "ImageHash":
        """Returns an instance of imagehash.ImageHash that has special comparison methods."""

        custom_hash: str = self.custom_hash
        if not custom_hash:
            raise Exception("Image's custom hash isn't set.")

        return get_imagehash_instance(custom_hash)

    @contextmanager
    def get_pil_image(self):
        with self.open_file() as image_file:
            yield Image.open(image_file)

    class Meta:  # type: ignore
        abstract = True
