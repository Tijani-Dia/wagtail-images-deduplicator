from shutil import rmtree

from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.images.permissions import permission_policy

from tests.models import CustomImage
from tests.utils import get_test_images_files
from wagtail_images_deduplicator.find_duplicates import find_image_duplicates


class TestFindDuplicates(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("admin")
        self.images = []
        for num, _file in enumerate(get_test_images_files()):
            image = CustomImage.objects.create(title=f"Image {num + 1}", file=_file)
            self.images.append(image)

    def tearDown(self):
        CustomImage.objects.all().delete()
        rmtree("original_images")

    def find_duplicates(self, image):
        return (
            find_image_duplicates(image, self.user, permission_policy)
            .order_by("pk")
            .values_list("pk", flat=True)
        )

    def test_find_image_duplicates(self):
        duplicates = {
            1: [2],
            2: [1, 3],
            3: [2, 4, 5],
            4: [3, 5],
            5: [3, 4],
        }

        for i, duplicates_expected in duplicates.items():
            with self.subTest(i=i):
                duplicates_found = self.find_duplicates(self.images[i - 1])
                self.assertQuerysetEqual(duplicates_found, duplicates_expected)
