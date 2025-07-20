from django.urls import path, include
from rest_framework import routers 
from .views import ConversationViewSet, MessageViewSet

# Create a DefaultRouter for top-level resources (e.g., /conversations/)
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet)

# NestedDefaultRouter for nesting messages under conversations
# parent_lookup_kwargs' must match the lookup field in the parent viewset
# ConversationViewSet, the lookup field is 'conversation_id' (default for UUID primary key)
conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')


# The urlpatterns list for the messaging app.
urlpatterns = [
    path('', include(router.urls)), # Includes top-level conversation URLs
    path('', include(conversations_router.urls)), # Includes nested message URLs
]

# This will allow the API to be accessed at /api/chats/conversations/ and /api/chats/messages/