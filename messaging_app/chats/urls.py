from django.urls import path, include
from rest_framework.routers import DefaultRouter # Using DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Create a router instance for automatic URL routing
router = DefaultRouter()

# Register your ViewSets with the router.
# DefaultRouter is used here as these are top-level resources.
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

# The urlpatterns list for the messaging app.
# We include the router's URLs directly here.
urlpatterns = [
    path('', include(router.urls)),
]

# This will allow the API to be accessed at /api/chats/conversations/ and /api/chats/messages/