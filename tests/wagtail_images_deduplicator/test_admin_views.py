import json
from shutil import rmtree

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Collection, GroupCollectionPermission, get_root_collection_id


class TestDuplicateImageViews(TestCase):
    """
    These tests are copied from `wagtail.images.tests.test_admin_views` to ensure
    duplicates detection works as expected in the admin.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser("admin")

    def setUp(self):
        self.client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        get_image_model().objects.all().delete()
        rmtree("uploaded_images")

        return super().tearDownClass()

    def post_image(self, title="test title"):
        return self.client.post(
            reverse("wagtailimages:add_multiple"),
            {
                "title": title,
                "files[]": SimpleUploadedFile(
                    "test.png", get_test_image_file().file.getvalue()
                ),
            },
        )

    def upload_image(self, title="Test image", select_format=False):
        params = "?select_format=true" if select_format else ""
        return self.client.post(
            reverse("wagtailimages:chooser_upload") + params,
            {
                "image-chooser-upload-title": title,
                "image-chooser-upload-file": SimpleUploadedFile(
                    "test.png", get_test_image_file().file.getvalue()
                ),
            },
        )

    def test_add(self):
        response = self.post_image()
        response_json = json.loads(response.content.decode())

        self.assertFalse(response_json["duplicate"])

    def test_add_duplicate(self):
        # Post image then post duplicate
        self.post_image()
        response = self.post_image(title="test title duplicate")

        # Check response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateUsed(
            response, "wagtailimages/images/confirm_duplicate_upload.html"
        )

        # Check image
        self.assertEqual(response.context["image"].title, "test title duplicate")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertIn("form", response_json)
        self.assertIn("confirm_duplicate_upload", response_json)
        self.assertTrue(response_json["success"])
        self.assertTrue(response_json["duplicate"])

    def test_add_duplicate_choose_permission(self):
        # Create group with access to admin and add permission.
        bakers_group = Group.objects.create(name="Bakers")
        access_admin_perm = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
        bakers_group.permissions.add(access_admin_perm)

        # Create the "Bakery" Collection and grant "add" permission to the Bakers group.
        root = Collection.objects.get(id=get_root_collection_id())
        bakery_collection = root.add_child(instance=Collection(name="Bakery"))
        GroupCollectionPermission.objects.create(
            group=bakers_group,
            collection=bakery_collection,
            permission=Permission.objects.get(
                content_type__app_label="wagtailimages", codename="add_image"
            ),
        )

        # Post image
        self.post_image()

        # Remove privileges from user
        self.user.is_superuser = False
        self.user.groups.add(bakers_group)
        self.user.save()

        # Post duplicate
        response = self.post_image(title="test title duplicate")

        # Check response
        self.assertEqual(response.status_code, 200)

        # Check template used
        self.assertTemplateNotUsed(
            response, "wagtailimages/images/confirm_duplicate_upload.html"
        )

        # Check image
        self.assertEqual(response.context["image"].title, "test title duplicate")

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertTrue(response_json["success"])
        self.assertFalse(response_json["duplicate"])
        self.assertIn("form", response_json)
        self.assertNotIn("confirm_duplicate_upload", response_json)

    def test_upload_duplicate(self):
        # Upload image then upload duplicate
        self.upload_image()
        response = self.upload_image(title="Test duplicate image")

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "wagtailimages/chooser/confirm_duplicate_upload.html"
        )

        # Check context
        Image = get_image_model()
        new_image = Image.objects.get(title="Test duplicate image")
        existing_image = Image.objects.get(title="Test image")
        self.assertEqual(response.context["new_image"], new_image)
        self.assertEqual(response.context["existing_image"], existing_image)

        choose_new_image_action = reverse(
            "wagtailimages:image_chosen", args=(new_image.id,)
        )
        self.assertEqual(
            response.context["confirm_duplicate_upload_action"], choose_new_image_action
        )

        choose_existing_image_action = (
            reverse("wagtailimages:delete", args=(new_image.id,))
            + "?"
            + urlencode(
                {
                    "next": reverse(
                        "wagtailimages:image_chosen", args=(existing_image.id,)
                    )
                }
            )
        )
        self.assertEqual(
            response.context["cancel_duplicate_upload_action"],
            choose_existing_image_action,
        )

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "duplicate_found")

    def test_upload_duplicate_select_format(self):
        # Upload image then upload duplicate.
        self.upload_image()
        response = self.upload_image(title="Test duplicate image", select_format=True)

        # Check response
        self.assertEqual(response.status_code, 200)

        # Check context
        Image = get_image_model()
        new_image = Image.objects.get(title="Test duplicate image")
        existing_image = Image.objects.get(title="Test image")

        choose_new_image_action = reverse(
            "wagtailimages:chooser_select_format", args=(new_image.id,)
        )
        self.assertEqual(
            response.context["confirm_duplicate_upload_action"], choose_new_image_action
        )

        choose_existing_image_action = (
            reverse("wagtailimages:delete", args=(new_image.id,))
            + "?"
            + urlencode(
                {
                    "next": reverse(
                        "wagtailimages:chooser_select_format", args=(existing_image.id,)
                    )
                }
            )
        )
        self.assertEqual(
            response.context["cancel_duplicate_upload_action"],
            choose_existing_image_action,
        )

        # Check JSON
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json["step"], "duplicate_found")
