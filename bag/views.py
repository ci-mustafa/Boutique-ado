from django.shortcuts import render, redirect

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


    # Update the shopping bag in the session with the new bag contents
    request.session['bag'] = bag

    # Print the updated shopping bag to the console (useful for debugging)
    print(request.session['bag'])

    # Redirect the user back to the provided URL
    return redirect(redirect_url)

