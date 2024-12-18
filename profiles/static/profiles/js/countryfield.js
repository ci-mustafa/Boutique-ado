// Get the initial value of the country dropdown field
let countrySelected = $('#id_default_country').val();

// Check if a country is selected on page load
if (!countrySelected) {
    // If no country is selected, set the text color to a light grey
    $('#id_default_country').css('color', '#aab7c4');
}

// Attach an event listener to detect changes in the dropdown field
$('#id_default_country').change(function() {
    // Get the currently selected value in the dropdown
    countrySelected = $(this).val();
    
    // Check if a country is selected
    if (!countrySelected) {
        // If no country is selected, set the text color to light grey
        $(this).css('color', '#aab7c4');
    } else {
        // If a country is selected, set the text color to black
        $(this).css('color', '#000');
    }
});
