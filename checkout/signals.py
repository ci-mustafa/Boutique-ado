from django.db.models.signals import post_save, post_delete  # Import signals for save and delete events
from django.dispatch import receiver  # Import receiver to connect signals to specific functions

from .models import OrderLineItem  # Import the OrderLineItem model

# Signal handler for updating the order total when a line item is created or updated
@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update the order's total whenever an OrderLineItem is created or updated.

    Args:
        sender: The model class sending the signal (OrderLineItem in this case).
        instance: The instance of OrderLineItem that triggered the signal.
        created: Boolean indicating if the instance was newly created (True) or updated (False).
        kwargs: Additional keyword arguments passed by the signal.

    Purpose:
        Ensures that any changes to the line item are reflected in the associated order's totals.
    """
    # Call the `update_total` method of the related order to recalculate totals
    instance.order.update_total()


# Signal handler for updating the order total when a line item is deleted
@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update the order's total whenever an OrderLineItem is deleted.

    Args:
        sender: The model class sending the signal (OrderLineItem in this case).
        instance: The instance of OrderLineItem that triggered the signal.
        kwargs: Additional keyword arguments passed by the signal.

    Purpose:
        Ensures that removing a line item updates the associated order's totals correctly.
    """
    # Call the `update_total` method of the related order to recalculate totals
    instance.order.update_total()
