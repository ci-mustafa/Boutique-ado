from django.shortcuts import render

# Create your views here.

def view_bag(request):
    """ A view to show bag content """
    return render(request, 'bag/bag.html')
