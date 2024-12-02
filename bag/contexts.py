from decimal import Decimal  # Importing Decimal for precise arithmetic operations
from django.conf import settings  # Importing settings to access project-wide configuration values

# Function to calculate the contents and totals of the shopping bag
def bag_contents(request):

    bag_items = []  # List to hold items in the shopping bag
    total = 0  # Total price of all items in the bag
    product_count = 0  # Total count of products in the bag

    # Check if the total is below the free delivery threshold
    if total < settings.MIN_ORDER_FOR_FREE_DELIVERY:
        # Calculate delivery cost as a percentage of the total
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        # Calculate the remaining amount required to qualify for free delivery
        free_delivery_delta = settings.MIN_ORDER_FOR_FREE_DELIVERY - total
    else:
        # No delivery charge if the total meets or exceeds the free delivery threshold
        delivery = 0
        # No remaining amount needed for free delivery
        free_delivery_delta = 0

    # Calculate the grand total, including delivery charges
    grand_total = delivery + total

    # Context dictionary to pass bag details to templates
    context = {
        'bag_items': bag_items,  # List of bag items
        'total': total,  # Total cost of items in the bag
        'product_count': product_count,  # Total count of products in the bag
        'delivery': delivery,  # Calculated delivery cost
        'free_delivery_delta': free_delivery_delta,  # Remaining amount for free delivery
        'free_delivery_threshold': settings.MIN_ORDER_FOR_FREE_DELIVERY,  # Free delivery threshold value
        'grand_total': grand_total,  # Final total including delivery charges
    }

    # Return the context dictionary for use in templates
    return context
