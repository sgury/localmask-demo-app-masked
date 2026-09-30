"""
Stripe Payment Notifier — found on GitHub ⭐ 847
Works great. Problem: my credentials are hardcoded.
I need to:
  1. Refactor to .env  (safe for git)
  2. Deploy as a cloud agent  (safe for cloud)
  ...but I can't paste this into Claude — my real keys are in here.
"""
import stripe, psycopg2, requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import Flask, request, jsonify

app = Flask(__name__)

# ── My credentials (hardcoded — needs to change before deploy) ───────────────
stripe.api_key        = "~[STRIPE_SECRET_KEY_2]~"
WEBHOOK_SECRET        = "~[STRIPE_WEBHOOK_SECRET_2]~"
DB_HOST               = "~[INTERNAL_FQDN_3]~"
DB_PASSWORD           = "~[DATABASE_PASSWORD_1]~"
SENDGRID_KEY          = "~[SENDGRID_API_KEY_0]~"
SLACK_WEBHOOK         = "~[SLACK_WEBHOOK_URL_2]~"

# ── Logic ─────────────────────────────────────────────────────────────────────
def save_payment(pi):
    """Insert a Stripe PaymentIntent's id, amount and status into the ``payments`` table.

    Args:
        pi: PaymentIntent object from the webhook event.
    """
    conn = psycopg2.connect(host=DB_HOST, dbname="payments", user="admin", password=DB_PASSWORD)
    cur  = conn.cursor()
    cur.execute("INSERT INTO payments (id,amount,status) VALUES (%s,%s,%s)",
                (pi["id"], pi["amount"], pi["status"]))
    conn.commit(); cur.close(); conn.close()

def notify_slack(msg):
    """Post a plain-text message to the configured Slack incoming webhook.

    Args:
        msg: Message text.
    """
    requests.post(SLACK_WEBHOOK, json={"text": msg})

def notify_email(to, amount):
    """Send a payment-confirmation email via SendGrid.

    Args:
        to: Recipient email address.
        amount: Amount in cents (formatted as dollars in the email).
    """
    SendGridAPIClient(SENDGRID_KEY).send(
        Mail(from_email="~[EMAIL_3]~", to_emails=to,
             subject="Payment confirmed",
             html_content=f"<p>Received ${amount/100:.2f}</p>"))

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle Stripe webhook POSTs.

    Verifies the ``Stripe-Signature`` header; on ``payment_intent.succeeded``
    saves the payment, notifies Slack, and emails the receipt address if present.

    Returns:
        JSON ``{"ok": true}``, or ``{"error": ...}`` with HTTP 400 on a bad signature.
    """
    try:
        event = stripe.Webhook.construct_event(
            request.data, request.headers["Stripe-Signature"], WEBHOOK_SECRET)
    except Exception:
        return jsonify(error="bad sig"), 400

    if event["type"] == "payment_intent.succeeded":
        pi = event["data"]["object"]
        save_payment(pi)
        notify_slack(f"💳 ${pi['amount']/100:.2f} received")
        if pi.get("receipt_email"):
            notify_email(pi["receipt_email"], pi["amount"])

    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(port=~[NETWORK_PORT_0]~)
