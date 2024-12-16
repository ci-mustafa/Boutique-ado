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
            content=f'Unhandled Webhook received: {event["type"]}',  # Include the event type in the response
            status=200  # Send a 200 OK status to indicate successful receipt
        )
    
    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe.
        
        This method is triggered when a payment intent is successfully processed by Stripe.
        It acknowledges the event and can be extended to handle actions like updating order statuses,
        sending confirmation emails, or logging payment details.

        Args:
            event (dict): A dictionary containing details about the webhook event from Stripe.
                        Includes information like event type, payment intent data, etc.
        
        Returns:
            HttpResponse: A response acknowledging receipt of the webhook, with the event type included in the content.
        """
        # Log the event type in the response content for debugging or auditing purposes
        # The `event["type"]` specifies the exact type of webhook event received (e.g., payment_intent.succeeded).
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',  # Include the event type in the response for transparency
            status=200  # Send a 200 OK status to Stripe, signaling that the webhook was received successfully
        )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe.

        This method is triggered when a payment intent fails (e.g., due to insufficient funds, invalid card, etc.).
        It acknowledges the event and can be extended to handle actions like notifying the user,
        logging the failure for debugging, or updating order statuses.

        Args:
            event (dict): A dictionary containing details about the webhook event from Stripe.
                        Includes information like event type, payment intent data, error message, etc.
        
        Returns:
            HttpResponse: A response acknowledging receipt of the webhook, with the event type included in the content.
        """
        # Log the event type in the response content for transparency and debugging.
        # The `event["type"]` indicates the type of event received (e.g., payment_intent.payment_failed).
        # You can use this value for logging or triggering specific workflows.

        # Note: This is where you might log payment failure details or notify the customer about the failed transaction.
        # Example extensions (not included here):
        # - Extract details from `event` to find the reason for failure.
        # - Send an email to the customer with details of the failure.
        # - Update the order status in your database to "Payment Failed."
    
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',  # Include the event type for transparency in the response
            status=200  # Send a 200 OK status to Stripe, indicating successful receipt of the webhook
        )


