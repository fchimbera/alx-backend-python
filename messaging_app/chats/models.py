from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    This model includes additional fields as per the specification.
    """
    # Override the primary key to use UUID as specified
    # AbstractUser already provides username, first_name, last_name, email, password, is_staff, is_active, date_joined
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True # Indexed automatically as primary key, but explicitly noted
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="User's phone number"
    )

    # Define choices for the 'role' field as an ENUM
    ROLE_CHOICES = (
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='guest',
        null=False,
        help_text="Role of the user (guest, host, or admin)"
    )


    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['date_joined'] # Order users by their creation date

    def __str__(self):
        return self.email or self.username # Prioritize email for representation


class Conversation(models.Model):
    
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True # Indexed automatically as primary key
    )
    # Many-to-many relationship with the User model for participants
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        help_text="Users involved in this conversation"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of conversation creation"
    )

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ['-created_at'] # Order by most recent conversation

    def __str__(self):
        # Display participants' emails for easy identification
        participant_emails = ", ".join([user.email for user in self.participants.all()])
        return f"Conversation {self.conversation_id} with: {participant_emails}"


class Message(models.Model):
    """
    Model for individual messages within a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True # Indexed automatically as primary key
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE, # If a user is deleted, their messages are also deleted
        related_name='sent_messages',
        help_text="The user who sent the message"
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE, # If a conversation is deleted, its messages are also deleted
        related_name='messages',
        help_text="The conversation this message belongs to"
    )
    message_body = models.TextField(
        null=False,
        help_text="The content of the message"
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the message was sent"
    )

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['sent_at'] # Order messages chronologically within a conversation

    def __str__(self):
        return f"Message from {self.sender.email} in Conversation {self.conversation.conversation_id} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"


