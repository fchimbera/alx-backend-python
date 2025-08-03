from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from .models import Message, Notification, MessageHistory

class MessagingSignalTest(TestCase):
    """
    Tests to ensure the post_save and pre_save signals for the Message model
    work as expected.
    """

    def setUp(self):
        self.client = Client()
        self.sender = User.objects.create_user(username='sender', password='password123')
        self.receiver = User.objects.create_user(username='receiver', password='password123')
        self.other_user = User.objects.create_user(username='other_user', password='password123')
        self.client.login(username='sender', password='password123')

    def test_view_conversation_optimizes_queries(self):
        """
        Tests that the view_conversation view uses select_related and prefetch_related
        to reduce the number of queries.
        """
        # Create multiple messages between sender and receiver.
        Message.objects.create(sender=self.sender, receiver=self.receiver, content="Hello")
        Message.objects.create(sender=self.receiver, receiver=self.sender, content="Hi")
        message_to_edit = Message.objects.create(sender=self.sender, receiver=self.receiver, content="Last message")
        
        # Edit the message to create history.
        message_to_edit.content = "Last message, edited"
        message_to_edit.save()
        
        # We expect a fixed number of queries regardless of the number of messages or history entries.
        # 1. Query for the other user.
        # 2. Query for the messages, using select_related and prefetch_related.
        with self.assertNumQueries(2):
            response = self.client.get(reverse('view_conversation', args=[self.receiver.id]))
            
            self.assertEqual(response.status_code, 200)
            
            context = response.context
            self.assertEqual(len(context['conversation_messages']), 3)
            
            # Accessing the related data should not trigger new queries.
            first_message = context['conversation_messages'][0]
            self.assertIsNotNone(first_message.sender.username)
            self.assertIsNotNone(first_message.history_entries)
            
