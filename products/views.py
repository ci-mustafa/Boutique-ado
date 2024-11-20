from django.shortcuts import render
from . import models

# Create your views here.

def all_products(request):
    """ A view to list all products including sorting and search quries """
    products = models.Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'products/products.html', context=context)