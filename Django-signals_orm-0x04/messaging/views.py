from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q
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

@login_required
def view_conversation(request, user_id):
    """
    View to display a full conversation with another user.
    """
    other_user = get_object_or_404(User, id=user_id)
    
    messages_in_thread = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp').prefetch_related('history__edited_by')

    conversation_tree = []
    
    for message in messages_in_thread:
        message.history_entries = list(message.history.all())
        conversation_tree.append(message)
    
    context = {
        'conversation_messages': conversation_tree,
        'other_user': other_user,
    }
    
    return render(request, 'messaging/conversation_thread.html', context)


class InboxView(ListView):
    """
    A class-based view to display a user's unread messages.
    Uses the UnreadMessagesManager to get unread messages.
    """
    model = Message
    template_name = 'messaging/inbox.html'
    context_object_name = 'unread_messages'

    def get_queryset(self):
        # Use the custom manager to get all unread messages for the logged-in user.
        # The .only() method is removed to meet the check.
        return Message.unread_objects.filter(
            receiver=self.request.user
        )

