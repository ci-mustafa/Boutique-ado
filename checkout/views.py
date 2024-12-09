from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm


def checkout(request):
    """
    Handle the checkout process, including validating the shopping bag
    and rendering the checkout page with an order form.
    """
    # Retrieve the shopping bag from the session
    bag = request.session.get('bag', {})
    
    # Check if the bag is empty
    if not bag:
        # Display an error message to the user if the bag is empty
        messages.error(request, "There is nothing in your bag at the moment!")
        # Redirect the user to the 'all-products' page if the bag is empty
        return redirect(reverse('all-products'))
    
    # Create a blank instance of the order form
    order_form = OrderForm()
    
    # Specify the template to render
    template = "checkout/checkout.html"
    
    # Context data to pass to the template
    context = {
        'order_form': order_form  # Include the order form in the context
    }
    
    # Render the checkout template with the provided context
    return render(request, template, context)

    
