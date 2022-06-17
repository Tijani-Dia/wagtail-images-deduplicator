from functools import lru_cache

import imagehash
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .hash_functions import HASH_FUNCTIONS


@lru_cache(maxsize=1)
def get_custom_hash_func():
    hash_func = getattr(settings, "WAGTAILIMAGESDEDUPLICATOR_HASH_FUNC", "phash")

    if hash_func not in HASH_FUNCTIONS:
        raise ImproperlyConfigured(
            f"Unrecognized hash function: {hash_func}.\n"
            f"Hash function must be one of {HASH_FUNCTIONS}."
        )

    return getattr(imagehash, hash_func)


@lru_cache(maxsize=1)
def get_max_distance_thresold():
    max_distance_thresold = getattr(
        settings, "WAGTAILIMAGESDEDUPLICATOR_MAX_DISTANCE_THRESOLD", 5
    )
    try:
        return int(max_distance_thresold)
    except (TypeError, ValueError):
        raise ImproperlyConfigured(
            "The 'WAGTAILIMAGESDEDUPLICATOR_MAX_DISTANCE_THRESOLD' setting value must be a number."
        )


@lru_cache(maxsize=1024)
def get_imagehash_instance(image_hash):
    return imagehash.hex_to_hash(image_hash)
