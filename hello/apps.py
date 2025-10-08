from django.apps import AppConfig


class HelloConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hello"

    def ready(self):
        from . import signals  # noqa: F401
