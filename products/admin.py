from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'friendly_name']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'description', 'price', 'rating', 'image', 'category__name']
