from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from bag.contexts import bag_contents  # Importing the function to get the bag contents
from .forms import OrderForm  # Importing the OrderForm to handle the checkout form
from products.models import Product  # Importing the Product model to manage product data
from .models import OrderLineItem, Order  # Importing the Order and OrderLineItem model to handle order details
import stripe
import json


@require_POST
def cache_checkout_data(request):
    """
    A view to cache checkout data in Stripe's PaymentIntent metadata.

    Args:
        request (HttpRequest): The HTTP request object containing the data sent by the client.

    Returns:
        HttpResponse: A response indicating success or failure of the operation.
    """
    try:
        # Retrieve the PaymentIntent ID from the client_secret sent in the POST data.
        # The client_secret format is: <payment_intent_id>_secret_<unique_key>
        # Extract only the PaymentIntent ID (everything before "_secret").
        pid = request.POST.get('client_secret').split('_secret')[0]

        # Set the Stripe API key to authenticate requests to Stripe.
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Modify the PaymentIntent's metadata with additional details.
        stripe.PaymentIntent.modify(
            pid,
            metadata={
                # Save the contents of the user's shopping bag (session data) as JSON.
                'bag': json.dumps(request.session.get('bag', {})),

                # Save whether the user wants their payment information saved.
                'save_info': request.POST.get('save_info'),

                # Store the username of the user making the request.
                # If the user is not logged in, this will likely be an empty string.
                'username': request.user,
            }
        )
        # Return a 200 OK response indicating the data was successfully cached.
        return HttpResponse(status=200)

    except Exception as e:
        # Handle any exceptions that occur during the process.
        
        # Display an error message to the user. This can be shown in the frontend using Django's messages framework.
        messages.error(
            request,
            'Sorry, your payment cannot be processed right now. Please try again later.'
        )

        # Return a 400 Bad Request response with the exception details for debugging.
        return HttpResponse(content=e, status=400)



def checkout(request):
    """
    Handle the checkout process, including:
    - Validating the shopping bag
    - Creating a Stripe payment intent
    - Rendering the checkout page with an order form
    """
    # Retrieve Stripe public and secret keys from settings
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        # Retrieve the shopping bag from the session
        bag = request.session.get('bag', {})
        # Collect form data from the POST request
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # Create an OrderForm instance with the submitted data
        order_form = OrderForm(form_data)
        if order_form.is_valid():  # Check if the form is valid
            order = order_form.save()  # Save the form to create an order instance
            # Loop through each item in the shopping bag
            for item_id, item_data in bag.items():
                try:
                    # Get the product instance for the item
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):  # If the item has no size variations
                        # Create an OrderLineItem instance
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()  # Save the line item to the database
                    else:  # If the item has size variations
                        for size, quantity in item_data['items_by_size'].items():
                            # Create OrderLineItem for each size
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()  # Save the line item
                except Product.DoesNotExist:  # Handle the case where the product is not found
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()  # Delete the order if there are issues
                    return redirect(reverse('view_bag'))  # Redirect back to the bag page
            # Save user preference to save info in the session
            request.session['save_info'] = 'save-info' in request.POST
            # Redirect to the checkout success page with the order number
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            # Show an error message if the form is invalid
            messages.error(request, 'There was an error with your form. \
                Please double-check your information.')
    else:
        # Retrieve the shopping bag from the session
        bag = request.session.get('bag', {})
        
        # Check if the bag is empty
        if not bag:
            # Display an error message if the bag is empty
            messages.error(request, "There is nothing in your bag at the moment!")
            return redirect(reverse('all-products'))  # Redirect to the 'all-products' page

        # Get the bag contents and calculate totals
        current_bag = bag_contents(request)  # Use the bag_contents context processor
        total = current_bag['grand_total']  # Get the grand total from the bag contents
        stripe_total = round(total * 100)  # Convert total to cents for Stripe (Stripe requires amounts in cents)

        # Set the Stripe secret key to create the payment intent
        stripe.api_key = stripe_secret_key

        # Create a Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,  # Total amount in cents
            currency=settings.STRIPE_CURRENCY  # Currency (e.g., "eur")
        )

        # Create a new, blank OrderForm for the user to fill out
        order_form = OrderForm()

    # Warn the user if the Stripe public key is missing
    if not stripe_public_key:
        messages.warning(request, "Stripe public key is missing. "
            "Did you forget to set it in your environment?")

    # Specify the template to render
    template = "checkout/checkout.html"

    # Context data to pass to the template
    context = {
        'order_form': order_form,  # Pass the order form
        'stripe_public_key': stripe_public_key,  # Pass the Stripe public key for the frontend
        'client_secret': intent.client_secret,  # Pass the client secret from the payment intent
    }

    # Render the checkout template with the context data
    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts:
    - Display a success message to the user
    - Remove the shopping bag from the session
    - Render the checkout success page
    """

    # Retrieve the user's save info preference from the session (if available)
    save_info = request.session.get('save_info')

    # Get the order using the order number or return a 404 error if not found
    order = get_object_or_404(Order, order_number=order_number)

    # Display a success message with the order details
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    # Remove the shopping bag from the session as the order is completed
    if 'bag' in request.session:
        del request.session['bag']

    # Define the template to use for the checkout success page
    template = 'checkout/checkout_success.html'

    # Define the context to pass to the template
    context = {
        'order': order,  # Include the order details for the success page
    }

    # Render the checkout success template with the provided context
    return render(request, template, context)
