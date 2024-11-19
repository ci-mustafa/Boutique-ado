from django.shortcuts import render

# Create your views here.

def index(request):
    """ A view for home page """
    return render(request, 'home/home.html')
