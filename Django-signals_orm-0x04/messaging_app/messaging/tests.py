from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from .models import Message, Notification, MessageHistory

class UnreadMessageManagerTest(TestCase):
    """
    Tests for the custom UnreadMessagesManager.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.user3 = User.objects.create_user(username='user3', password='password123')
        self.client = Client()
        self.client.login(username='user1', password='password123')

    def test_unread_messages_manager_filters_correctly(self):
        """
        Tests that the UnreadMessagesManager returns only unread messages
        for the correct user.
        """
        # Create a few messages for user1.
        Message.objects.create(sender=self.user2, receiver=self.user1, content="Message 1", is_read=False)
        Message.objects.create(sender=self.user3, receiver=self.user1, content="Message 2", is_read=False)
        Message.objects.create(sender=self.user2, receiver=self.user1, content="Message 3", is_read=True)
        # Create a message for another user that should not be counted.
        Message.objects.create(sender=self.user1, receiver=self.user2, content="Message 4", is_read=False)
        
        # Check that the manager returns the correct number of unread messages for user1.
        unread_count = Message.unread_objects.filter(receiver=self.user1).count()
        self.assertEqual(unread_count, 2)
        
        # Check that the messages returned are indeed unread.
        for msg in Message.unread_objects.filter(receiver=self.user1):
            self.assertFalse(msg.is_read)

    def test_inbox_view_displays_unread_messages(self):
        """
        Tests that the InboxView correctly displays only unread messages.
        """
        # Create some messages for the logged-in user (user1)
        Message.objects.create(sender=self.user2, receiver=self.user1, content="Unread 1", is_read=False)
        Message.objects.create(sender=self.user2, receiver=self.user1, content="Read 1", is_read=True)
        Message.objects.create(sender=self.user3, receiver=self.user1, content="Unread 2", is_read=False)

        response = self.client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 200)

        # The view should return only the unread messages.
        unread_messages = response.context['unread_messages']
        self.assertEqual(len(unread_messages), 2)
        
        for msg in unread_messages:
            self.assertFalse(msg.is_read)
            
        # The content of the messages should be correct.
        self.assertIn("Unread 1".encode('utf-8'), response.content)
        self.assertNotIn("Read 1".encode('utf-8'), response.content)
        self.assertIn("Unread 2".encode('utf-8'), response.content)
