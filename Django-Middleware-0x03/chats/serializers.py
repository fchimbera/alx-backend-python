from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    
    full_name = serializers.SerializerMethodField()

    # It mirrors the 'email' field but is declared separately for demonstration.
    email_display = serializers.CharField(source='email', read_only=True, help_text="A read-only display of the user's email.")

    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'email_display', # Include the new explicit CharField here
            'phone_number',
            'role',
            'date_joined',
        ]
        read_only_fields = ['user_id', 'date_joined', 'full_name', 'email_display']


    def get_full_name(self, obj):
        """
        Returns the combined first_name and last_name of the user.
        """
        return f"{obj.first_name} {obj.last_name}".strip()


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Includes nested sender information.
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    conversation_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id',
            'conversation',
            'conversation_id',
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at', 'conversation']

    def create(self, validated_data):
        sender_id = validated_data.pop('sender_id')
        conversation_id = validated_data.pop('conversation_id')

        try:
            sender = User.objects.get(user_id=sender_id)
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"sender_id": "User with this ID does not exist."})
        except Conversation.DoesNotExist:
            raise serializers.ValidationError({"conversation_id": "Conversation with this ID does not exist."})

        message = Message.objects.create(sender=sender, conversation=conversation, **validated_data)
        return message


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Handles many-to-many participants, nested messages, and a last message preview.
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    # Adding a SerializerMethodField for a preview of the last message
    last_message_preview = serializers.SerializerMethodField()

    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="List of User UUIDs to add as participants."
    )

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'messages',
            'last_message_preview',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'last_message_preview']

    def get_last_message_preview(self, obj):
        """
        Returns a preview of the body of the most recent message in the conversation.
        """
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return last_message.message_body[:50] + '...' if len(last_message.message_body) > 50 else last_message.message_body
        return None

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)

        if participant_ids:
            users = User.objects.filter(user_id__in=participant_ids)
            if len(users) != len(participant_ids):
                raise serializers.ValidationError({"participant_ids": "One or more participant IDs are invalid."})
            conversation.participants.set(users)

        return conversation

    def update(self, instance, validated_data):
        participant_ids = validated_data.pop('participant_ids', None)

        instance.created_at = validated_data.get('created_at', instance.created_at)

        if participant_ids is not None:
            users = User.objects.filter(user_id__in=participant_ids)
            if len(users) != len(participant_ids):
                raise serializers.ValidationError({"participant_ids": "One or more participant IDs are invalid."})
            instance.participants.set(users)

        instance.save()
        return instance

