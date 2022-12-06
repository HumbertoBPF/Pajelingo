from languageschool.models import AppUser


def save_app_users(sender, instance, created, **kwargs):
    if created:
        AppUser.objects.create(user=instance)
