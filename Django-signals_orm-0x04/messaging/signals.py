from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


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


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal handler to log message content before it is updated.
    """
    if instance.pk:
        try:
            original_message = Message.objects.get(pk=instance.pk)
        except Message.DoesNotExist:
            return
        
        if original_message.content != instance.content:
            MessageHistory.objects.create(
                message=instance,
                old_content=original_message.content,
                edited_by=instance.sender
            )
            
            instance.edited_at = timezone.now()
            instance.edited_by = instance.sender
            
            print(f"DEBUG: Message {instance.pk} updated. Old content logged to history.")


# signal handler for clean up data when a user is deleted.
@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal handler to delete all messages, notifications, and message histories
    associated with a user after their account has been deleted.

    Note: The foreign keys in our models (Message, Notification, MessageHistory)
    are already set with on_delete=models.CASCADE. This means Django will
    automatically handle the cleanup of related data when a user is deleted.
    This signal handler provides an explicit, redundant cleanup as requested.
    """
    # The 'instance' here is the User object that was just deleted.
    print(f"DEBUG: User '{instance.username}' has been deleted. Starting data cleanup.")
    
    # Manually delete all messages where the deleted user was the sender or receiver.
    # This also triggers the CASCADE deletion of related Notifications and MessageHistory.
    sent_messages_count = Message.objects.filter(sender=instance).count()
    received_messages_count = Message.objects.filter(receiver=instance).count()
    
    # Perform the deletion
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    
    print(f"DEBUG: Deleted {sent_messages_count} sent messages and {received_messages_count} received messages.")

