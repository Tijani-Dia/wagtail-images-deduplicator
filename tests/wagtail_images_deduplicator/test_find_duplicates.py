from shutil import rmtree

from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.images.permissions import permission_policy

from tests.models import CustomImage
from tests.utils import get_test_images_files
from wagtail_images_deduplicator.find_duplicates import find_image_duplicates
from wagtail_images_deduplicator.models import DuplicateFindingMixin


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

    def find_duplicates(self, image, first_only=False):
        duplicates = find_image_duplicates(
            image, self.user, permission_policy, first_only
        )
        if duplicates._result_cache is None:
            return duplicates.order_by("pk").values_list("pk", flat=True)
        return [duplicate.pk for duplicate in duplicates._result_cache]

    def duplicate_image(self, image, copy_file_hash=True, copy_custom_hash=True):
        """Duplicates an image and saves the copy in the database."""

        image.pk = None
        image.id = None
        image._state.adding = True
        if not copy_file_hash:
            image.file_hash = ""
        if not copy_custom_hash:
            image.custom_hash = ""

        super(DuplicateFindingMixin, image).save()

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
                with self.assertNumQueries(3):
                    self.assertQuerysetEqual(
                        self.find_duplicates(self.images[i - 1]), duplicates_expected
                    )

    def test_find_image_duplicates_first_only(self):
        duplicates = {
            1: [2],
            2: [1],
            3: [2],
            4: [3],
            5: [3],
        }

        for i, duplicates_expected in duplicates.items():
            with self.subTest(i=i):
                with self.assertNumQueries(3):
                    self.assertQuerysetEqual(
                        self.find_duplicates(self.images[i - 1], first_only=True),
                        duplicates_expected,
                    )

    def test_find_image_duplicates_without_hashes(self):
        images = CustomImage.objects.all()[:]
        for i in range(1, 6):
            with self.subTest(i=i):
                image = images[i - 1]
                self.duplicate_image(
                    image, copy_file_hash=False, copy_custom_hash=False
                )

                # Image has no file hash nor custom_hash, so no duplicates should be returned.
                # No queries performed as well.
                with self.assertNumQueries(0):
                    self.assertQuerysetEqual(self.find_duplicates(image), [])

    def test_find_image_duplicates_with_only_file_hash(self):
        images = CustomImage.objects.all()
        for image in images:
            # Set file hash
            with image.open_file() as f:
                image._set_file_hash(f.read())

            super(DuplicateFindingMixin, image).save(update_fields=["file_hash"])

        for i in range(1, 6):
            with self.subTest(i=i):
                image = images[i - 1]
                self.duplicate_image(image, copy_custom_hash=False)

                # Image has only file hash, only exact duplicates (by file hash) should be returned.
                with self.assertNumQueries(1):
                    self.assertQuerysetEqual(self.find_duplicates(image), [i])

    def test_find_image_duplicates_with_only_custom_hash(self):
        images = CustomImage.objects.all()[:]
        for i in range(1, 6):
            with self.subTest(i=i):
                image = images[i - 1]
                self.duplicate_image(image)

                # Image has only custom hash, only exact duplicates (by custom hash) should be returned.
                with self.assertNumQueries(1):
                    self.assertQuerysetEqual(self.find_duplicates(image), [i])

    def test_find_image_duplicates_with_hashes(self):
        images = CustomImage.objects.all()
        for image in images:
            with image.open_file() as f:
                image._set_file_hash(f.read())

            super(DuplicateFindingMixin, image).save(update_fields=["file_hash"])

        for i in range(1, 6):
            with self.subTest(i=i):
                duplicates = []
                image = images[i - 1]
                file_hash = image.file_hash

                # Duplicate the image twice.
                # One with the file hash removed and the other with the custom hash removed.
                self.duplicate_image(image, copy_file_hash=False)
                duplicates.append(image.pk)

                image.file_hash = file_hash
                self.duplicate_image(image, copy_custom_hash=False)
                duplicates.append(image.pk)

                original_image = CustomImage.objects.get(pk=i)
                # The original image has both a custom hash and a file hash,
                # exact duplicates (by custom hash or file hash) should be returned.
                # The 2 copies we made above should match as well.
                with self.assertNumQueries(1):
                    duplicates_found = self.find_duplicates(original_image)
                    self.assertQuerysetEqual(duplicates_found, duplicates)
