from django.apps import AppConfig

class EasyparkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'easypark'

    def ready(self):
        import easypark.signals  # เชื่อมต่อ Signal


