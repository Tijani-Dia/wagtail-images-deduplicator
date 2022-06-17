import pytest
from django.core.exceptions import ImproperlyConfigured

from tests.utils import clear_function_cache_before_and_after_test
from wagtail_images_deduplicator.hash_functions import HASH_FUNCTIONS
from wagtail_images_deduplicator.utils import (
    get_custom_hash_func,
    get_max_distance_thresold,
)


@clear_function_cache_before_and_after_test(get_custom_hash_func)
def test_get_invalid_custom_hash_func(settings):
    settings.WAGTAILIMAGESDEDUPLICATOR_HASH_FUNC = "hash-me"
    expected_err = f"Unrecognized hash function: hash-me.\nHash function must be one of {HASH_FUNCTIONS}."

    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_custom_hash_func()


@clear_function_cache_before_and_after_test(get_max_distance_thresold)
def test_get_max_distance_thresold(settings):
    settings.WAGTAILIMAGESDEDUPLICATOR_MAX_DISTANCE_THRESOLD = "five"
    expected_err = "The 'WAGTAILIMAGESDEDUPLICATOR_MAX_DISTANCE_THRESOLD' setting value must be a number."

    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_max_distance_thresold()
