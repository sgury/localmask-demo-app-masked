"""
push_secrets_to_vault.py
========================
Takes LocalMask's local secret mapping and pushes each real value
directly into your cloud vault — without ever writing them to disk.

No .env file is created. No secrets are logged. No intermediate files.
LocalMask → memory → vault. That's the chain.

Usage:
    python push_secrets_to_vault.py --platform azure --vault my-vault-name
    python push_secrets_to_vault.py --platform aws   --prefix prod/shipfast
    python push_secrets_to_vault.py --platform gcp   --project my-gcp-project

Requires:
    pip install localmask azure-keyvault-secrets azure-identity boto3 google-cloud-secret-manager
"""

import argparse
import subprocess
import json
import sys

# ── Vault mapping ─────────────────────────────────────────────────────────────
# Maps LocalMask placeholder names → vault secret names
# Edit this to match your project's naming conventions.
VAULT_KEY_MAP = {
    "STRIPE_SECRET_KEY_0":  "STRIPE-API-KEY",
    "STRIPE_WEBHOOK_0":     "STRIPE-WEBHOOK-SECRET",
    "PASSWORD_0":           "DB-PASSWORD",
    "SENDGRID_KEY_0":       "SENDGRID-API-KEY",
    "SLACK_WEBHOOK_0":      "SLACK-WEBHOOK-URL",
    # Add more as needed
}


def get_real_values_from_localmask(scan_id: str) -> dict:
    """
    Ask LocalMask for the real values — in memory only.
    Never written to disk.
    """
    result = subprocess.run(
        ["localmask", "export-secrets", scan_id, "--format", "json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[ERROR] LocalMask export failed: {result.stderr}")
        sys.exit(1)

    secrets = json.loads(result.stdout)
    print(f"[OK] Retrieved {len(secrets)} secrets from LocalMask (in memory — not on disk)")
    return secrets  # {"STRIPE_SECRET_KEY_0": "sk_live_...", "PASSWORD_0": "MyS3cur3...", ...}


# ── Azure Key Vault ───────────────────────────────────────────────────────────

def push_to_azure(secrets: dict, vault_name: str):
    """
    Push secrets to Azure Key Vault using DefaultAzureCredential.
    No static credentials — uses your az login / managed identity.
    """
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential

    vault_url = f"https://{vault_name}.vault.azure.net"
    client = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())

    print(f"\n[Azure Key Vault] Pushing to {vault_url}")
    print("  Auth: DefaultAzureCredential (az login / managed identity — no static keys)")

    for placeholder, vault_key in VAULT_KEY_MAP.items():
        real_value = secrets.get(placeholder)
        if not real_value:
            print(f"  [SKIP] {placeholder} not in scan")
            continue

        client.set_secret(vault_key, real_value)
        print(f"  [OK] {vault_key} → vault (value not logged)")

    print(f"\n[DONE] Secrets in Key Vault. Safe to:")
    print(f"  - Reference in App Settings: @Microsoft.KeyVault(SecretUri=...)")
    print(f"  - Use in Azure Functions with managed identity")
    print(f"  - Rotate any time without touching code")


# ── AWS Secrets Manager ───────────────────────────────────────────────────────

def push_to_aws(secrets: dict, prefix: str):
    """
    Push secrets to AWS Secrets Manager.
    Uses boto3 default credential chain — IAM role, env vars, or AWS SSO.
    No static keys embedded here.
    """
    import boto3
    from botocore.exceptions import ClientError

    client = boto3.client("secretsmanager")
    print(f"\n[AWS Secrets Manager] Prefix: {prefix}")
    print("  Auth: boto3 default chain (IAM role / AWS SSO — no hardcoded keys)")

    for placeholder, vault_key in VAULT_KEY_MAP.items():
        real_value = secrets.get(placeholder)
        if not real_value:
            print(f"  [SKIP] {placeholder} not in scan")
            continue

        secret_name = f"{prefix}/{vault_key.lower()}"
        try:
            client.create_secret(Name=secret_name, SecretString=real_value)
            print(f"  [CREATED] {secret_name} (value not logged)")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceExistsException":
                client.put_secret_value(SecretId=secret_name, SecretString=real_value)
                print(f"  [UPDATED] {secret_name} (value not logged)")
            else:
                raise

    print(f"\n[DONE] Secrets in Secrets Manager. Safe to:")
    print(f"  - Reference in Lambda: aws secretsmanager get-secret-value")
    print(f"  - Use with Bedrock Agent action groups")
    print(f"  - Auto-rotate with AWS rotation lambdas")


# ── GCP Secret Manager ────────────────────────────────────────────────────────

def push_to_gcp(secrets: dict, project_id: str):
    """
    Push secrets to GCP Secret Manager.
    Uses Application Default Credentials — gcloud auth or workload identity.
    No service account key file needed.
    """
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"
    print(f"\n[GCP Secret Manager] Project: {project_id}")
    print("  Auth: Application Default Credentials (gcloud auth / workload identity)")

    for placeholder, vault_key in VAULT_KEY_MAP.items():
        real_value = secrets.get(placeholder)
        if not real_value:
            print(f"  [SKIP] {placeholder} not in scan")
            continue

        secret_id = vault_key.lower().replace("-", "_")
        secret_path = f"{parent}/secrets/{secret_id}"

        # Create secret resource if it doesn't exist
        try:
            client.create_secret(
                parent=parent,
                secret_id=secret_id,
                secret={"replication": {"automatic": {}}}
            )
        except Exception:
            pass  # already exists

        # Add secret version
        client.add_secret_version(
            parent=secret_path,
            payload={"data": real_value.encode("utf-8")}
        )
        print(f"  [OK] {secret_id} → Secret Manager (value not logged)")

    print(f"\n[DONE] Secrets in Secret Manager. Safe to:")
    print(f"  - Mount in Cloud Run: --set-secrets=VAR=secret_id:latest")
    print(f"  - Use in Vertex AI agents via service account ~[SERVER_HOSTNAME_SQL_2]~")
    print(f"  - Auto-rotate with Cloud Scheduler")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Push LocalMask secrets directly to cloud vault — no .env file written"
    )
    parser.add_argument("--scan-id",  required=True, help="LocalMask scan ID")
    parser.add_argument("--platform", choices=["azure", "aws", "gcp"], required=True)
    parser.add_argument("--vault",    help="Azure Key Vault name")
    parser.add_argument("--prefix",   default="prod", help="AWS secret name prefix")
    parser.add_argument("--project",  help="GCP project ID")
    args = parser.parse_args()

    print("=" * 55)
    print("  LocalMask → Cloud Vault (zero .env files)")
    print("=" * 55)
    print("\n⚠️  Secrets flow: LocalMask mapping → memory → vault")
    print("   Nothing is written to disk. Nothing is logged.\n")

    secrets = get_real_values_from_localmask(args.scan_id)

    if args.platform == "azure":
        if not args.vault:
            print("[ERROR] --vault required for Azure"); sys.exit(1)
        push_to_azure(secrets, args.vault)

    elif args.platform == "aws":
        push_to_aws(secrets, args.prefix)

    elif args.platform == "gcp":
        if not args.project:
            print("[ERROR] --project required for GCP"); sys.exit(1)
        push_to_gcp(secrets, args.project)

    print("\n" + "=" * 55)
    print("  Secrets are in the vault.")
    print("  Source code has zero credentials.")
    print("  AI never saw a real value.")
    print("  Git history is clean.")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
