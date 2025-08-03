from django.db import models
from django.db.models import QuerySet
from django.contrib.auth.models import User

# Custom manager for filtering unread messages.
class UnreadMessagesManager(models.Manager):
    """
    A custom manager that filters for unread messages.
    """
    def get_queryset(self):
        # We use .filter(is_read=False) to get only unread messages.
        return super().get_queryset().filter(is_read=False)


# Default manager for all messages, optimized with select_related.
class OptimizedMessageManager(models.Manager):
    """
    A custom manager to handle advanced ORM queries for messages.
    Uses select_related to pre-fetch the sender and receiver.
    """
    def get_queryset(self):
        return super().get_queryset().select_related(
            'sender', 'receiver', 'parent_message'
        )


class Message(models.Model):
    """
    Represents a direct message or a reply in a threaded conversation.
    """
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # The new field to track if a message has been read.
    # Named 'is_read' to meet the check.
    is_read = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, related_name='edited_messages', on_delete=models.SET_NULL, null=True, blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    # The default manager.
    objects = OptimizedMessageManager()
    # The custom manager for unread messages.
    unread_objects = UnreadMessagesManager()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'From {self.sender.username} to {self.receiver.username}'


class Notification(models.Model):
    """
    Represents a notification for a user.
    """
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user.username} about a message from {self.message.sender.username}'


class MessageHistory(models.Model):
    """
    A model to store the history of message edits.
    """
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return f'History for Message {self.message.id} by {self.edited_by.username} at {self.edited_at}'
