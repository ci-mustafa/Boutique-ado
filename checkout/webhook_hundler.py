from django.http import HttpResponse

class StripeWH_Handler:
    """
    A class to handle Stripe webhooks.
    Webhooks are notifications sent by Stripe to your application
    when specific events occur, like a successful payment.
    """

    def __init__(self, request):
        """
        Initialize the handler with the HTTP request.
        
        Args:
            request: The HTTP request containing the webhook data from Stripe.
        """
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic, unknown, or unexpected webhook event.
        
        This is a fallback method to handle events that are not explicitly defined.
        
        Args:
            event (dict): A dictionary containing details about the webhook event from Stripe.
        
        Returns:
            HttpResponse: A response acknowledging receipt of the webhook, with the event type included in the content.
        """
        # Log the event type in the response content and send a status 200 (OK) response
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',  # Include the event type in the response
            status=200  # Send a 200 OK status to indicate successful receipt
        )
