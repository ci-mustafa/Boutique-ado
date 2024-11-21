from django.shortcuts import render, get_object_or_404
from . import models

# Create your views here.

def all_products(request):
    """ A view to list all products including sorting and search quries """
    products = models.Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'products/products.html', context=context)


def product_detail(request, pk):
    """ A view to show product details """
    product = get_object_or_404(models.Product, pk=pk)
    context = {
        'product': product
    }
    return render(request, 'products/product_detail.html', context=context)

