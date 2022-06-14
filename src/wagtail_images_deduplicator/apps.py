from django.apps import AppConfig
from django.core.checks import Tags, register


class WagtailImagesDeduplicatorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wagtail_images_deduplicator"

    def ready(self):
        from .checks import check_image_model

        register(check_image_model, Tags.models)
