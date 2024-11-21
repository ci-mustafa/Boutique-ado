from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db.models import Q
from . import models

# Create your views here.

def all_products(request):
    """ A view to list all products including sorting and search quries """
    products = models.Product.objects.all()
    query = None
    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, 'You did not enter any search criteria!')
                return redirect(reverse('all-products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    context = {
        'products': products,
        'search_term': query
    }
    return render(request, 'products/products.html', context=context)


def product_detail(request, pk):
    """ A view to show product details """
    product = get_object_or_404(models.Product, pk=pk)
    context = {
        'product': product
    }
    return render(request, 'products/product_detail.html', context=context)

