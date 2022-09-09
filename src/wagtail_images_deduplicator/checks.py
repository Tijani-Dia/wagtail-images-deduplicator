import typing

from django.apps import AppConfig
from django.core.checks import Warning
from wagtail.images import get_image_model


def check_image_model(app_configs: typing.Dict[str, AppConfig], **kwargs: typing.Any):
    from .models import DuplicateFindingMixin

    warnings: typing.List[Warning] = []
    ImageModel = get_image_model()
    if not issubclass(ImageModel, DuplicateFindingMixin):
        warnings.append(
            Warning(
                "Finding image duplicates with wagtail-images-deduplicator is not available.",
                hint=(
                    "Ensure that your image model inherits from "
                    "wagtail_images_deduplicator.models.DuplicateFindingMixin."
                ),
                obj=ImageModel,
                id="wagtail_images_deduplicator.W001",
            )
        )
    return warnings
