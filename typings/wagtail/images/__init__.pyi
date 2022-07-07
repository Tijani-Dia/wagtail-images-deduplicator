import typing

from wagtail.images.models import AbstractImage

def get_image_model() -> typing.Type[AbstractImage]: ...
