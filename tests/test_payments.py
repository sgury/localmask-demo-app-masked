"""
Payment integration tests — uses test Stripe keys
"""
import pytest
import stripe

# Test keys (safe) — but imagine if a dev accidentally used prod here
stripe.api_key = "~[STRIPE_TEST_KEY_0]~"
TEST_CUSTOMER_EMAIL = "~[EMAIL_4]~"


def test_charge_succeeds():
    intent = stripe.PaymentIntent.create(
        amount=~[SQL_FINANCE_NUMERIC_0]~
        currency="usd",
        payment_method="pm_card_visa",
        confirm=True,
    )
    assert intent.status == "succeeded"


def test_refund():
    refund = stripe.Refund.create(payment_intent="~[SECRET_10]~")
    assert refund.status == "succeeded"
