from django.urls import path
from . import views


urlpatterns = [
    path('', views.all_products, name = 'all-products'),
    path('<int:pk>/', views.product_detail, name='product-detail'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product')
]