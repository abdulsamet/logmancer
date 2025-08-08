from django.apps import AppConfig


class LogmancerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "logmancer"
    verbose_name = "Logmancer - Magical Logging for Django"

    def ready(self):
        import logmancer.signals  # noqa: F401
