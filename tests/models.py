from wagtail.images.models import Image

from wagtail_images_deduplicator.models import DuplicateFindingMixin


class CustomImage(DuplicateFindingMixin, Image):
    pass
