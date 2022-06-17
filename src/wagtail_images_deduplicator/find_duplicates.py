from django.db.models import Q
from wagtail.images import get_image_model

from .utils import get_max_distance_thresold


def is_image_duplicate(image_hash, other_image_hash):
    distance = image_hash - other_image_hash
    return True if distance < get_max_distance_thresold() else False


def find_image_duplicates(image, user, permission_policy):
    instances = permission_policy.instances_user_has_permission_for(
        user, "choose"
    ).exclude(pk=image.pk)

    file_hash = image.file_hash
    custom_hash = image.custom_hash

    # Try to shortcut by finding exact duplicates (if any).
    if custom_hash:
        if file_hash:
            duplicates = instances.filter(
                Q(file_hash=file_hash) | Q(custom_hash=custom_hash)
            )
        else:
            duplicates = instances.filter(custom_hash=custom_hash)

        if duplicates:
            return duplicates

    elif file_hash:
        # Custom hash isn't set, resort to finding exact duplicates by file hash.
        return instances.filter(file_hash=file_hash)

    else:
        # Neither file hash nor custom hash are set. We can't find duplicates!
        return get_image_model().objects.none()

    # We haven't found any exact duplicates at this point but the image's custom hash is set.
    # Let's find the near duplicates (if any).
    image_hash = image.hash_instance
    duplicates = (
        instance.pk
        for instance in instances.exclude(custom_hash="")
        .only("pk", "custom_hash")
        .iterator()
        if is_image_duplicate(image_hash, instance.hash_instance)
    )
    return instances.filter(pk__in=duplicates)
