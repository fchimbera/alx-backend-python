from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification
from django.contrib.auth.models import User

# The @receiver decorator connects the function to the post_save signal of the Message model.
# This function will be called every time a Message object is saved.
@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Signal handler to create a notification when a new message is saved.

    :param sender: The model class that sent the signal (Message).
    :param instance: The actual instance of Message that was just saved.
    :param created: A boolean; True if a new record was created, False if an update.
    """
    # We only want to create a notification if a new message was created,
    # not when an existing message is updated.
    if created:
        # The user to be notified is the receiver of the new message.
        # The message is the instance that just got created.
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )
        print(f"DEBUG: Notification created for {instance.receiver.username}")

