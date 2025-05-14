const express = require('express');
const cors = require('cors');
const Stripe = require('stripe');

const app = express();
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

app.use(cors());
app.use(express.json());

app.post('/create-checkout-session', async (req, res) => {
  const { amount, customer_name, items, weight, dimensions, distance, inside, stairs } = req.body;

  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [{
      price_data: {
        currency: 'usd',
        unit_amount: amount,
        product_data: {
          name: 'Keenway Delivery',
          description: `Items: ${items}, Weight: ${weight} lbs, Distance: ${distance} mi`
        }
      },
      quantity: 1
    }],
    mode: 'payment',
    success_url: 'https://www.gokeenway.com/success',
    cancel_url: 'https://www.gokeenway.com/cancel'
  });

  res.json({ id: session.id });
});

const PORT = process.env.PORT || 4242;
app.listen(PORT, () => console.log(`✅ Server running on ${PORT}`));
