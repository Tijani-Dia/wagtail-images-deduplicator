from functools import wraps
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


class clear_function_cache_before_and_after_test:
    def __init__(self, cached_func):
        self.cached_func = cached_func

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.cached_func.cache_clear()
            exception = None

            try:
                func(*args, **kwargs)
            except Exception as e:
                exception = e
            finally:
                self.cached_func.cache_clear()

            if exception:
                raise exception

        return wrapper
