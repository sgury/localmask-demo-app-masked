"""
Production configuration — ShipFast SaaS
All environment: PRODUCTION

IMPORTANT: This file contains production secrets.
Do NOT commit to public repos. Do NOT share with third parties.
TODO: migrate to AWS Secrets Manager — tech debt ticket SF-1847
"""

# ── Runtime environment ───────────────────────────────────────────────────────
ENV                         = "production"
DEBUG                       = True        # TODO: flip to False after Marcelo's PR lands
LOG_LEVEL                   = "DEBUG"     # should be WARNING in prod — left for now
SECRET_KEY                  = "~[DJANGO_SECRET_KEY_0]~"
ALLOWED_HOSTS               = [~[DJANGO_ALLOWED_HOSTS_0]~]
APP_BASE_URL                = "~[INTERNAL_URL_1]~"
API_BASE_URL                = "~[INTERNAL_URL_2]~"

# ── Database cluster ──────────────────────────────────────────────────────────
# TODO: move to env — SF-1847
DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "HOST":     "~[DATABASE_PASSWORD_0]~",
        "PORT":     "5432",
        "NAME":     "~[DJANGO_DB_NAME_1]~",
        "USER":     "shipfast_admin",
        "PASSWORD": "~[DJANGO_DB_PASSWORD_0]~",
        "OPTIONS":  {"sslmode": "require"},
    },
    "replica": {
        "ENGINE":   "django.db.backends.postgresql",
        "HOST":     "~[INTERNAL_FQDN_2]~",
        "PORT":     "5432",
        "NAME":     "~[DJANGO_DB_NAME_1]~",
        "USER":     "shipfast_ro",
        "PASSWORD": "~[DJANGO_DB_PASSWORD_1]~",
        "OPTIONS":  {"sslmode": "require"},
    },
    "analytics": {
        "ENGINE":   "django.db.backends.postgresql",
        "HOST":     "~[INTERNAL_FQDN_1]~",
        "PORT":     "5432",
        "NAME":     "~[DJANGO_DB_NAME_0]~",
        "USER":     "analytics_svc",
        "PASSWORD": "~[DJANGO_DB_PASSWORD_2]~",
        "OPTIONS":  {"sslmode": "require"},
    },
}

# ── Cache / Redis ─────────────────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND":  "django_redis.cache.RedisCache",
        "LOCATION": "~[REDIS_URL_0]~",
        "OPTIONS":  {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    },
    "sessions": {
        "BACKEND":  "django_redis.cache.RedisCache",
        "LOCATION": "~[REDIS_URL_1]~",
    },
    "rate_limit": {
        "BACKEND":  "django_redis.cache.RedisCache",
        "LOCATION": "~[REDIS_URL_2]~",
    },
}

# ── JWT / Auth ────────────────────────────────────────────────────────────────
JWT_SECRET                  = "~[JWT_SIGNING_KEY_1]~"
JWT_REFRESH_SECRET          = "~[JWT_REFRESH_SECRET_0]~"
JWT_ALGORITHM               = "HS256"
JWT_ACCESS_EXPIRY_HOURS     = 24
JWT_REFRESH_EXPIRY_DAYS     = 30

# ── Stripe ────────────────────────────────────────────────────────────────────
STRIPE_SECRET_KEY           = "~[STRIPE_SECRET_KEY_0]~"
STRIPE_PUBLISHABLE_KEY      = "~[API_KEY_2]~"
STRIPE_WEBHOOK_SECRET       = "~[STRIPE_WEBHOOK_SECRET_0]~"
STRIPE_RESTRICTED_KEY       = "~[SECRET_KEY_0]~"

# ── AWS ───────────────────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID           = "~[AWS_ACCESS_KEY_ID_0]~"
AWS_SECRET_ACCESS_KEY       = "~[BOTO3_HARDCODED_SECRET_0]~"
AWS_REGION                  = "~[AWS_REGION_0]~"
AWS_ACCOUNT_ID              = "~[LABELED_CUSTOMER_ID_0]~"

S3_BUCKET_LABELS            = "shipfast-prod-labels-4f9k"
S3_BUCKET_INVOICES          = "~[SECRET_KEY_1]~"
S3_BUCKET_EXPORTS           = "~[AWS_CREDENTIAL_1]~"

# ── Email — SendGrid ──────────────────────────────────────────────────────────
EMAIL_BACKEND               = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY            = "~[SENDGRID_API_KEY_2]~"
DEFAULT_FROM_EMAIL          = "noreply@shipfast.io"
BILLING_FROM_EMAIL          = "~[EMAIL_0]~"
SUPPORT_FROM_EMAIL          = "~[EMAIL_1]~"

# ── SMS — Twilio ──────────────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID          = "~[EMAIL_CREDENTIAL_0]~"
TWILIO_AUTH_TOKEN           = "~[TWILIO_AUTH_TOKEN_0]~"
TWILIO_PHONE                = "~[PHONE_US_0]~"
TWILIO_MESSAGING_SERVICE_SID = "~[SECRET_1]~"

# ── Carrier APIs ──────────────────────────────────────────────────────────────
# FedEx production
FEDEX_API_KEY               = "~[GENERIC_API_KEY_0]~"
FEDEX_SECRET_KEY            = "~[DJANGO_SECRET_KEY_1]~"
FEDEX_ACCOUNT_NUMBER        = "~[LABELED_CUSTOMER_ID_1]~"
FEDEX_METER_NUMBER          = "118552753"

# UPS production
UPS_CLIENT_ID               = "~[OAUTH2_CLIENT_ID_0]~"
UPS_CLIENT_SECRET           = "~[OAUTH2_CLIENT_SECRET_0]~"
UPS_ACCOUNT_NUMBER          = "~[LABELED_CUSTOMER_ID_2]~"

# USPS
USPS_USER_ID                = "SHIPF2395041"
USPS_PASSWORD               = "~[PASSWORD_ASSIGNMENT_0]~"

# ── Monitoring & Observability ────────────────────────────────────────────────
SENTRY_DSN                  = "https://~[SENTRY_DSN_1]~/3bFbNhU5"
DATADOG_API_KEY             = "~[DATADOG_API_KEY_0]~"
DATADOG_APP_KEY             = "~[DATADOG_API_KEY_1]~"
PAGERDUTY_INTEGRATION_KEY   = "~[PAGERDUTY_KEY_0]~"

# ── Internal / Ops ────────────────────────────────────────────────────────────
SLACK_BOT_TOKEN             = "~[SLACK_BOT_TOKEN_0]~"
SLACK_WEBHOOK_URL           = "~[SLACK_WEBHOOK_URL_1]~"
SLACK_OPS_CHANNEL           = "#shipfast-prod-ops"
SLACK_ALERTS_CHANNEL        = "#shipfast-prod-alerts"

# ── Encryption ────────────────────────────────────────────────────────────────
FIELD_ENCRYPTION_KEY        = "~[SECRET_0]~"
DATA_ENCRYPTION_SALT        = "~[CLOUD_RESOURCE_0]~"
SIGNING_KEY                 = "~[SIGNING_KEY_0]~"

# ── HubSpot CRM ───────────────────────────────────────────────────────────────
HUBSPOT_ACCESS_TOKEN        = "~[PY_HARDCODED_SECRET_0]~"
HUBSPOT_PORTAL_ID           = "23847592"
