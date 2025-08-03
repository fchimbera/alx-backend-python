from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout
from django.contrib import messages
from .models import Message
from django.views.generic import ListView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@login_required
def delete_user(request):
    """
    View to handle the deletion of a user's account.
    """
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    return HttpResponse("Are you sure you want to delete your account? This action is irreversible.", status=200)

@method_decorator(cache_page(60), name='dispatch')
class InboxView(ListView):
    """
    A class-based view to display a user's messages.
    This view is cached for 60 seconds using the cache_page decorator.
    """
    model = Message
    template_name = 'messaging/inbox.html'
    context_object_name = 'inbox_messages'

    def get_queryset(self):
        """
        Fetches all messages for the current user, using select_related for optimization.
        Also demonstrates filtering by sender, using a custom unread manager, and optimizing with .only().
        """
        sent_messages = Message.objects.filter(
            sender=self.request.user
        ).only('id', 'subject', 'timestamp', 'receiver')

        unread_messages = Message.unread.unread_for_user(self.request.user).only('id', 'subject', 'timestamp', 'sender')

        # Main inbox: messages received by the current user
        inbox_messages = Message.objects.filter(
            receiver=self.request.user
        ).select_related('sender', 'receiver').only('id', 'subject', 'timestamp', 'sender', 'receiver').order_by('-timestamp')

        return inbox_messages
