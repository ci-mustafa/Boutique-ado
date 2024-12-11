/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// Retrieve the Stripe public key and client secret from hidden HTML elements
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1); // Extract and clean the public key
var clientSecret = $('#id_client_secret').text().slice(1, -1); // Extract and clean the client secret

// Initialize Stripe using the public key
var stripe = Stripe(stripePublicKey);

// Initialize Stripe Elements
var elements = stripe.elements();

// Define the style for the Stripe card element
var style = {
    base: {
        color: '#000', // Set base text color to black
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif', // Use Helvetica font family
        fontSmoothing: 'antialiased', // Enable font smoothing for better readability
        fontSize: '16px', // Set base font size
        '::placeholder': {
            color: '#aab7c4' // Set placeholder text color
        }
    },
    invalid: {
        color: '#dc3545', // Set text color for invalid input to red
        iconColor: '#dc3545' // Set icon color for invalid input to red
    }
};

// Create the Stripe card element with the defined style
var card = elements.create('card', { style: style });

// Mount the card element to the DOM element with ID 'card-element'
card.mount('#card-element');

// Handle real-time validation errors on the card element
card.addEventListener('change', function (event) {
    // Get the error display element
    var errorDiv = document.getElementById('card-errors');
    
    if (event.error) {
        // If there's an error, display it in the errorDiv
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i> <!-- Error icon -->
            </span>
            <span>${event.error.message}</span> <!-- Error message -->
        `;
        $(errorDiv).html(html); // Update the HTML content of errorDiv with the error message
    } else {
        // Clear the errorDiv if there are no errors
        errorDiv.textContent = '';
    }
});

// Get the payment form element
var form = document.getElementById('payment-form');

// Add a submit event listener to handle form submission
form.addEventListener('submit', function(ev) {
    ev.preventDefault(); // Prevent the default form submission

    // Disable the card element and the submit button to prevent multiple submissions
    card.update({ 'disabled': true });
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);
    // Confirm the card payment using the client secret
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card, // Pass the card element as the payment method
        }
    }).then(function(result) {
        if (result.error) {
            // If there's an error during the payment process, display it in the errorDiv
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i> <!-- Error icon -->
                </span>
                <span>${result.error.message}</span> <!-- Error message -->
            `;
            $(errorDiv).html(html); // Update the HTML content of errorDiv with the error message
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
            // Re-enable the card element and the submit button
            card.update({ 'disabled': false });
            $('#submit-button').attr('disabled', false);
        } else {
            // If the payment is successful
            if (result.paymentIntent.status === 'succeeded') {
                form.submit(); // Submit the form to the server
            }
        }
    });
});
