from contextlib import contextmanager

import PIL
from django.db import models

from .utils import get_custom_hash_func, get_imagehash_instance


class DuplicateFindingMixin(models.Model):
    custom_hash = models.CharField(
        max_length=40, blank=True, editable=False, db_index=True
    )

    def _set_custom_hash(self):
        hash_func = get_custom_hash_func()
        # Hash functions from the imagehash library work with PIL.Image instances.
        with self.get_pil_image() as pil_image:
            hash_value = hash_func(pil_image)
            # hash_value is an instance of imagehash.ImageHash. We save the string representation.
            # This will also allow us to load the class instance back in order to make comparisons.
            self.custom_hash = str(hash_value)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields", [])
        update_file = not bool(update_fields) or ("file" in update_fields)
        update_custom_hash = not bool(update_fields) or (
            update_file or "custom_hash" in update_fields
        )
        if update_custom_hash:
            self._set_custom_hash()

        return super().save(*args, **kwargs)

    @property
    def hash_instance(self):
        """Returns an instance of imagehash.ImageHash that has special comparison methods."""

        return get_imagehash_instance(self.custom_hash)

    @contextmanager
    def get_pil_image(self):
        with self.open_file() as image_file:
            yield PIL.Image.open(image_file)

    class Meta:
        abstract = True
