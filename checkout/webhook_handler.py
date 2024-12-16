from django.http import HttpResponse
from .models import Order, OrderLineItem
from products.models import Product

import json
import time
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
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        # Get the Charge object
        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )

        billing_details = stripe_charge.billing_details
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)
        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
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


