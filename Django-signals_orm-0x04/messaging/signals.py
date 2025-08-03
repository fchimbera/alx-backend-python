from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

# The original signal from Task 1
@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Signal handler to create a notification when a new message is saved.
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )
        print(f"DEBUG: Notification created for {instance.receiver.username}")


# This is the corrected pre_save signal handler for Task 2.
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal handler to log message content before it is updated.
    It checks if the message is being updated and if the content has changed.
    """
    # Check if the instance has a primary key, meaning it's an existing object being updated.
    if instance.pk:
        try:
            # Fetch the original object from the database before the save operation.
            original_message = Message.objects.get(pk=instance.pk)
        except Message.DoesNotExist:
            # This should not happen in a normal update flow.
            return
        
        # Compare the content. If it has changed, create a history entry.
        if original_message.content != instance.content:
            # Create a new MessageHistory record with the old content.
            # We assume the sender is the one who is editing their own message.
            MessageHistory.objects.create(
                message=instance,
                old_content=original_message.content,
                edited_by=instance.sender
            )
            
            # Update the edited_at field on the Message instance itself
            # The edited_by field is also updated here.
            instance.edited_at = timezone.now()
            instance.edited_by = instance.sender
            
            print(f"DEBUG: Message {instance.pk} updated. Old content logged to history.")