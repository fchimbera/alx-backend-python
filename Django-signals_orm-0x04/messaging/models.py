from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    """
    direct message sent from one user to another.
    Added a 'edited' field to track if the message has been modified.
    """
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False) # New field to track edits

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'From {self.sender.username} to {self.receiver.username} at {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}'


class Notification(models.Model):
    
    # notification for a user.
    
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
    A new model to store the history of message edits.
    Each instance represents a previous version of a message.
    """
    # Link to the original message that was edited.
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    
    # The content of the message before it was edited.
    old_content = models.TextField()
    
    # The timestamp when the edit occurred.
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Order history by the time of the edit, most recent first.
        ordering = ['-edited_at']
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return f'History for Message {self.message.id} at {self.edited_at.strftime("%Y-%m-%d %H:%M:%S")}'