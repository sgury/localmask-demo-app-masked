"""
Stripe Payment Notifier — REFACTORED by AI (via LocalMask)
=============================================================
This is what the AI produced after seeing the MASKED version.
All ~[TOKEN]~ placeholders were rehydrated locally to real values.

Ready to:
  ✅ Run locally with a .env file
  ✅ Deploy to Azure / AWS / GCP — secrets injected at runtime from vault
  ✅ Commit to git — no secrets anywhere in this file
"""
import os
import stripe
import psycopg2
import requests
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import Flask, request, jsonify

# Load from .env locally — cloud platforms inject these from Key Vault at runtime
load_dotenv()

# ── Load & validate all secrets at startup ────────────────────────────────────
_REQUIRED = [
    "STRIPE_API_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "DB_HOST", "DB_PASSWORD",
    "SENDGRID_KEY",
    "SLACK_WEBHOOK_URL",
]

missing = [k for k in _REQUIRED if not os.getenv(k)]
if missing:
    raise EnvironmentError(
        f"\n\nMissing environment variables: {', '.join(missing)}\n"
        f"  → Copy .env.example to .env and fill in your values.\n"
        f"  → In Azure: add these to Key Vault and reference in App Settings.\n"
        f"  → In AWS: add to Secrets Manager and reference in Lambda env vars.\n"
    )

STRIPE_API_KEY      = os.environ["STRIPE_API_KEY"]
WEBHOOK_SECRET      = os.environ["STRIPE_WEBHOOK_SECRET"]
DB_HOST             = os.environ["DB_HOST"]
DB_PASSWORD         = os.environ["DB_PASSWORD"]
SENDGRID_KEY        = os.environ["SENDGRID_KEY"]
SLACK_WEBHOOK       = os.environ["SLACK_WEBHOOK_URL"]

stripe.api_key = STRIPE_API_KEY

app = Flask(__name__)

# ── Logic (unchanged — AI kept all functionality intact) ──────────────────────
def save_payment(pi):
    """Insert a Stripe PaymentIntent's id, amount and status into the ``payments`` table.

    Connection details come from environment variables
    (``DB_HOST``, ``DB_PASSWORD``, optional ``DB_NAME``/``DB_USER``).

    Args:
        pi: PaymentIntent object from the webhook event.
    """
    conn = psycopg2.connect(
        host=DB_HOST, dbname=os.getenv("DB_NAME", "payments"),
        user=os.getenv("DB_USER", "admin"), password=DB_PASSWORD
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments (id, amount, status) VALUES (%s, %s, %s)",
        (pi["id"], pi["amount"], pi["status"])
    )
    conn.commit(); cur.close(); conn.close()

def notify_slack(msg: str):
    """Post a plain-text message to the Slack webhook in ``SLACK_WEBHOOK_URL``.

    Args:
        msg: Message text.
    """
    requests.post(SLACK_WEBHOOK, json={"text": msg}, timeout=5)

def notify_email(to: str, amount: int):
    """Send a payment-confirmation email via SendGrid.

    Args:
        to: Recipient email address.
        amount: Amount in cents (formatted as dollars in the email).
    """
    SendGridAPIClient(SENDGRID_KEY).send(
        Mail(
            from_email=os.getenv("FROM_EMAIL", "~[EMAIL_2]~"),
            to_emails=to,
            subject="Payment confirmed",
            html_content=f"<p>Your payment of ${amount/100:.2f} was received.</p>"
        )
    )

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle Stripe webhook POSTs.

    Verifies the ``Stripe-Signature`` header against ``STRIPE_WEBHOOK_SECRET``;
    on ``payment_intent.succeeded`` saves the payment, notifies Slack, and emails
    the receipt address if present.

    Returns:
        JSON ``{"ok": true}``, or ``{"error": ...}`` with HTTP 400 on an invalid signature.
    """
    try:
        event = stripe.Webhook.construct_event(
            request.data, request.headers["Stripe-Signature"], WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return jsonify(error="Invalid signature"), 400

    if event["type"] == "payment_intent.succeeded":
        pi = event["data"]["object"]
        save_payment(pi)
        notify_slack(f"💳 Payment received: ${pi['amount']/100:.2f}")
        if pi.get("receipt_email"):
            notify_email(pi["receipt_email"], pi["amount"])

    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 5000)))
