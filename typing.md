# Getting Started with Type Checking

This follows the steps in https://github.com/microsoft/pyright/blob/main/docs/getting-started.md.

## Write a minimal configuration file

```
[tool.pyright]
include = ["src"]
exclude = ["**/migrations", "**/__pycache__"]
extraPaths = ["./venv/lib/python3.10/site-packages/"] # So pyright can load imports on CI
ignore = ["tests"]
defineConstant = { DEBUG = true }

reportMissingImports = true
reportMissingTypeStubs = false

pythonVersion = "3.10"
pythonPlatform = "Linux"
```

## Run pyright over your source base with the default settings. Fix any errors and warnings that it emits.

I've run into the following errors:

### error: "Image" is not a known member of module (reportGeneralTypeIssues)

**Source code**

```python
yield PIL.Image.open(image_file)
```

**Fix**

Changed `import PIL` to `from PIL import Image`.

## Enable the `reportMissingTypeStubs` setting in the config file and add (minimal) type stub files for the imported files.

After enabling it, I've got the following errors:

```bash
wagtail-images-deduplicator/src/wagtail_images_deduplicator/__init__.py
wagtail-images-deduplicator/src/wagtail_images_deduplicator/__init__.py:1:8 - error: Stub file not found for "wagtail.images.utils" (reportMissingTypeStubs)

wagtail-images-deduplicator/src/wagtail_images_deduplicator/apps.py
wagtail-images-deduplicator/src/wagtail_images_deduplicator/apps.py:1:6 - error: Stub file not found for "django.apps" (reportMissingTypeStubs)

wagtail-images-deduplicator/src/wagtail_images_deduplicator/apps.py:2:6 - error: Stub file not found for "django.core.checks" (reportMissingTypeStubs)

wagtail-images-deduplicator/src/wagtail_images_deduplicator/checks.py
wagtail-images-deduplicator/src/wagtail_images_deduplicator/checks.py:1:6 - error: Stub file not found for "django.core.checks" (reportMissingTypeStubs)

wagtail-images-deduplicator/src/wagtail_images_deduplicator/checks.py:2:6 - error: Stub file not found for "wagtail.images" (reportMissingTypeStubs)

wagtail-images-deduplicator/src/wagtail_images_deduplicator/find_duplicates.py
wagtail-images-deduplicator/src/wagtail_images_deduplicator/find_duplicates.py:1:6 - error: Stub file not found for "django.db.models" (reportMissingTypeStubs)

wagtail-images-deduplicator/src/wagtail_images_deduplicator/find_duplicates.py:2:6 - error: Stub file not found for "wagtail.images" (reportMissingTypeStubs)

wagtail-images-deduplicator/src/wagtail_images_deduplicator/models.py
wagtail-images-deduplicator/src/wagtail_images_deduplicator/models.py:4:6 - error: Stub file not found for "django.db" (reportMissingTypeStubs)

wagtail-images-deduplicator/src/wagtail_images_deduplicator/utils.py
wagtail-images-deduplicator/src/wagtail_images_deduplicator/utils.py:3:8 - error: Stub file not found for "imagehash" (reportMissingTypeStubs)

wagtail-images-deduplicator/src/wagtail_images_deduplicator/utils.py:4:6 - error: Stub file not found for "django.conf" (reportMissingTypeStubs)

wagtail-images-deduplicator/src/wagtail_images_deduplicator/utils.py:5:6 - error: Stub file not found for "django.core.exceptions" (reportMissingTypeStubs)
```

Read https://github.com/microsoft/pyright/blob/main/docs/type-concepts.md.

## Look for type stubs for the packages you use

I've installed `django-types` and it fixed all `reportMissingTypeStubs` errors related to Django.

It introduced this error as a side effect:

```bash
wagtail-images-deduplicator/src/wagtail_images_deduplicator/models.py:42:19 - error: Cannot access member "open_file" for type "DuplicateFindingMixin"
```

`DuplicateFindingMixin` is designed to be mixed with an actual `Image` model where `open_file` is defined. Here is a link in Stackoverflow about adding type hinting to mixin classes and I went for the solution based from Guido's one:

```python
from typing import Callable
from django.db import models

class DuplicateFindingBase:
    open_file: Callable

class DuplicateFindingMixin(models.Model, DuplicateFindingBase):
    ...
```

## In cases where type stubs do not yet exist for a package you are using, consider creating a custom type stub that defines the portion of the interface that your source code consumes.

Wagtail is a perfect example for this section.

I've followed the instructions in [Generating Type Stubs](https://github.com/microsoft/pyright/blob/main/docs/type-stubs.md#generating-type-stubs) to automatically generate type stubs for `wagtail.images` and removed all the folders/files that aren't used in this project:

```bash
pyright --createstub wagtail.images
```

It suppressed the `reportMissingTypeStubs)` errors related to 'wagtail.images'.

I've also generated type stubs for the `imagehash`.

## Incrementally add type annotations to your code files
