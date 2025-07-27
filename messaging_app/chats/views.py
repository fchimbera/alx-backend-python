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
from .permissions import IsParticipantOfConversation


class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conversations to be viewed or edited.
    Supports listing, retrieving, creating, updating, and deleting conversations.
    Includes filtering capabilities.
    """
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    
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
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # ✅ Restrict messages to participant access only
        user = self.request.user
        return Message.objects.filter(conversation__participants=user)

    def retrieve(self, request, *args, **kwargs):
        message = self.get_object()
        if request.user not in message.conversation.participants.all():
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        if request.user not in message.conversation.participants.all():
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        if request.user not in message.conversation.participants.all():
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)