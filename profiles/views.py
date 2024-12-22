from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm
from checkout.models import Order

@login_required
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
        else:
            messages.error(request, 'Update failed, please ensure the form is valid!')
    else:
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


def order_history(request, order_number):
    """
    View to display the order history for a specific order.

    Args:
        request: The HTTP request object.
        order_number: The unique identifier for the order.

    Returns:
        HttpResponse: Renders the checkout success template with order details.
    """
    # Retrieve the order using the provided order number.
    # If the order doesn't exist, return a 404 error.
    order = get_object_or_404(Order, order_number=order_number)

    # Add an informational message to notify the user about the order confirmation.
    # The message includes the order number and mentions that a confirmation email was sent.
    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    # Specify the template to render. In this case, it's the checkout success page.
    template = 'checkout/checkout_success.html'

    # Prepare the context data to pass to the template.
    # The `order` contains the order details to display, 
    # and `from_profile` indicates that this view is being accessed from the user profile.
    context = {
        'order': order,
        'from_profile': True,
    }

    # Render the template with the provided context and return the response.
    return render(request, template, context)


