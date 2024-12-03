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
    
    # Retrieve the current shopping bag from the session, or an empty dictionary if not present
    bag = request.session.get('bag', {})

    # If the item already exists in the shopping bag, increment its quantity
    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    else:
        # If the item is not in the bag, add it with the specified quantity
        bag[item_id] = quantity

    # Update the shopping bag in the session with the new bag contents
    request.session['bag'] = bag

    # Print the updated shopping bag to the console (useful for debugging)
    print(request.session['bag'])

    # Redirect the user back to the provided URL
    return redirect(redirect_url)

