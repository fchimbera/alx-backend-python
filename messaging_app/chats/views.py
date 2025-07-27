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
        # ✅ Filter messages by conversations user is part of
        user = self.request.user
        return Message.objects.filter(conversation__participants=user)

    def create(self, request, *args, **kwargs):
        # ✅ Get conversation_id from request data
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response({'detail': 'conversation_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({'detail': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Check user is a participant
        if request.user not in conversation.participants.all():
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        # ✅ Create the message
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

