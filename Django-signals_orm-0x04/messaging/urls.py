from django.urls import path
from . import views

urlpatterns = [
    # ... other URL patterns ...
    path('delete/', views.delete_user, name='delete_user'),
    path('conversation/<int:user_id>/', views.view_conversation, name='view_conversation'),
]