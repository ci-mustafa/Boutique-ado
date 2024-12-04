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
    for item_id, item_data in bag.items():
        # Check if the item data is a simple integer (for non-sized products).
        if isinstance(item_data, int):
            # Retrieve the product from the database using the item_id.
            product = get_object_or_404(Product, pk=item_id)
            # Update the total cost with the product's price multiplied by its quantity.
            total += item_data * product.price
            # Update the total product count with the quantity of this product.
            product_count += item_data
            # Append the product details to the bag items list for display.
            bag_items.append({
                'item_id': item_id,  # Unique identifier for the product.
                'quantity': item_data,  # Quantity of the product.
                'product': product,  # Product object for reference.
            })
        else:
            # Handle products with size variants (item_data is a dictionary in this case).
            product = get_object_or_404(Product, pk=item_id)
            # Iterate through each size and its quantity in the item's data.
            for size, quantity in item_data['items_by_size'].items():
                # Update the total cost with the price of the product multiplied by the quantity.
                total += quantity * product.price
                # Update the total product count with the quantity for this size.
                product_count += quantity
                # Append the product details to the bag items list, including size information.
                bag_items.append({
                    'item_id': item_id,  # Unique identifier for the product.
                    'quantity': quantity,  # Quantity of this specific size.
                    'product': product,  # Product object for reference.
                    'size': size,  # Specific size of the product.
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
