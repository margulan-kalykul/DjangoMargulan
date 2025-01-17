from django.apps import AppConfig
from django.db.models.signals import post_save


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles'

    # Used to connect recievers
    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals

        # Explicitly connect a signal handler.
        # post_save.connect(signals.my_callback)
