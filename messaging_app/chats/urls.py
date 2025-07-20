from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Create a router instance for automatic URL routing
router = DefaultRouter()

# Register your ViewSets with the router.
# This will automatically generate URLs for listing, retrieving, creating,
# updating, and deleting conversations and messages.
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

# We include the router's URLs directly here.
urlpatterns = [
    path('', include(router.urls)),
]
# This will allow the API to be accessed at /api/chats/conversations/ and /api/chats/messages/