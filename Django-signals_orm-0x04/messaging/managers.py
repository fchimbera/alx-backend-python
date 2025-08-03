from django.db import models
from django.db.models import QuerySet

class UnreadMessagesManager(models.Manager):
    """
    A custom manager that filters for unread messages.
    """
    def get_queryset(self):
        # Filters for messages where the 'is_read' field is False.
        return super().get_queryset().filter(is_read=False)


class OptimizedMessageManager(models.Manager):
    """
    A custom manager to handle advanced ORM queries for messages.
    Uses select_related to pre-fetch the sender and receiver.
    """
    def get_queryset(self):
        # Pre-fetches related User objects to avoid N+1 query problems.
        return super().get_queryset().select_related(
            'sender', 'receiver', 'parent_message'
        )