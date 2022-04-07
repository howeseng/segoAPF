from django.apps import AppConfig


class FunoConfig(AppConfig):
    name = 'funo'
    def ready(self):
        import funo.signals
