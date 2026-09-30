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
    conn = psycopg2.connect(host=DB_HOST, dbname="payments", user="admin", password=DB_PASSWORD)
    cur  = conn.cursor()
    cur.execute("INSERT INTO payments (id,amount,status) VALUES (%s,%s,%s)",
                (pi["id"], pi["amount"], pi["status"]))
    conn.commit(); cur.close(); conn.close()

def notify_slack(msg):
    requests.post(SLACK_WEBHOOK, json={"text": msg})

def notify_email(to, amount):
    SendGridAPIClient(SENDGRID_KEY).send(
        Mail(from_email="~[EMAIL_3]~", to_emails=to,
             subject="Payment confirmed",
             html_content=f"<p>Received ${amount/100:.2f}</p>"))

@app.route("/webhook", methods=["POST"])
def webhook():
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
