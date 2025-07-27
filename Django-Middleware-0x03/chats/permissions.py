from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only authenticated users who are participants 
    in the conversation to view, edit, or delete messages.
    """

    def has_permission(self, request, view):
        # ✅ Enforce authenticated access
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        method = request.method

        # ✅ Check object type and participant status
        if hasattr(obj, 'participants'):  # Conversation object
            is_participant = user in obj.participants.all()
        elif hasattr(obj, 'conversation'):  # Message object
            is_participant = user in obj.conversation.participants.all()
        else:
            return False

        # ✅ Allow read-only access for safe methods
        if method in permissions.SAFE_METHODS:
            return is_participant

        # ✅ Restrict write/delete/update actions to participants
        if method in ['PUT', 'PATCH', 'DELETE', 'POST']:
            return is_participant

        return False
