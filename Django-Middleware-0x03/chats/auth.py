from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from chats.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends TokenObtainPairSerializer to include additional user data in the response.
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom user fields to the response
        user = self.user
        data.update({
            'user_id': str(user.user_id),
            'username': user.username,
            'email': user.email,
            'role': user.role,
        })

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Overrides the default JWT view to use our custom serializer.
    """
    serializer_class = CustomTokenObtainPairSerializer
