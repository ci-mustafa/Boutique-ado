/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS styling guidelines and examples from here: 
    https://stripe.com/docs/stripe-js
*/

// Retrieve the Stripe public key and client secret from the template
// These values are rendered as hidden elements in the template
var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1); 
var client_secret = $('#id_client_secret').text().slice(1, -1);

// Initialize Stripe with the public key
var stripe = Stripe(stripe_public_key);

// Create an instance of Stripe Elements to manage UI components for the payment form
var elements = stripe.elements();

// Define the style object to customize the appearance of the Stripe Elements card input
var style = {
    base: {
        color: '#000', // Text color for valid input
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif', // Font style
        fontSmoothing: 'antialiased', // Smooth font rendering
        fontSize: '16px', // Base font size
        '::placeholder': {
            color: '#aab7c4' // Placeholder text color
        }
    },
    invalid: {
        color: '#dc3545', // Text color for invalid input
        iconColor: '#dc3545' // Icon color for invalid input
    }
};

// Create a Stripe Elements card component with the specified style
var card = elements.create('card', {style: style});

// Mount the card component into the DOM at the specified element
card.mount('#card-element');
