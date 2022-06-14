from .utils import get_max_distance_thresold


def is_image_duplicate(image_hash, other_image_hash):
    distance = image_hash - other_image_hash
    return True if distance < get_max_distance_thresold() else False


def find_image_duplicates(image, user, permission_policy):
    instances = permission_policy.instances_user_has_permission_for(
        user, "choose"
    ).exclude(pk=image.pk)

    image_hash = image.hash_instance
    duplicates = (
        instance.pk
        for instance in instances.only("pk", "custom_hash").iterator()
        if is_image_duplicate(image_hash, instance.hash_instance)
    )
    return instances.filter(pk__in=duplicates)
