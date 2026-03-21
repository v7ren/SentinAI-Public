const Stripe = require('stripe');
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '');

async function createCustomer(email, name) {
  const customer = await stripe.customers.create({ email, name });
  return customer.id;
}

async function createCheckoutSession(customerId, priceId, successUrl, cancelUrl) {
  const session = await stripe.checkout.sessions.create({
    customer: customerId,
    mode: 'subscription',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: successUrl,
    cancel_url: cancelUrl,
  });
  return session;
}

async function createBillingPortalSession(customerId, returnUrl) {
  return stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: returnUrl,
  });
}

function constructEvent(payload, signature, secret) {
  return stripe.webhooks.constructEvent(payload, signature, secret);
}

module.exports = {
  createCustomer,
  createCheckoutSession,
  createBillingPortalSession,
  constructEvent,
};
