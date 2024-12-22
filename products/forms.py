from django import forms  # Import Django forms for creating form classes
from .models import Product, Category  # Import the Product and Category models

# Define a form for the Product model
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product  # Specify the model to use for this form
        fields = '__all__'  # Include all fields from the Product model in the form

    def __init__(self, *args, **kwargs):
        """
        Initialize the form, customize the category field's choices,
        and apply a consistent style to all form fields.
        """
        super().__init__(*args, **kwargs)  # Call the parent class's initializer

        # Get all category objects from the database
        categories = Category.objects.all()

        # Create a list of tuples (id, friendly_name) for dropdown options
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        # Set the choices for the 'category' field using the friendly names
        self.fields['category'].choices = friendly_names

        # Iterate through all fields in the form
        for field_name, field in self.fields.items():
            # Add consistent styling to each field's widget
            field.widget.attrs['class'] = 'border-black rounded-0'
