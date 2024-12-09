import uuid
from django.db import models
from django.conf import settings
from django.db.models import Sum
from products.models import Product


from django.db import models
from django.conf import settings
from django.db.models import Sum
import uuid


class Order(models.Model):
    """
    Model to represent a customer's order. Includes customer details, order totals,
    and other necessary information for processing an order.
    """
    # Unique order number, automatically generated and not editable
    order_number = models.CharField(max_length=32, null=False, editable=False)

    # Customer's full name
    full_name = models.CharField(max_length=50, null=False, blank=False)

    # Customer's email address
    email = models.EmailField(max_length=254, null=False, blank=False)

    # Customer's phone number
    phone_number = models.CharField(max_length=20, null=False, blank=False)

    # Customer's country
    country = models.CharField(max_length=40, null=False, blank=False)

    # Customer's postal code, optional
    postcode = models.CharField(max_length=20, null=True, blank=True)

    # Customer's town or city
    town_or_city = models.CharField(max_length=40, null=False, blank=False)

    # Customer's primary street address
    street_address1 = models.CharField(max_length=80, null=False, blank=False)

    # Customer's secondary street address, optional
    street_address2 = models.CharField(max_length=80, null=True, blank=True)

    # Customer's county, optional
    county = models.CharField(max_length=80, null=True, blank=True)

    # Date and time the order was created
    date = models.DateTimeField(auto_now_add=True)

    # Delivery cost for the order
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)

    # Total cost of the items in the order (excluding delivery)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

    # Final total cost including delivery
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID.
        Ensures each order has a unique identifier.
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Recalculate the grand total whenever a line item is added or modified.
        Includes the logic for delivery cost based on a free delivery threshold.
        """
        # Calculate the total of all line items in the order
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0

        # Determine the delivery cost based on the total
        if self.order_total < settings.MIN_ORDER_FOR_FREE_DELIVERY:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0

        # Update the grand total
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the default save method to ensure the order number is generated
        the first time the order is saved.
        """
        if not self.order_number:
            # Generate and assign an order number if it's not already set
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        String representation of the order, using its order number.
        """
        return self.order_number


class OrderLineItem(models.Model):
    """
    Model to represent individual items in an order.
    Stores details about the product, its quantity, and the total cost for that item.
    """
    # Reference to the associated order
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')

    # Reference to the product being ordered
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)

    # Size of the product (if applicable, e.g., XS, S, M, L, XL)
    product_size = models.CharField(max_length=2, null=True, blank=True)

    # Quantity of the product being ordered
    quantity = models.IntegerField(null=False, blank=False, default=0)

    # Total cost for this line item (price * quantity), automatically calculated
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the default save method to calculate the line item total
        and update the associated order's total.
        """
        # Calculate the total cost for this line item
        self.lineitem_total = self.product.price * self.quantity

        # Save the line item
        super().save(*args, **kwargs)

        # Update the order's total after saving this line item
        self.order.update_total()

    def __str__(self):
        """
        String representation of the line item, including product SKU and order number.
        """
        return f'SKU {self.product.sku} on order {self.order.order_number}'


