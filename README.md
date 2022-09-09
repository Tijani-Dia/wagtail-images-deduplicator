# Wagtail Images De-duplicator

`wagtail-images-deduplicator` is a Wagtail app to detect duplicate images in the admin. It's built with [`imagehash`](https://github.com/JohannesBuchner/imagehash).

## Requirements

Wagtail Images De-duplicator works with `wagtail>=3.0`.

## Installation

Use `pip` to install this package:

```bash
pip install wagtail-images-deduplicator
```

## Configuration

- Add `wagtail_images_deduplicator` to your `INSTALLED_APPS` in your project's settings.

- Add the `DuplicateFindingMixin` to your [custom image model](https://docs.wagtail.org/en/latest/advanced_topics/images/custom_image_model.html). An example of doing it is shown below:

```python
from wagtail.images.models import Image, AbstractImage, AbstractRendition

from wagtail_images_deduplicator.models import DuplicateFindingMixin


class CustomImage(DuplicateFindingMixin, AbstractImage):
    admin_form_fields = Image.admin_form_fields


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
```

If you choose to add the mixin and have existing image data, you will need to call `save()` on all existing instances to fill in the new hash value:

```bash
from wagtail.images import get_image_model

for image in get_image_model().objects.all():
    image.save()
```

## Settings

### `WAGTAILIMAGESDEDUPLICATOR_HASH_FUNC`

This setting determines the [hash function](https://github.com/JohannesBuchner/imagehash#references) to use.

| Hash function          | Reference                                                                       | Setting name                |
| ---------------------- | ------------------------------------------------------------------------------- | --------------------------- |
| Average hashing        | http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html     | `average_hash`              |
| Perceptual hashing     | http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html     | `phash` (_default_)         |
| Difference hashing     | http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html | `dhash` or `dhash_vertical` |
| Wavelet hashing        | https://fullstackml.com/2016/07/02/wavelet-image-hash-in-python/                | `whash`                     |
| HSV color hashing      |                                                                                 | `colorhash`                 |
| Crop-resistant hashing | https://ieeexplore.ieee.org/document/6980335                                    | `crop_resistant_hash`       |

### `WAGTAILIMAGESDEDUPLICATOR_MAX_DISTANCE_THRESOLD`

This setting determines the maximum distance between 2 images to consider them as duplicates.  
The default value is **5**.

To help you assess how these different algorithms behave and to learn more about hash distances, check out the [examples section](https://github.com/JohannesBuchner/imagehash#examples) of the imagehash library's README.
