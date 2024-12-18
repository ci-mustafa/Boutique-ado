from .models import UserProfile
from .forms import UserProfileForm
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

def profile(request):
    """
    Display and handle updates to the user's profile.
    
    This view retrieves the user's profile, displays their information,
    and allows updates to their profile through a form.
    """
    # Get the user's profile or return a 404 error if not found
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        # If the request is a POST, create a form instance with the submitted data
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # Save the form data to update the user's profile
            form.save()
            # Add a success message to be displayed on the frontend
            messages.success(request, 'Profile updated successfully')

    # For GET requests or after a successful POST, initialize the form with the user's profile instance
    form = UserProfileForm(instance=profile)
    # Retrieve all orders associated with the user's profile
    orders = profile.orders.all()

    # Define the template to be used for rendering the profile page
    template = 'profiles/profile.html'
    # Pass the form, orders, and a flag indicating the current page to the template context
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True  # This can be used to conditionally render elements in the template
    }

    # Render the profile page with the provided template and context
    return render(request, template, context)

