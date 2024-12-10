from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings
import stripe
from bag.contexts import bag_contents  # Importing the function to get the bag contents
from .forms import OrderForm  # Importing the OrderForm to handle checkout form

def checkout(request):
    """
    Handle the checkout process, including validating the shopping bag,
    creating a Stripe payment intent, and rendering the checkout page with an order form.
    """
    # Retrieve Stripe public and secret keys from settings
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Retrieve the shopping bag from the session
    bag = request.session.get('bag', {})
    
    # Check if the bag is empty
    if not bag:
        # If the bag is empty, display an error message to the user
        messages.error(request, "There is nothing in your bag at the moment!")
        # Redirect the user to the 'all-products' page
        return redirect(reverse('all-products'))
    
    # Retrieve the current bag contents and calculate totals
    current_bag = bag_contents(request)  # Get the bag's contents using the bag_contents context processor
    total = current_bag['grand_total']  # Get the grand total from the bag contents
    stripe_total = round(total * 100)  # Convert the total to cents (Stripe requires amounts in cents)

    # Set the Stripe secret key for API interaction
    stripe.api_key = stripe_secret_key

    # Create a Stripe payment intent to handle the payment
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,  # Total amount for the payment in cents
        currency=settings.STRIPE_CURRENCY  # Currency to use for the payment (e.g., "eur")
    )

    # Create a new, blank instance of the order form for the user to fill out
    order_form = OrderForm()

    # Warning message if forget to set stripe public key
    if not stripe_public_key:
        messages.warning(request, "Stripe public key is missing."\
            "did you forget to set it in your environment?")
    
    # Specify the template to render
    template = "checkout/checkout.html"
    
    # Context data to pass to the template
    context = {
        'order_form': order_form,  # Pass the order form to the template
        'stripe_public_key': stripe_public_key,  # Pass the Stripe public key for the frontend
        'client_secret': intent.client_secret,  # Pass the client secret from the payment intent
    }
    
    # Render the checkout template with the provided context
    return render(request, template, context)


    
