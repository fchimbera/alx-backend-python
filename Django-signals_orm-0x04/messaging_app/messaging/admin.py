from django.contrib import admin
from .models import Message, Notification, MessageHistory

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Message model.
    """
    list_display = ('sender', 'receiver', 'parent_message', 'is_read', 'timestamp', 'edited_at', 'edited_by', 'content')
    list_filter = ('timestamp', 'sender', 'receiver', 'is_read', 'edited_at')
    search_fields = ('content', 'sender__username', 'receiver__username')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Notification model.
    """
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'user')
    search_fields = ('user__username', 'message__content')
    ordering = ('-created_at',)

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the MessageHistory model.
    """
    list_display = ('message', 'old_content', 'edited_by', 'edited_at')
    list_filter = ('edited_at', 'edited_by')
    search_fields = ('message__content', 'old_content', 'edited_by__username')
    date_hierarchy = 'edited_at'
    ordering = ('-edited_at',)
