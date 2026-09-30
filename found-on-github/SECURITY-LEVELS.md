# Security Levels — Which version is right for you?

Three versions of the same script. Each progressively safer.

---

## Level 1 — Original (unsafe)
**File**: `stripe_notifier.py`

```python
stripe.api_key = "~[STRIPE_SECRET_KEY_5]~"   # hardcoded
DB_PASSWORD    = "~[DATABASE_PASSWORD_1]~"        # hardcoded
```

| Risk | Status |
|------|--------|
| Secrets in source code | ❌ YES |
| Secrets in git history | ❌ YES |
| Safe to share with AI | ❌ NO |
| Safe to commit | ❌ NO |
| Safe to deploy | ❌ NO |

---

## Level 2 — Refactored (good)
**File**: `stripe_notifier_REFACTORED.py`

```python
load_dotenv()
stripe.api_key = os.environ["STRIPE_API_KEY"]  # from .env file
```

| Risk | Status |
|------|--------|
| Secrets in source code | ✅ NO |
| Secrets in git history | ✅ NO (if .env is gitignored) |
| .env file on disk | ⚠️ YES — must protect this file |
| Safe to share with AI | ✅ YES (after LocalMask) |
| Safe to commit | ✅ YES (code only, not .env) |
| Safe to deploy | ⚠️ Depends — .env must not travel with the deployment |

**Good for**: local development, small teams, non-critical apps.

---

## Level 3 — Vault + Workload Identity (safest)
**File**: `stripe_notifier_SAFEST.py`

```python
vault = VaultSecrets()                         # fetches from ~[NER_PERSON_57]~ at startup
stripe.api_key = vault.get("STRIPE-API-KEY")  # never in any file
```

| Risk | Status |
|------|--------|
| Secrets in source code | ✅ NO |
| Secrets in git history | ✅ NO |
| Secrets in .env file | ✅ NO — no .env file at all |
| Secrets in env variables | ✅ NO — fetched from vault |
| Secrets in CI/CD pipeline | ✅ NO — workload identity |
| Secrets visible to AI | ✅ NO — LocalMask protected them |
| Audit trail of secret access | ✅ YES — vault logs every read |
| Secret rotation without code change | ✅ YES |
| Safe to share with AI | ✅ YES |
| Safe to commit | ✅ YES |
| Safe to deploy anywhere | ✅ YES |

**Good for**: production workloads, regulated industries, enterprise teams, Series A and beyond.

---

## The pipeline that produces Level 3

```
1. Start: stripe_notifier.py (hardcoded secrets)
          ↓
2. LocalMask scan — secrets replaced with ~[TOKEN]~ placeholders
          ↓
3. Claude sees masked code — refactors to vault.get("STRIPE-API-KEY")
          ↓
4. push_secrets_to_vault.py — LocalMask mapping → ~[NER_PERSON_57]~ (no disk writes)
          ↓
5. Deploy stripe_notifier_SAFEST.py — zero secrets anywhere in code or config
          ↓
6. Runtime: VaultSecrets() fetches from ~[NER_PERSON_57]~ using managed identity
          ↓
7. Agent runs. Audited. Rotatable. Zero-secret source code.
```

**At no point did any secret touch a file, a log, an AI, or a deployment pipeline.**

---

## The two tools working together

| Tool | Role | When |
|------|------|------|
| **LocalMask** | Protects secrets from AI during development | Before asking AI for help |
| **~[NER_PERSON_57]~ / ~[NER_PERSON_53]~** | Protects secrets from code/git/CI at deploy time | Before and during deployment |

They solve different parts of the same problem.
Neither is sufficient alone.
Together they close every gap.
