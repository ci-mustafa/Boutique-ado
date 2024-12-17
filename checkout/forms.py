from django import forms  # Import Django's forms module for creating forms
from .models import Order  # Import the Order model to base the form on it

# Define the OrderForm class, which is a ModelForm
class OrderForm(forms.ModelForm):
    # Specify the metadata for the form
    class Meta:
        model = Order  # Use the Order model as the base for this form
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)  # Fields to include in the form(required)

    # Override the initialization method to customize the form fields
    def __init__(self, *args, **kwargs):
        """
        Customize the form fields by adding placeholders, CSS classes,
        removing labels, and setting autofocus on the first field.
        """
        super().__init__(*args, **kwargs)  # Call the parent class's initializer

        # Dictionary of placeholder texts for each field
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, state or locality',
        }

        # Set the autofocus attribute on the 'full_name' field
        self.fields['full_name'].widget.attrs['autofocus'] = True

        # Iterate through all the fields in the form
        for field in self.fields:
            if field != 'country':
                # If the field is required, add an asterisk to the placeholder
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]

                # Set the placeholder attribute of the field's widget
                self.fields[field].widget.attrs['placeholder'] = placeholder

            # Add a custom CSS class to the field's widget for styling
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'

            # Remove the auto-generated label by setting it to False
            self.fields[field].label = False
