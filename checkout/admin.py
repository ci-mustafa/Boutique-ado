from django.contrib import admin
from .models import Order, OrderLineItem

# Define an inline admin class to manage OrderLineItems within the Order admin interface
class OrderLineItemAdminInline(admin.TabularInline):
    """
    Inline admin class for OrderLineItem.
    Allows line items to be managed directly within the Order admin interface.
    """
    model = OrderLineItem  # Specifies the associated model
    readonly_fields = ('lineitem_total',)  # Makes the lineitem_total field read-only


# Register the Order model in the admin interface with a custom admin class
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Order model.
    Configures how orders are displayed and managed in the Django admin interface.
    """

    # Add the OrderLineItem inline to the Order admin
    inlines = (OrderLineItemAdminInline,)

    # Fields to be displayed as read-only in the admin form
    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total', 'original_bag', 'stripe_pid')

    # The order and grouping of fields in the admin form
    fields = ('order_number', 'user_profile','date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total', 'original_bag', 'stripe_pid')

    # Columns to be displayed in the list view of the admin panel
    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total',)

    # Default ordering for the list view, newest orders first
    ordering = ('-date',)

