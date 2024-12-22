from django.forms.widgets import ClearableFileInput  # Import the ClearableFileInput widget to customize file input fields
from django.utils.translation import gettext_lazy as _  # Import translation function for multi-language support

# Define a custom widget for handling file input fields with additional functionality
class CustomClearableFileInput(ClearableFileInput):
    # Label for the checkbox to remove the current file
    clear_checkbox_label = _('Remove')
    
    # Text displayed next to the currently uploaded file
    initial_text = _('Current Image')
    
    # Placeholder or additional text for the input field (empty string in this case)
    input_text = _('')

    # Path to the custom template that defines the HTML structure for the widget
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'
