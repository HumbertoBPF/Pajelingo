from django.apps import AppConfig


class LanguageschoolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'languageschool'

    def ready(self):
        from django.db.models.signals import post_save
        from languageschool.signals import save_app_users
        from django.contrib.auth.models import User

        post_save.connect(save_app_users, sender=User, dispatch_uid="id_save_app_users")
