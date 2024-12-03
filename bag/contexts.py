from decimal import Decimal  # Importing Decimal for precise arithmetic operations
from django.conf import settings  # Importing settings to access project-wide configuration values
from django.shortcuts import get_object_or_404
from products.models import Product

# Function to calculate the contents and totals of the shopping bag
def bag_contents(request):

    bag_items = []  # List to hold items in the shopping bag
    total = 0  # Total price of all items in the bag
    product_count = 0  # Total count of products in the bag
    # Retrieve the current shopping bag from the user's session. 
    # If no bag exists in the session, initialize it as an empty dictionary.
    bag = request.session.get('bag', {})

    # Iterate through each item in the shopping bag.
    # `bag.items()` returns a list of key-value pairs where the key is the item ID, and the value is the quantity.
    for item_id, quantity in bag.items():
        # Fetch the product object from the database using the item ID.
        # If the product with the given primary key (pk) does not exist, raise a 404 error.
        product = get_object_or_404(Product, pk=item_id)
    
        # Calculate the total cost by multiplying the product's price by the quantity and adding it to the running total.
        total += quantity * product.price
    
        # Increment the total product count with the quantity of this item.
        product_count += quantity
    
        # Append a dictionary with details of the current item to the `bag_items` list.
        # This includes:
        # - `item_id`: The unique identifier for the product.
        # - `quantity`: The number of units of the product in the bag.
        # - `product`: The full product object fetched from the database.
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
        })

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
