import os
import stripe
from fastapi import HTTPException
from utils.db import increment_credits

# Initialize Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

def create_checkout_session(dollars: float, success_url: str, cancel_url: str) -> str:
    """
    Create a Stripe Checkout Session to purchase roasts based on dollar amount.

    1 USD buys 10 roasts. Returns the session ID.
    """
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured.")
    try:
        dollars = float(dollars)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid dollar amount")
    if dollars <= 0:
        raise HTTPException(status_code=400, detail="Dollar amount must be greater than 0")
    # Compute roasts and Stripe amount
    roasts = int(dollars * 10)
    amount_cents = int(dollars * 100)
    # Build dynamic price data
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": amount_cents,
                "product_data": {
                    "name": f"{roasts} Roasts",
                    "description": f"Be the good guy. Buy {roasts} roasts for ${dollars:.2f}"
                }
            },
            "quantity": 1
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"roasts": roasts}
    )
    return session.id

def process_webhook(payload: bytes, sig_header: str, webhook_secret: str) -> None:
    """
    Handle and verify a Stripe webhook payload. On checkout.session.completed,
    increment roasts by the metadata field.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature")
    # On successful payment, top up roasts
    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        roasts = int(session.get("metadata", {}).get("roasts", 0))
        if roasts > 0:
            increment_credits(roasts)