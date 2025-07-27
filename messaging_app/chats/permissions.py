from rest_framework import permissions


class IsParticipantOrSender(permissions.BasePermission):
    """
    Allows access only to participants of a conversation or the sender of a message.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if hasattr(obj, 'participants'):
            return user in obj.participants.all()

        if hasattr(obj, 'sender') and hasattr(obj, 'conversation'):
            return user == obj.sender or user in obj.conversation.participants.all()

        return False
