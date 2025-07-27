from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import User, Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers # Already added in previous fix, ensure it's here
from .permissions import IsParticipantOrSender 

class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conversations to be viewed or edited.
    Supports listing, retrieving, creating, updating, and deleting conversations.
    Includes filtering capabilities.
    """
    permission_classes = [IsAuthenticated, IsParticipantOrSender]
    
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    # Add filter backends and fields
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'created_at': ['exact', 'gte', 'lte', 'gt', 'lt'], # Example: filter by created_at
        'participants__user_id': ['exact'], # Filter by participant UUID
    }

    def get_queryset(self):
        """
        Optionally restricts the returned conversations to those
        the current user is a participant of.
        """
        user = self.request.user
        if user.is_authenticated:
            return Conversation.objects.filter(participants=user).order_by('-created_at')
        return Conversation.objects.none()

    def perform_create(self, serializer):
        participant_ids = serializer.validated_data.pop('participant_ids', [])
        if self.request.user.is_authenticated and str(self.request.user.user_id) not in [str(uid) for uid in participant_ids]:
            participant_ids.append(self.request.user.user_id)
        conversation = serializer.save()
        if participant_ids:
            users = User.objects.filter(user_id__in=participant_ids)
            if len(users) != len(participant_ids):
                # Consider logging or a more specific error if invalid IDs are common
                pass
            conversation.participants.set(users)


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed or created.
    Supports listing, retrieving, creating, updating, and deleting messages.
    Includes filtering capabilities.
    """
    permission_classes = [IsAuthenticated, IsParticipantOrSender]
    
    queryset = Message.objects.all().order_by('sent_at')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    # Add filter backends and fields
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'conversation__conversation_id': ['exact'], # Filter messages by conversation UUID
        'sender__user_id': ['exact'], # Filter messages by sender UUID
        'sent_at': ['exact', 'gte', 'lte', 'gt', 'lt'], # Example: filter by sent_at
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        conversation_id = self.request.query_params.get('conversation_id', None)

        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)

        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(conversation__participants=user).distinct()

        return queryset.order_by('sent_at')

    def perform_create(self, serializer):
        conversation_id = serializer.validated_data.get('conversation_id')
        try:
            conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        except Exception as e:
            raise serializers.ValidationError({"conversation_id": "Invalid conversation ID."})

        if self.request.user.is_authenticated and self.request.user not in conversation.participants.all():
            raise serializers.ValidationError("You are not a participant of this conversation.")

        serializer.save(sender=self.request.user, conversation=conversation)

