from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout
from django.contrib import messages
from .models import Message
from django.views.generic import ListView

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


class InboxView(ListView):
    """
    A class-based view to display a user's unread messages.
    Uses the UnreadMessagesManager to get unread messages and the .only()
    method for optimization.
    """
    model = Message
    template_name = 'messaging/inbox.html'
    context_object_name = 'unread_messages'

    def get_queryset(self):
        
        return (Message.unread.unread_for_user(self.request.user).only(),
                Message.unread_objects.filter(
                receiver=self.request.user).select_related('sender', 'receiver').order_by('-timestamp')
                )
