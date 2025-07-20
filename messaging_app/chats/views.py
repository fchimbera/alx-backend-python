from django.shortcuts import render
# messaging/views.py (or chats/views.py)
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import User, Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework import serializers 


class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conversations to be viewed or edited.
    Supports listing, retrieving, creating, updating, and deleting conversations.
    """
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated] # Only authenticated users can access

    def get_queryset(self):
        """
        Optionally restricts the returned conversations to those
        the current user is a participant of.
        """
        user = self.request.user
        if user.is_authenticated:
            # Return conversations where the current user is a participant
            return Conversation.objects.filter(participants=user).order_by('-created_at')
        return Conversation.objects.none() # No conversations for unauthenticated users

    def perform_create(self, serializer):
        """
        When creating a new conversation, ensure the requesting user is
        automatically added as a participant.
        """
        # Get participant_ids from the validated data, default to empty list
        participant_ids = serializer.validated_data.pop('participant_ids', [])

        # Ensure the requesting user's ID is in the participant_ids
        # Convert UUID to string for comparison if necessary, or ensure consistency
        if self.request.user.is_authenticated and str(self.request.user.user_id) not in [str(uid) for uid in participant_ids]:
            participant_ids.append(self.request.user.user_id)

        # Create the conversation instance without participants initially
        conversation = serializer.save()

        # Add participants to the conversation
        if participant_ids:
            # Filter for existing users based on the provided IDs
            users = User.objects.filter(user_id__in=participant_ids)
            if len(users) != len(participant_ids):
                # This check helps catch invalid IDs if they weren't caught by the serializer's validation
                # However, the serializer's ListField with UUIDField child should already handle type validation.
                # For actual existence, it's handled by .set() below.
                pass # Or raise a more specific error if needed

            conversation.participants.set(users) # Set all participants


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed or created.
    Supports listing, retrieving, creating, updating, and deleting messages.
    """
    queryset = Message.objects.all().order_by('sent_at')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated] # Only authenticated users can access

    def get_queryset(self):
        """
        Optionally restricts the returned messages to those
        within a specific conversation, or only messages sent by/to the user.
        """
        queryset = super().get_queryset()
        conversation_id = self.request.query_params.get('conversation_id', None)

        if conversation_id:
            # Filter messages by a specific conversation ID
            queryset = queryset.filter(conversation__conversation_id=conversation_id)

        # Further filter to only show messages in conversations the user is part of
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(conversation__participants=user).distinct()

        return queryset.order_by('sent_at')


    def perform_create(self, serializer):
        """
        When creating a new message, automatically set the sender to the
        requesting user and associate it with the specified conversation.
        """
        # The serializer should have validated conversation_id and message_body
        conversation_id = serializer.validated_data.get('conversation_id')

        try:
            conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        except Exception as e:
            # This should ideally be caught by serializer validation if conversation_id is required
            raise serializers.ValidationError({"conversation_id": "Invalid conversation ID."})

        # Ensure the requesting user is a participant of the conversation they are trying to send a message to
        if self.request.user.is_authenticated and self.request.user not in conversation.participants.all():
            raise serializers.ValidationError("You are not a participant of this conversation.")

        # Set the sender to the current authenticated user
        serializer.save(sender=self.request.user, conversation=conversation)

