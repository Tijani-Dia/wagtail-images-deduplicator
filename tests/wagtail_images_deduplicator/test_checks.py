from unittest import mock

from django.core import checks
from django.test import TestCase


class TestChecks(TestCase):
    def test_check_image_model(self):
        class Image:
            pass

        image_model_warning = checks.Warning(
            "Finding image duplicates with wagtail-images-deduplicator is not available.",
            hint=(
                "Ensure that your image model inherits from "
                "wagtail_images_deduplicator.models.DuplicateFindingMixin."
            ),
            obj=Image,
            id="wagtail_images_deduplicator.W001",
        )

        with mock.patch(
            "wagtail_images_deduplicator.checks.get_image_model", return_value=Image
        ):
            checks_result = checks.run_checks(tags=[checks.Tags.models])

            # Only look at warnings for Image
            warning = [warning for warning in checks_result if warning.obj == Image]

            self.assertEqual(warning, [image_model_warning])
