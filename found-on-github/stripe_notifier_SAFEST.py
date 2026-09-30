"""
Stripe Payment Notifier — SAFEST version
=========================================
Secrets are NEVER in code, NEVER in .env files, NEVER in environment variables.
They are fetched at runtime directly from the cloud vault using workload identity.

Security properties:
  ✅ No secrets in source code
  ✅ No secrets in git history
  ✅ No secrets in environment variables
  ✅ No secrets in .env files on disk
  ✅ No static credentials anywhere
  ✅ Vault access logged and auditable
  ✅ Secrets rotatable without code changes
  ✅ Workload identity — no service account keys
  ✅ AI (LocalMask) never saw real values
  ✅ CI/CD pipeline never saw real values

How secrets are fetched at runtime:
  Azure:  Azure Key Vault SDK + DefaultAzureCredential (managed identity)
  AWS:    AWS Secrets Manager SDK + IAM role (no static key)
  GCP:    GCP Secret Manager SDK + Workload Identity Federation
"""

import os
import functools
import logging
import stripe
import psycopg2
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import Flask, request, jsonify

logger = logging.getLogger(__name__)

# ── Secret loader — fetches from vault at startup, cached in memory ───────────

class VaultSecrets:
    """
    Fetches all required secrets from the cloud vault once at startup.
    Cached in memory for the process lifetime — never written to disk.
    Raises at startup if any secret is missing or vault is unreachable.
    """

    REQUIRED = [
        "STRIPE-API-KEY",
        "STRIPE-WEBHOOK-SECRET",
        "DB-PASSWORD",
        "SENDGRID-API-KEY",
        "SLACK-WEBHOOK-URL",
    ]

    def __init__(self):
        """Load all ``REQUIRED`` secrets from the vault named by ``VAULT_PLATFORM``.

        ``VAULT_PLATFORM`` is ``azure`` (default), ``aws`` or ``gcp``.

        Raises:
            ValueError: If ``VAULT_PLATFORM`` is not a supported platform.
        """
        platform = os.getenv("VAULT_PLATFORM", "azure").lower()
        loader   = getattr(self, f"_load_{platform}", None)
        if not loader:
            raise ValueError(f"Unknown VAULT_PLATFORM: {platform}. Use: azure | aws | gcp")

        logger.info(f"Loading secrets from {platform.upper()} vault...")
        self._secrets = loader()
        logger.info(f"Loaded {len(self._secrets)} secrets — none written to disk")

    # ── Azure Key Vault ───────────────────────────────────────────────────────
    def _load_azure(self) -> dict:
        """Fetch ``REQUIRED`` secrets from Azure Key Vault at ``AZURE_VAULT_URL``.

        Authenticates with ``DefaultAzureCredential``.

        Returns:
            dict: Secret name -> value.
        """
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential

        vault_url = os.environ["AZURE_VAULT_URL"]  # e.g. https://my-vault.vault.azure.net
        client    = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())

        return {name: client.get_secret(name).value for name in self.REQUIRED}

    # ── AWS Secrets Manager ───────────────────────────────────────────────────
    def _load_aws(self) -> dict:
        """Fetch ``REQUIRED`` secrets from AWS Secrets Manager.

        Secret IDs are ``<AWS_SECRET_PREFIX>/<name-lowercased>`` (prefix defaults to ``prod``).

        Returns:
            dict: Secret name -> value.
        """
        import boto3, json
        prefix = os.getenv("AWS_SECRET_PREFIX", "prod")
        client = boto3.client("secretsmanager")

        secrets = {}
        for name in self.REQUIRED:
            arn  = f"{prefix}/{name.lower()}"
            resp = client.get_secret_value(SecretId=arn)
            secrets[name] = resp["SecretString"]
        return secrets

    # ── GCP Secret Manager ────────────────────────────────────────────────────
    def _load_gcp(self) -> dict:
        """Fetch the latest version of each ``REQUIRED`` secret from GCP Secret Manager.

        Uses project ``GCP_PROJECT_ID``; secret IDs are lowercased with ``-`` -> ``_``.

        Returns:
            dict: Secret name -> value.
        """
        from google.cloud import secretmanager

        project = os.environ["GCP_PROJECT_ID"]
        client  = secretmanager.SecretManagerServiceClient()

        secrets = {}
        for name in self.REQUIRED:
            secret_id = name.lower().replace("-", "_")
            path      = f"projects/{project}/secrets/{secret_id}/versions/latest"
            resp      = client.access_secret_version(name=path)
            secrets[name] = resp.payload.data.decode("utf-8")
        return secrets

    def get(self, key: str) -> str:
        """Return a cached secret value.

        Args:
            key: Vault secret name, e.g. ``"STRIPE-API-KEY"``.

        Raises:
            KeyError: If the secret is missing or empty.
        """
        value = self._secrets.get(key)
        if not value:
            raise KeyError(f"Secret '{key}' not found in vault")
        return value


# ── Bootstrap — load secrets once at startup ─────────────────────────────────
vault = VaultSecrets()

stripe.api_key = vault.get("STRIPE-API-KEY")


# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__)


def get_db():
    """Open a new PostgreSQL connection using the vault-held ``DB-PASSWORD``.

    Host, database name and user come from ``DB_HOST``, ``DB_NAME`` and ``DB_USER``.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME", "payments"),
        user=os.getenv("DB_USER", "admin"),
        password=vault.get("DB-PASSWORD")   # from vault — not env var, not .env
    )


def save_payment(pi: dict):
    """Insert a Stripe PaymentIntent's id, amount and status into the ``payments`` table.

    Args:
        pi: PaymentIntent object from the webhook event.
    """
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO payments (id, amount, status) VALUES (%s, %s, %s)",
        (pi["id"], pi["amount"], pi["status"])
    )
    conn.commit(); cur.close(); conn.close()


def notify_slack(msg: str):
    """Post a plain-text message to the vault-held Slack webhook URL.

    Args:
        msg: Message text.
    """
    requests.post(
        vault.get("SLACK-WEBHOOK-URL"),
        json={"text": msg},
        timeout=5
    )


def notify_email(to: str, amount: int):
    """Send a payment-confirmation email via SendGrid using the vault-held API key.

    Args:
        to: Recipient email address.
        amount: Amount in cents (formatted as dollars in the email).
    """
    SendGridAPIClient(vault.get("SENDGRID-API-KEY")).send(
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

    Verifies the ``Stripe-Signature`` header against the vault-held webhook secret;
    on ``payment_intent.succeeded`` saves the payment, notifies Slack, and emails
    the receipt address if present.

    Returns:
        JSON ``{"ok": true}``, or ``{"error": ...}`` with HTTP 400 on an invalid signature.
    """
    try:
        event = stripe.Webhook.construct_event(
            request.data,
            request.headers.get("Stripe-Signature"),
            vault.get("STRIPE-WEBHOOK-SECRET")
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
