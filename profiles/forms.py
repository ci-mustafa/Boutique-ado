from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    """
    A form for the UserProfile model to handle updating user profile details.
    """
    class Meta:
        # Specify the model to base the form on and exclude the 'user' field
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        """
        Customize the form initialization to add placeholders, 
        CSS classes, remove auto-generated labels, 
        and set autofocus on the first field.
        """
        super().__init__(*args, **kwargs)
        
        # Placeholder text for each field in the form
        placeholders = {
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
        }

        # Set autofocus on the 'default_phone_number' field
        self.fields['default_phone_number'].widget.attrs['autofocus'] = True

        # Iterate through each field in the form
        for field in self.fields:
            # Skip the 'default_country' field for placeholder customization
            if field != 'default_country':
                # Add an asterisk to required fields in the placeholder
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                
                # Set the placeholder attribute for the field's widget
                self.fields[field].widget.attrs['placeholder'] = placeholder

            # Add a CSS class to all fields for consistent styling
            self.fields[field].widget.attrs['class'] = 'border-black rounded-0 profile-form-input'
            
            # Remove the default label for all fields to rely on placeholders instead
            self.fields[field].label = False
