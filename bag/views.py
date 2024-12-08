from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import messages
from products.models import Product

# Create your views here.

def view_bag(request):
    """ A view to show bag content """
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """
    Add a quantity of the specified product to the shopping bag.

    Args:
    - request: The HTTP request object containing data from the user.
    - item_id: The ID of the product to be added to the shopping bag.

    Returns:
    - A redirect to the URL provided in the POST request.
    """

    product = Product.objects.get(pk=item_id)
    # Get the quantity of the product to add from the POST data
    quantity = int(request.POST.get('quantity'))
    
    # Get the URL to redirect to after adding the item
    redirect_url = request.POST.get('redirect_url')

    # Initialize the 'size' variable to None. This will hold the product size if it's provided in the POST request.
    size = None

    # Check if the 'product_size' key exists in the POST request data.
    if 'product_size' in request.POST:
        # If 'product_size' is found in the POST data, retrieve its value and assign it to the 'size' variable.
        size = request.POST['product_size']

    # Retrieve the current shopping bag from the session, or an empty dictionary if not present
    bag = request.session.get('bag', {})

    # Check if a size was provided (e.g., for products with size options).
    if size:
        # If the item already exists in the shopping bag.
        if item_id in list(bag.keys()):
            # Check if the specific size of the item already exists in the bag.
            if size in bag[item_id]['items_by_size'].keys():
                # If the size exists, update the quantity for that size.
                bag[item_id]['items_by_size'][size] += quantity
            else:
                # If the size does not exist, add the size with the provided quantity.
                bag[item_id]['items_by_size'][size] = quantity
        else:
            # If the item does not exist in the bag, add it with the size and quantity information.
            bag[item_id] = {'items_by_size': {size: quantity}}
    else:
        # If no size is provided (e.g., for non-sized products).
        if item_id in list(bag.keys()):
            # If the item already exists in the bag, simply update the quantity.
            bag[item_id] += quantity
        else:
            # If the item does not exist in the bag, add it with the provided quantity.
            bag[item_id] = quantity
            messages.success(request, f"Added {product.name} to your bag.")


    # Update the shopping bag in the session with the new bag contents
    request.session['bag'] = bag

    # Print the updated shopping bag to the console (useful for debugging)
    print(request.session['bag'])

    # Redirect the user back to the provided URL
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """
    Adjust the quantity of the specified product to the specified amount.

    This function updates the shopping bag stored in the session based on user input.
    If the quantity is set to 0, the product is removed from the bag.
    Handles both products with sizes (e.g., clothing) and without sizes.
    """
    
    # Retrieve the new quantity from the POST request
    quantity = int(request.POST.get('quantity'))
    
    # Initialize `size` to None; check if a product size is specified in the POST data
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    
    # Get the current bag (stored in the user's session) or initialize it as an empty dictionary
    bag = request.session.get('bag', {})
    
    # If the product has a size, handle size-specific logic
    if size:
        if quantity > 0:
            # Update the quantity for the specific size of the product
            bag[item_id]['items_by_size'][size] = quantity
        else:
            # If the quantity is 0, remove the size entry for the product
            del bag[item_id]['items_by_size'][size]
            
            # If there are no more sizes for this product, remove the entire product from the bag
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
    else:
        # Handle products without sizes
        if quantity > 0:
            # Update the quantity for the product
            bag[item_id] = quantity
        else:
            # If the quantity is 0, remove the product from the bag
            bag.pop(item_id)
    
    # Save the updated bag back into the session
    request.session['bag'] = bag
    
    # Redirect the user back to the bag view page
    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """
    Remove a specific item or size of an item from the shopping bag.

    If a size is provided in the request, only that specific size of the item
    will be removed. If no size is provided, the entire item will be removed.
    """

    try:
        # Initialize size as None
        size = None

        # Check if a specific size was provided in the POST data
        if 'product_size' in request.POST:
            size = request.POST['product_size']

        # Retrieve the current shopping bag from the session
        bag = request.session.get('bag', {})

        if size:
            # If a size is specified, remove only that size from the item
            del bag[item_id]['items_by_size'][size]

            # If no sizes remain for this item, remove the item completely
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
        else:
            # If no size is specified, remove the entire item from the bag
            bag.pop(item_id)

        # Save the updated shopping bag back into the session
        request.session['bag'] = bag

        # Return a 200 OK response to indicate success
        return HttpResponse(status=200)

    except Exception as e:
        # If an error occurs, return a 500 Internal Server Error response
        return HttpResponse(status=500)




