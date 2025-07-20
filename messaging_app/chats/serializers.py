from rest_framework import serializers
from .models import User,Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.
    Exposes essential user information.
    """
    class Meta:
        model = User
        fields = [
            'user_id',
            'username', # Inherited from AbstractUser
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'date_joined', # Equivalent to created_at from AbstractUser
        ]
        read_only_fields = ['user_id', 'date_joined'] # These fields are auto-generated


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Includes nested sender information.
    """
    # Nested serializer for the sender, making it read-only as we don't create/update
    # users directly through message creation.
    sender = UserSerializer(read_only=True)

    # To allow writing/creating messages, we need to specify how to handle the sender ID.
    # This field will be used for input (e.g., when creating a new message).
    # When creating, you'd pass a sender_id (UUID string).
    sender_id = serializers.UUIDField(write_only=True)
    conversation_id = serializers.UUIDField(write_only=True) # For creating messages

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',        # For reading (nested User object)
            'sender_id',     # For writing (UUID string)
            'conversation',  # For reading (nested Conversation object, if desired, but typically handled by ConversationSerializer)
            'conversation_id', # For writing (UUID string)
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at', 'conversation'] # conversation is read-only here when nested

    def create(self, validated_data):
        # Extract sender_id and conversation_id from validated_data
        sender_id = validated_data.pop('sender_id')
        conversation_id = validated_data.pop('conversation_id')

        try:
            sender = User.objects.get(user_id=sender_id)
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"sender_id": "User with this ID does not exist."})
        except Conversation.DoesNotExist:
            raise serializers.ValidationError({"conversation_id": "Conversation with this ID does not exist."})

        # Create the message instance
        message = Message.objects.create(sender=sender, conversation=conversation, **validated_data)
        return message


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Handles many-to-many participants and nested messages.
    """
    # Nested serializer for participants (many-to-many relationship).
    # read_only=True because we typically manage participants through separate views/actions,
    # not directly when creating/updating a conversation object itself via this serializer.
    participants = UserSerializer(many=True, read_only=True)

    # Nested serializer for messages within this conversation (reverse foreign key).
    # read_only=True because messages are created/updated via their own serializer/endpoint.
    messages = MessageSerializer(many=True, read_only=True)

    # To allow adding participants when creating/updating a conversation,
    # you might want a write-only field for participant IDs.
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False, # Not required for every update
        help_text="List of User UUIDs to add as participants."
    )

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',      # For reading (nested User objects)
            'participant_ids',   # For writing (list of UUIDs)
            'messages',          # For reading (nested Message objects)
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)

        # Add participants to the conversation
        if participant_ids:
            users = User.objects.filter(user_id__in=participant_ids)
            if len(users) != len(participant_ids):
                # Handle cases where some IDs might not correspond to existing users
                raise serializers.ValidationError({"participant_ids": "One or more participant IDs are invalid."})
            conversation.participants.set(users) # Use .set() for ManyToMany

        return conversation

    def update(self, instance, validated_data):
        participant_ids = validated_data.pop('participant_ids', None)

        # Update standard fields
        instance.created_at = validated_data.get('created_at', instance.created_at)
        # Add other fields if they were exposed for update

        # Update participants if participant_ids are provided
        if participant_ids is not None:
            users = User.objects.filter(user_id__in=participant_ids)
            if len(users) != len(participant_ids):
                raise serializers.ValidationError({"participant_ids": "One or more participant IDs are invalid."})
            instance.participants.set(users) # Use .set() to replace current participants

        instance.save()
        return instance

