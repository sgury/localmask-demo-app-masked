# Deploy the Refactored Agent to Cloud
### Secrets never in code. Injected at runtime from vault.

---

## How it works on each platform

### Azure AI Foundry / Azure Functions

```bash
# 1. Push each secret to ~[NER_PERSON_57]~ (one time)
az keyvault secret set --vault-name my-vault --name STRIPE-API-KEY       -~[DATABASE_PASSWORD_7]~ "sk_live_..."
az keyvault secret set --vault-name my-vault --name STRIPE-WEBHOOK-SECRET -~[DATABASE_PASSWORD_7]~ "whsec_..."
az keyvault secret set --vault-name my-vault --name DB-PASSWORD           -~[DATABASE_PASSWORD_7]~ "MyS3cur3..."
az keyvault secret set --vault-name my-vault --name SENDGRID-KEY          -~[DATABASE_PASSWORD_7]~ "SG.7mK2..."
az keyvault secret set --vault-name my-vault --name SLACK-WEBHOOK-URL     -~[DATABASE_PASSWORD_7]~ "https://hooks..."

# 2. Reference ~[NER_PERSON_57]~ secrets in App Settings (not the values — references)
az functionapp config appsettings set \
  --name my-agent-app \
  --settings \
    STRIPE_API_KEY="~[API_KEY_1]~" \
    DB_PASSWORD="~[DATABASE_PASSWORD_4]~"

# 3. Deploy code — no secrets in it
func azure functionapp publish my-agent-app
```

**At runtime**: Azure resolves the ~[NER_PERSON_57]~ references → injects as environment variables → `os.environ["STRIPE_API_KEY"]` works. The code never contained the real value.

---

### AWS Bedrock / Lambda

```bash
# 1. Store secrets in AWS ~[NER_PERSON_53]~
aws secretsmanager create-secret --name ~[PROSE_CREDENTIAL_0]~       -~[PROSE_CREDENTIAL_1]~ "sk_live_..."
aws secretsmanager create-secret --name prod/stripe/webhook-secret -~[PROSE_CREDENTIAL_1]~ "whsec_..."
aws secretsmanager create-secret --name ~[DATABASE_PASSWORD_6]~           -~[PROSE_CREDENTIAL_1]~ "MyS3cur3..."

# 2. Set Lambda environment vars from ~[NER_PERSON_53]~ ARNs
aws lambda update-function-configuration \
  --function-name stripe-notifier \
  --environment Variables="{
    STRIPE_API_KEY_ARN=~[UNQUOTED_ENV_SECRET_0]~,
    DB_PASSWORD_ARN=~[DATABASE_PASSWORD_5]~
  }"

# 3. In code — resolve at runtime (or use Lambda Powertools for automatic injection)
import boto3, json
def get_secret(arn):
    return json.loads(boto3.client("secretsmanager").get_secret_value(SecretId=arn)["SecretString"])
```

---

### GCP Vertex AI / Cloud Run

```bash
# 1. Store secrets in GCP ~[NER_PERSON_55]~
echo -n "sk_live_..."   | gcloud secrets create STRIPE_API_KEY       --data-file=-
echo -n "whsec_..."     | gcloud secrets create STRIPE_WEBHOOK_SECRET --data-file=-
echo -n "MyS3cur3..."   | gcloud secrets create DB_PASSWORD           --data-file=-

# 2. Mount as env vars in Cloud Run
gcloud run deploy stripe-notifier \
  --image gcr.io/my-project/stripe-notifier \
  --set-secrets="STRIPE_API_KEY=~[UNQUOTED_ENV_SECRET_1]~,DB_PASSWORD=DB_PASSWORD:~[PASSWORD_SHORT_0]~"

# 3. Code reads with os.environ["STRIPE_API_KEY"] — same as local .env
```

---

## The full pipeline (one diagram)

```
STEP 1 — Local development
  Original code (hardcoded secrets)
          │
          ▼ localmask scan
  Masked code (~[TOKEN]~ placeholders)
          │
          ▼ Send to AI
  AI refactors → uses os.getenv()
          │
          ▼ localmask rehydrate
  .env file with real values (local only)

STEP 2 — Deployment
  Real secrets → ~[NER_PERSON_57]~ / ~[NER_PERSON_53]~ / ~[NER_PERSON_55]~
  Refactored code → git → CI/CD pipeline → cloud
  Cloud injects secrets at runtime via env vars

STEP 3 — Runtime (cloud agent executing)
  os.environ["STRIPE_API_KEY"] → resolved from vault
  Agent runs with real values
  Secrets were NEVER in source code
  AI NEVER saw the real values
  Git history has ZERO secrets
```
