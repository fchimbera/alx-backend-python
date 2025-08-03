from django.test import TestCase

from django.contrib.auth.models import User
from .models import Message, Notification

class MessagingSignalTest(TestCase):
    """
    Tests to ensure the post_save signal for the Message model
    correctly creates a Notification.
    """

    def setUp(self):
        """
        Set up the necessary objects for the tests.
        We'll create two user instances: a sender and a receiver.
        """
        self.sender = User.objects.create_user(username='sender', password='password123')
        self.receiver = User.objects.create_user(username='receiver', password='password123')
        self.other_user = User.objects.create_user(username='other_user', password='password123')

    def test_notification_created_on_new_message(self):
        """
        Tests that a new Notification is created for the receiver when a new
        Message is created.
        """
        # Initially, there should be no notifications.
        self.assertEqual(Notification.objects.count(), 0)

        # Create a new message from sender to receiver.
        # This action should trigger our post_save signal.
        new_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello there!"
        )

        # After creating the message, a notification should exist.
        self.assertEqual(Notification.objects.count(), 1)
        
        # Verify the details of the created notification.
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, new_message)
        self.assertFalse(notification.is_read)

    def test_notification_not_created_on_update(self):
        """
        Tests that the signal does not create a new notification when an
        existing message is updated.
        """
        # Create an initial message. This will create one notification.
        initial_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="First message."
        )
        self.assertEqual(Notification.objects.count(), 1)

        # Update the message content and save it.
        # The 'created' argument in the signal will be False, so no
        # new notification should be generated.
        initial_message.content = "First message, updated."
        initial_message.save()

        # The notification count should still be 1.
        self.assertEqual(Notification.objects.count(), 1)

        # Verify that the existing notification's details haven't changed.
        notification = Notification.objects.first()
        self.assertEqual(notification.message, initial_message)


    def test_notification_count_with_multiple_messages(self):
        """
        Tests that multiple messages correctly create multiple notifications.
        """
        # Send a message from sender to receiver.
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="First message."
        )
        # Send a message from other_user to receiver.
        Message.objects.create(
            sender=self.other_user,
            receiver=self.receiver,
            content="Second message."
        )
        # Send a message from sender to other_user.
        Message.objects.create(
            sender=self.sender,
            receiver=self.other_user,
            content="Third message."
        )

        # There should be one notification for each of the three messages.
        self.assertEqual(Notification.objects.count(), 3)
        
        # Check notifications for the receiver.
        self.assertEqual(Notification.objects.filter(user=self.receiver).count(), 2)
        # Check notifications for the other_user.
        self.assertEqual(Notification.objects.filter(user=self.other_user).count(), 1)
