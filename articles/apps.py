from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles'

    # Used to connect recievers
    # def ready(self):
    #     Implicitly connect signal handlers decorated with @receiver.
    #     from . import signals
