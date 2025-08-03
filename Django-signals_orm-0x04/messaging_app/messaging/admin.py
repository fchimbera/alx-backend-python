from django.contrib import admin
from .models import Message, Notification

# Register the Message model with the Django admin site.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Message model.
    """
    list_display = ('sender', 'receiver', 'timestamp', 'content')
    list_filter = ('timestamp', 'sender', 'receiver')
    search_fields = ('content', 'sender__username', 'receiver__username')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

# Register the Notification model with the Django admin site.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Notification model.
    """
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'user')
    search_fields = ('user__username', 'message__content')
    ordering = ('-created_at',)
