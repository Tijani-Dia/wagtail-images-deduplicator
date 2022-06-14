from io import BytesIO

import PIL.Image
from django.core.files.base import File


def get_test_images_files():
    """Produces 5 copies of the original image and rotate by 2 degrees after each iteration."""

    image = PIL.Image.open("tests/images/wagtail.jpg")
    for i in range(1, 6):
        image = image.rotate(2)
        f = BytesIO()
        image.save(f, "PNG")
        f.seek(0)
        yield File(f, name=f"image-{i}.png")
