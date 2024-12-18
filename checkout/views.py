from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from bag.contexts import bag_contents  # Importing the function to get the bag contents
from .forms import OrderForm  # Importing the OrderForm to handle the checkout form
from products.models import Product  # Importing the Product model to manage product data
from .models import OrderLineItem, Order  # Importing the Order and OrderLineItem model to handle order details
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
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
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
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
         # Attempt to prefill the form with any info the user maintains in their profile
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
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
    Handle successful checkouts.

    Args:
        request: The HTTP request object.
        order_number: The unique identifier for the order.

    Returns:
        HttpResponse: Renders the checkout success template with the order details.
    """
    # Retrieve the 'save_info' flag from the session, which determines if user info should be saved.
    save_info = request.session.get('save_info')

    # Get the order using the provided order number.
    # If the order doesn't exist, return a 404 error.
    order = get_object_or_404(Order, order_number=order_number)

    # If the user is logged in, associate their profile with the order.
    if request.user.is_authenticated:
        # Retrieve the user's profile.
        profile = UserProfile.objects.get(user=request.user)

        # Attach the user's profile to the order and save the order.
        order.user_profile = profile
        order.save()

        # If the 'save_info' flag is set, update the user's profile with the order details.
        if save_info:
            # Prepare the profile data using the order's delivery information.
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            # Use a form to validate and save the profile data.
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    # Display a success message to the user, including the order number and email address.
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    # Clear the shopping bag from the session as the checkout process is complete.
    if 'bag' in request.session:
        del request.session['bag']

    # Define the template for displaying the checkout success page.
    template = 'checkout/checkout_success.html'

    # Prepare the context data, including the order, to pass to the template.
    context = {
        'order': order,
    }

    # Render the template with the context and return the response.
    return render(request, template, context)

