import wagtail.images.utils

from .find_duplicates import find_image_duplicates

# Monkey patch duplicate images finder utility from wagtail.images.
wagtail.images.utils.find_image_duplicates = find_image_duplicates
