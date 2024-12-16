from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .webhook_handler import StripeWH_Handler

import stripe 


@require_POST  # Ensures this view only accepts POST requests
@csrf_exempt  # Disables CSRF protection since Stripe webhooks won't include CSRF tokens
def webhook(request):
    """
    Listen for webhooks from Stripe.

    Stripe sends webhook events (e.g., payment succeeded, payment failed) to this endpoint.
    This view verifies the webhook's authenticity and routes it to the appropriate handler function.
    """

    # Setup: Retrieve the webhook secret and API key from Django settings
    wh_secret = settings.STRIPE_WH_SECRET  # Webhook secret for verifying event signatures
    stripe.api_key = settings.STRIPE_SECRET_KEY  # Secret key to interact with Stripe's API

    # Get the raw webhook payload and the Stripe signature header
    payload = request.body  # Raw body of the webhook request
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']  # Signature header from Stripe
    event = None  # Initialize the event variable

    # Verify the webhook's signature and construct the event object
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:
        # If the payload is invalid, return a 400 Bad Request response
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # If the signature verification fails, return a 400 Bad Request response
        return HttpResponse(status=400)
    except Exception as e:
        # Catch-all for any other errors; return the error message with a 400 status
        return HttpResponse(content=e, status=400)

    # Set up a webhook handler instance
    handler = StripeWH_Handler(request)  # Custom handler class to manage Stripe events

    # Map Stripe event types to the appropriate handler functions
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,  # Handle successful payments
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,  # Handle failed payments
    }

    # Get the type of the Stripe event (e.g., 'payment_intent.succeeded')
    event_type = event['type']

    # Retrieve the appropriate handler from the map, or use a generic handler as a fallback
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler and pass the event data to it
    response = event_handler(event)

    # Return the handler's response
    return response

    
