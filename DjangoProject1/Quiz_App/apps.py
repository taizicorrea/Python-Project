from django.apps import AppConfig




class QuizAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Quiz_App'

class QuizAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Quiz_App'

    def ready(self):
        from . import signals  # Use relative import to load signals