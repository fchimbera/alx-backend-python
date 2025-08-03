from django.apps import AppConfig

class MessagingConfig(AppConfig):
    """
    App configuration for the messaging app.
    """
    # Sets the default primary key field type for models in this app.
    default_auto_field = 'django.db.models.BigAutoField'
    
    # The name of the app.
    name = 'messaging'

    def ready(self):
        """
        This method is called when Django starts up.
        It imports the signals module to ensure the signal handlers are
        connected and registered.
        """
        # Importing signals at startup ensures the @receiver decorator runs.
        # It's a standard practice for Django signals.
        import messaging.signals

