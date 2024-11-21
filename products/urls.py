from django.urls import path
from . import views


urlpatterns = [
    path('', views.all_products, name = 'all-products'),
    path('<int:pk>', views.product_detail, name='product-detail'),
]