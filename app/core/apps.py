from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.core'
    
    def ready(self):
        import app.core.signals  # importa los signals
