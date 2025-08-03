from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout
from django.contrib import messages

# This view will be responsible for user account deletion.
# It is protected by @login_required to ensure only authenticated users can access it.
@login_required
def delete_user(request):
    """
    View to handle the deletion of a user's account.

    This view is triggered by a POST request.
    When a user deletes their account, it also triggers the post_delete signal
    on the User model, which will clean up related data.
    """
    if request.method == 'POST':
        # Get the currently logged-in user.
        user = request.user
        
        # Log the user out before deleting the account.
        logout(request)
        
        # Delete the user account.
        # This action will fire the post_delete signal on the User model.
        user.delete()

        # Add a success message for the user.
        messages.success(request, 'Your account has been successfully deleted.')
        
        # Redirect to a a safe page after deletion.
        return redirect('home')  # Assuming a 'home' URL name exists.
    
    # If the request is not a POST, show a confirmation page.
    # A simple HTML template would be rendered here for confirmation.
    return HttpResponse("Are you sure you want to delete your account? This action is irreversible.", status=200)
