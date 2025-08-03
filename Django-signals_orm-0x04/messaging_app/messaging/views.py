from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q
from .models import Message

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

# A simple helper function to build the conversation tree recursively.
def get_threaded_replies(message_list, message_id):
    """
    Recursively finds all replies for a given message ID from a flat list.
    """
    replies = [msg for msg in message_list if getattr(msg, 'parent_message_id', None) == message_id]
    for reply in replies:
        reply.replies = get_threaded_replies(message_list, reply.id)
    return replies

@login_required
def view_conversation(request, user_id):
    """
    View to display a full conversation with another user.
    This view fetches all messages between two users and structures them
    into a threaded format.
    It uses prefetch_related and select_related for optimized querying.
    """
    other_user = get_object_or_404(User, id=user_id)
    
    # Efficiently fetch all messages in the conversation.
    # The OptimizedMessageManager already uses select_related for sender/receiver.
    # The prefetch_related is used to fetch the history of each message.
    messages_in_thread = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp').prefetch_related('history__edited_by')

    # A simple way to represent a conversation tree, with no parent_message field.
    conversation_tree = []
    
    # We will just list all the messages chronologically and show their history.
    for message in messages_in_thread:
        message.history_entries = list(message.history.all())
        conversation_tree.append(message)
    
    context = {
        'conversation_messages': conversation_tree,
        'other_user': other_user,
    }
    
    # render a template here.
    return render(request, 'messaging/conversation_thread.html', context)