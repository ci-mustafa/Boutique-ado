/*
    Core logic/payment flow for this comes from:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from:
    https://stripe.com/docs/stripe-js
*/

// Extract public Stripe key and client secret from hidden elements in the HTML
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1); // Remove leading and trailing quotes
var clientSecret = $('#id_client_secret').text().slice(1, -1); // Same for client secret

// Initialize Stripe with the public key
var stripe = Stripe(stripePublicKey);

// Create an instance of Stripe Elements to handle card input
var elements = stripe.elements();

// Define styles for the card element
var style = {
    base: {
        color: '#000', // Text color
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif', // Font family
        fontSmoothing: 'antialiased', // Smooth font rendering
        fontSize: '16px', // Base font size
        '::placeholder': { // Placeholder text color
            color: '#aab7c4'
        }
    },
    invalid: { // Styles for invalid card input
        color: '#dc3545', // Red text for errors
        iconColor: '#dc3545' // Red icon color for errors
    }
};

// Create the card element using the defined style
var card = elements.create('card', {style: style});

// Mount the card element onto the page in the specified HTML container
card.mount('#card-element');

// Handle real-time validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        // If there's an error, display it in the errorDiv
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        // Clear any existing error messages
        errorDiv.textContent = '';
    }
});

// Handle the form submission
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    ev.preventDefault(); // Prevent the default form submission

    // Disable the card element and submit button to prevent multiple submissions
    card.update({ 'disabled': true });
    $('#submit-button').attr('disabled', true);

    // Show the loading spinner and hide the form temporarily
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    // Check if the user wants to save their information for future payments
    var saveInfo = Boolean($('#id-save-info').attr('checked'));

    // Extract the CSRF token from the form for secure POST requests
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // Prepare the data to be sent to the cache_checkout_data endpoint
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };

    // Endpoint to cache checkout data
    var url = '/checkout/cache_checkout_data/';

    // Send the cached data to the server using an AJAX POST request
    $.post(url, postData).done(function () {
        // Once caching is successful, confirm the card payment with Stripe
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card, // Pass the card element as the payment method
                billing_details: { // Include billing details
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address: { // User's billing address
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        state: $.trim(form.county.value),
                    }
                }
            },
            shipping: { // Include shipping details
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    postal_code: $.trim(form.postcode.value),
                    state: $.trim(form.county.value),
                }
            },
        }).then(function(result) {
            if (result.error) {
                // If there's an error, display it in the errorDiv
                var errorDiv = document.getElementById('card-errors');
                var html = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                $(errorDiv).html(html);

                // Re-enable the form and card input in case the user wants to try again
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false });
                $('#submit-button').attr('disabled', false);
            } else {
                // If the payment is successful, submit the form
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function () {
        // If caching fails, reload the page to display Django error messages
        location.reload();
    });
});
