# messaging/models.py

from django.db import models
from django.db.models import QuerySet
from django.contrib.auth.models import User

class OptimizedMessageManager(models.Manager):
    """
    A custom manager to handle advanced ORM queries for messages.
    Uses select_related to pre-fetch the sender and receiver.
    """
    def get_queryset(self):
        # We also need to select_related on parent_message to avoid N+1 queries when traversing a thread.
        return super().get_queryset().select_related('sender', 'receiver', 'parent_message')


class Message(models.Model):
    """
    Represents a direct message or a reply in a threaded conversation.
    """
    # A self-referential foreign key to link a reply to its parent message.
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
    edited_by = models.ForeignKey(User, related_name='edited_messages', on_delete=models.SET_NULL, null=True, blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    objects = OptimizedMessageManager()

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
