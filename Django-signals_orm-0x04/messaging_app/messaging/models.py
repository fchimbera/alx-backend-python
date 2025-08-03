from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    """
    Represents a direct message sent from one user to another.
    """
    # The user who sent the message.
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    
    # The user who received the message.
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    
    # The content of the message.
    content = models.TextField()
    
    # The timestamp when the message was created. auto_now_add=True
    # automatically sets the creation date.
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Order messages by timestamp in descending order (most recent first)
        ordering = ['-timestamp']

    def __str__(self):
        """String representation of the Message model."""
        return f'From {self.sender.username} to {self.receiver.username} at {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}'


class Notification(models.Model):
    """
    Represents a notification for a user, triggered by an event like
    receiving a new message.
    """
    # The user who will receive the notification.
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    
    # A link to the message that triggered this notification.
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    
    # A flag to check if the user has read the notification.
    is_read = models.BooleanField(default=False)
    
    # The timestamp when the notification was created.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Order notifications by creation date, most recent first.
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the Notification model."""
        return f'Notification for {self.user.username} about a message from {self.message.sender.username}'

