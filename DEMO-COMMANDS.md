# LocalMask Demo — Command Cheat Sheet
### Pre-written terminal commands for all three video recordings

**Read this before recording.** Every command is pre-written in order.
Copy-paste directly or type from memory. No surprises on camera.

---

## PRE-FLIGHT CHECKS (run before any recording)

```bash
# Confirm you're in the right directory
pwd
# Expected: /Users/shaig/Downloads/localmask-demo-app

# Confirm LocalMask is installed
localmask --version
# Expected: localmask 0.x.x (any version)

# Confirm license is active
localmask license status
# Expected: Status: Active | Licensed to: <your name/org>

# Confirm all demo files exist
ls src/ config/
# Expected:
#   src/   → app.py  ai_generated_checkout.py  database.py
#   config/ → settings.py

# Quick sanity check — make sure secrets are visible in the raw file
head -35 src/app.py
# Expected: Stripe key visible around line 28
```

---

---

# VIDEO 1 — "The Catch-22"
### Scenario: Want AI to refactor hardcoded secrets into .env, but can't share the code with AI because the code HAS the secrets.

---

## SETUP (before hitting record)

```bash
# Make sure the repo is clean / no leftover scan state
ls -la .localmask/ 2>~[SYSTEM_PATH_UNIX_0]~ || echo "No .localmask dir — clean state confirmed"

# Optional: bump VS Code font size in terminal
# Cmd+= three times to zoom the editor pane
```

---

## BLOCK 1 — Show the problem (narrate as you type)

```bash
# Open app.py in VS Code — do this by clicking in the editor, not terminal
# Then in terminal, show the line count so it feels substantial:
wc -l src/app.py src/database.py config/settings.py
# Expected output (approximate):
#   170  src/app.py
#    95  src/database.py
#    80  config/settings.py
#   345  total
```

**Narration cue**: "15 secrets across three files, 345 lines of code. This is what you'd have to paste into an AI chat."

---

## BLOCK 2 — Run the scan

```bash
localmask scan .
```

**Expected output** (approximate — exact numbers may vary by LocalMask version):
```
Scanning /Users/shaig/Downloads/localmask-demo-app...

  src/app.py             ████████████  22 secrets
  src/database.py        ████          6 secrets
  config/settings.py     ██████████    19 secrets

  Total: 47 detections across 3 files

Scan ID: scan_<alphanumeric_id>
Run `localmask get-review-queue` to review detections.
```

**Note for recording**: The scan ID will be a random string. Write it down as it appears — you'll use it in the next command. Or just use `localmask get-review-queue` without the scan ID.

---

## BLOCK 3 — Review the detection queue

```bash
localmask get-review-queue
```

**Expected output** (excerpt):
```
┌─────────────────────────────────────────────────────────────────────────┐
│  REVIEW QUEUE — 47 detections pending                                   │
├──────────┬──────────────────────────────┬─────────────┬─────────────────┤
│  Type    │  File                        │  Line       │  Placeholder    │
├──────────┼──────────────────────────────┼─────────────┼─────────────────┤
│  STRIPE  │  src/app.py                  │  28         │  ~[STRIPE_KEY_0]~  │
│  DB_URL  │  src/app.py                  │  21         │  ~[DB_CONN_0]~  │
│  DB_URL  │  src/app.py                  │  22         │  ~[DB_CONN_1]~  │
│  JWT     │  src/app.py                  │  33         │  ~[JWT_SIGNING_KEY_0]~  │
│  AWS_KEY │  src/app.py                  │  39         │  ~[AWS_KEY_0]~  │
│  AWS_SEC │  src/app.py                  │  40         │  ~[AWS_SECRET_0]~  │
│  REDIS   │  src/app.py                  │  52         │  ~[REDIS_URL_0]~  │
│  ...     │  ...                         │  ...        │  ...            │
└──────────┴──────────────────────────────┴─────────────┴─────────────────┘
```

**Narration cue**: "Each one tells you what type of secret, where it lives, and what placeholder it becomes. Nothing has left the machine yet."

---

## BLOCK 4 — Approve the scan

```bash
# Approve all detections (bulk approve)
localmask bulk-review --action approve
```

**Expected output**:
```
Approved 47 detections.
Scan is ready for masking.
```

---

## BLOCK 5 — THE REVEAL — Generate masked prompt

```bash
localmask mask-prompt "Refactor all hardcoded credentials in src/app.py and config/settings.py into environment variables. Create a .env.example file with safe placeholder values and update all code references to use os.getenv(). Return the full refactored files and the .env.example."
```

**Expected output**:
```
Generating masked prompt...

The following files will be included (masked):
  - src/app.py  (22 secrets masked)
  - config/settings.py  (19 secrets masked)

--- MASKED PROMPT ---

Refactor all hardcoded credentials in src/app.py and config/settings.py
into environment variables...

[File: src/app.py]
...
stripe.api_key = "~[STRIPE_KEY_0]~"
...
JWT_SECRET = "~[JWT_SIGNING_KEY_0]~"
...

--- END PROMPT ---

Copy this prompt and paste it into your AI assistant.
To rehydrate the AI's response: localmask rehydrate-answer "<response>"
```

**Narration cue**: Pause here. Point at `~[STRIPE_KEY_0]~` on screen. "The AI gets the full file. The code structure is intact. But your live Stripe key is `~[STRIPE_KEY_0]~`."

---

## BLOCK 6 — Rehydrate the AI response

After getting the AI's response, copy the entire response text and run:

```bash
localmask rehydrate-answer "PASTE_AI_RESPONSE_HERE"
```

**Expected output**:
```
Rehydrating response...

  Replaced 22 placeholders with real values.
  Output written to: .localmask/rehydrated/response_<timestamp>.py

Preview (first 10 lines of rehydrated output):
  stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # was sk_live_51OkLpB...
  JWT_SECRET = os.getenv("JWT_SECRET")
  ...
```

---

## BLOCK 7 — Verify the result (optional but satisfying on camera)

```bash
# Show the rehydrated file
cat .localmask/rehydrated/response_*.py | head -40
# Expected: clean refactored code with os.getenv() calls, real values restored where needed

# Show the .env.example if AI generated it
cat .env.example 2>~[SYSTEM_PATH_UNIX_0]~ || echo "Check rehydrated output for .env.example content"
```

---

---

# VIDEO 2 — "AI Hardcoded My Key"
### Scenario: Cursor generated a checkout flow and hardcoded the production Stripe key. LocalMask pre-commit hook catches it before the push.

---

## SETUP (before hitting record)

```bash
# Confirm the AI-generated file is present and contains the hardcoded key
grep -n "sk_live" src/ai_generated_checkout.py
# Expected: line 21: STRIPE_API_KEY = "~[STRIPE_SECRET_KEY_1]~"

# Confirm git hook is NOT yet installed (so we can install it on camera)
ls .git/hooks/pre-commit 2>~[SYSTEM_PATH_UNIX_0]~ && echo "HOOK EXISTS — remove it first" || echo "No hook — clean state confirmed"

# If hook exists from a previous take, remove it:
rm .git/hooks/pre-commit
```

---

## BLOCK 1 — Show the AI-generated file

```bash
# Show the file header (the "Generated by Cursor" comment)
head -10 src/ai_generated_checkout.py
# Expected:
# # Generated by Cursor on 2026-09-18
# # Model: ~[SUFFIXED_RESOURCE_NAME_0]~
# ...

# Show the hardcoded key line
grep -n "sk_live\|STRIPE_API_KEY\|api_key" src/ai_generated_checkout.py | head -5
# Expected:
# 21: STRIPE_API_KEY = "~[STRIPE_SECRET_KEY_1]~"
# 22: stripe.api_key = STRIPE_API_KEY
```

---

## BLOCK 2 — Install the git hook

```bash
localmask setup-git-hook
```

**Expected output**:
```
Installing LocalMask pre-commit hook...

  Hook written to: .git/hooks/pre-commit
  Permissions set: executable

LocalMask will scan staged files before every commit.
Secrets found = commit blocked. No secrets = commit proceeds normally.
```

---

## BLOCK 3 — Stage the file (about to commit)

```bash
git add src/ai_generated_checkout.py
git status
```

**Expected output**:
```
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   src/ai_generated_checkout.py
```

---

## BLOCK 4 — THE REVEAL — Trigger the hook

```bash
git commit -m "add stripe checkout flow"
```

**Expected output** (this is the money shot):
```
Running LocalMask pre-commit scan...

  SECRETS DETECTED — commit blocked

  ┌─────────────────────────────────────────────────────────────┐
  │  File: src/ai_generated_checkout.py                         │
  │                                                             │
  │  Line 21 — STRIPE_SECRET_KEY                               │
  │    sk_live_51OkLpBJKl2mW8Vzf... → ~[STRIPE_KEY_0]~        │
  │                                                             │
  │  Line 25 — STRIPE_WEBHOOK_SECRET                           │
  │    whsec_9mK3nPpX8vLqS5wF2... → ~[STRIPE_WEBHOOK_1]~      │
  │                                                             │
  │  2 secrets found.                                           │
  └─────────────────────────────────────────────────────────────┘

Commit blocked.
  - To review: localmask get-review-queue
  - To override (not recommended): git commit --no-verify
  - To fix: remove secrets from staged files, then commit again.
```

**Hold on this output for 2-3 seconds before narrating.**

---

## BLOCK 5 — Ask AI to fix its own mistake (via LocalMask)

```bash
localmask mask-prompt "The file src/ai_generated_checkout.py has hardcoded Stripe credentials on lines 21 and 25. Specifically, STRIPE_API_KEY and STRIPE_WEBHOOK_SECRET are hardcoded strings. Replace them with os.getenv() calls using the variable names STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET. Show me the corrected lines 19-27 only."
```

**Expected output**: Masked prompt generated. ~[NER_PERSON_4]~ key appears as `~[STRIPE_KEY_0]~` in the context sent to AI.

---

## BLOCK 6 — Apply the fix manually (or show rehydrated AI fix)

Open `src/ai_generated_checkout.py` in VS Code and make the changes:

**Before** (line 21-25):
```python
# Using your API key from the codebase
STRIPE_API_KEY = "~[STRIPE_SECRET_KEY_0]~"
stripe.api_key = STRIPE_API_KEY

STRIPE_WEBHOOK_SECRET = "~[STRIPE_WEBHOOK_SECRET_0]~"
```

**After** (what you show after the fix):
```python
import os

STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_API_KEY

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
```

---

## BLOCK 7 — Clean commit succeeds

```bash
git add src/ai_generated_checkout.py
git commit -m "add stripe checkout flow — keys via env vars"
```

**Expected output** (satisfying contrast to the blocked commit):
```
Running LocalMask pre-commit scan...

  No secrets detected. ✓

[main 3f8c2a1] add stripe checkout flow — keys via env vars
 1 file changed, 4 insertions(+), 2 deletions(-)
```

---

---

# VIDEO 3 — "The Security Audit"
### Scenario: Ask AI to find all security vulnerabilities in a codebase that's full of real credentials. LocalMask masks the creds before sending.

---

## SETUP (before hitting record)

```bash
# Confirm the codebase is in its original state (vulnerabilities intact)
grep -n "f\"SELECT\|f'SELECT" src/app.py
# Expected: at least 2 string-formatted SQL queries

grep -n "logger.debug.*password" src/app.py
# Expected: line ~107 — password logged in plaintext

# Clean any leftover scan state for a fresh demo
rm -rf .localmask/ 2>~[SYSTEM_PATH_UNIX_0]~ && echo "Clean state" || echo "No .localmask dir to clean"
```

---

## BLOCK 1 — Show the vulnerable code (narrate as you scroll)

```bash
# Show line count to establish scope
wc -l src/app.py src/database.py config/settings.py
# Expected: ~345 total lines

# Highlight the SQL injection — use grep to find the line quickly
grep -n "f\"SELECT\|f'SELECT\|f\".*WHERE" src/app.py
# Expected output:
# 94:    query = f"SELECT id, email, password_hash, role, org_id FROM users WHERE email = '{email}'"
# 153:    query = f"SELECT * FROM shipments WHERE id = '{shipment_id}'"
# 181:        query = f"SELECT id, email, org_id, role, created_at FROM users WHERE email LIKE '%{search}%'..."

# Show the password logging
grep -n "password" src/app.py
# Expected output includes: logger.debug(f"Login attempt: email={email}, password={password}")
```

---

## BLOCK 2 — Run the scan

```bash
localmask scan .
```

**Expected output** (same as Video 1, Block 2):
```
Scanning /Users/shaig/Downloads/localmask-demo-app...

  src/app.py             ████████████  22 secrets
  src/database.py        ████          6 secrets
  config/settings.py     ██████████    19 secrets

  Total: 47 detections across 3 files

Scan ID: scan_<alphanumeric_id>
```

---

## BLOCK 3 — Bulk approve all detections

```bash
localmask bulk-review --action approve
```

**Expected**:
```
Approved 47 detections.
```

---

## BLOCK 4 — THE REVEAL — Build the security audit prompt

```bash
localmask mask-prompt "You are a senior application security engineer performing a full security audit. Analyze this codebase completely and identify ALL security vulnerabilities. Categorize findings by severity (Critical / High / Medium / Low). For each finding include: severity level, affected file and exact line number, vulnerability type (e.g. SQL injection, IDOR, missing auth, etc.), description of the risk, and a specific recommended fix. Cover: injection attacks, authentication and authorization flaws, insecure data handling, missing security controls (rate limiting, input validation, HTTPS enforcement), logging and monitoring issues, and any other issues you find. Be exhaustive — this is going to production."
```

**Expected output**: Masked prompt generated. All 4 code files attached. All secrets replaced with placeholders. Total prompt size displayed.

**Narration cue**: "The AI is going to get the full codebase. Every function, every query, every import. Just not the values that could be weaponized."

---

## BLOCK 5 — Paste prompt to AI, show the response

This block is pre-recorded or live depending on your setup.

**What the AI should find** (these are in the code — the AI will find them):

| # | Severity | Finding | File | Line |
|---|----------|---------|------|------|
| 1 | Critical | SQL Injection — string-formatted query | src/app.py | 94 |
| 2 | Critical | SQL Injection — shipment lookup | src/app.py | 153 |
| 3 | Critical | SQL Injection — admin user search | src/app.py | 181 |
| 4 | Critical | SQL Injection — status filter | src/database.py | ~95 |
| 5 | Critical | Passwords logged in plaintext | src/app.py | 107 |
| 6 | High | Stripe webhook signature verification disabled | src/app.py | ~159 |
| 7 | High | No authorization check on /admin/users | src/app.py | ~177 |
| 8 | High | No rate limiting on /auth/login | src/app.py | ~99 |
| 9 | High | No rate limiting on /notifications/sms | src/app.py | ~155 |
| 10 | High | /notifications/sms requires no auth | src/app.py | ~155 |
| 11 | Medium | Internal services called over HTTP | src/app.py | ~52,54 |
| 12 | Medium | CORS configured to allow all origins | src/app.py | ~31 |
| 13 | Medium | debug=True in production FastAPI config | src/app.py | ~24 |
| 14 | Medium | health endpoint exposes infrastructure details | src/app.py | ~196 |
| 15 | Low | JWT tokens don't rotate on login | src/app.py | ~111 |

**If the AI misses any**: that's fine. Even 8-10 findings is a compelling demo.

---

## BLOCK 6 — Ask AI to fix the SQL injection

After seeing the audit results, follow up:

```bash
localmask mask-prompt "Based on the audit findings, rewrite the login endpoint in src/app.py to: 1) use parameterized queries (not string formatting), 2) remove the password from the debug log, 3) add a Redis-based rate limiter (max 5 attempts per IP per minute). Use the existing Redis connection at ~[REDIS_URL_0]~. Show the complete updated login function."
```

**Expected**: AI returns fixed login function. ~[NER_PERSON_5]~ URL placeholder is preserved in the response.

---

## BLOCK 7 — Rehydrate the fix

```bash
localmask rehydrate-answer "PASTE_AI_RESPONSE_HERE"
```

**Expected output**:
```
Rehydrating response...

  Replaced 3 placeholders with real values.
  ~[REDIS_URL_0]~ → ~[REDIS_URL_0]~
  ~[JWT_SIGNING_KEY_0]~ → shipfast-prod-jwt-!7kP#mNxQ2vRtZ9wY-HS256
  ~[DB_CONN_0]~ → ~[DATABASE_URL_0]~

Output written to: .localmask/rehydrated/response_<timestamp>.py
```

---

## BLOCK 8 — Show the before/after (closing shot)

```bash
# Show the vulnerable original
grep -A5 "async def login" src/app.py | head -10
# Shows: logger.debug(password), string-formatted SQL

# Show the fixed version (from rehydrated output)
cat .localmask/rehydrated/response_*.py | head -30
# Shows: parameterized query, no password logging, rate limiter
```

---

---

# TROUBLESHOOTING

## "localmask: command not found"
```bash
pip install localmask
# or
pip3 install localmask
# then verify:
localmask --version
```

## Scan finds 0 detections
```bash
# Check you're in the right directory
pwd  # should be localmask-demo-app/

# Check the files have content
cat src/app.py | grep sk_live
# If empty: the files need to be re-created from the repo
```

## Git hook not blocking the commit
```bash
# Check hook is executable
ls -la .git/hooks/pre-commit
# Should show: -rwxr-xr-x

# If not executable:
chmod +x .git/hooks/pre-commit

# Verify hook content
head -5 .git/hooks/pre-commit
# Should show: #!/bin/sh and localmask command
```

## Rehydrate command fails
```bash
# Make sure the scan was approved first
localmask get-review-queue
# If any are pending, approve them:
localmask bulk-review --action approve

# Then retry rehydrate
```

## AI response doesn't contain placeholders
This means the AI replaced the placeholders with invented values — common with some models.
Fix: add "Preserve every ~[TOKEN]~ placeholder exactly as-is" to your prompt.

## Multiple scan IDs in queue
```bash
# List all scans
localmask get-review-queue

# You can filter by the most recent scan — LocalMask will show timestamps
```

---

---

# VIDEO 4 — THE CLOUD AI AGENT
## "I connected my private codebase to an Azure AI agent — safely"

---

## SETUP (run once before recording — not on camera)

```bash
# Install demo dependencies
pip install -r requirements.demo.txt

# Copy and fill in .env.demo
cp .env.demo.example .env.demo
# Edit .env.demo — add ANTHROPIC_API_KEY at minimum
# (Azure vars optional — --platform claude works without Azure)

# Verify the demo script loads correctly
python src/cloud_agent_demo.py --help
# Expected: usage info with all three tasks listed

# Do a dry run of the task you'll record (so output is cached in your head)
python src/cloud_agent_demo.py --task security-audit --platform claude
# Expected: streams a full security audit report to terminal
```

---

## BLOCK 1 — Show the codebase (0:20–1:00)

```bash
# Open src/app.py in VS Code — scroll from top to show credentials
# Then switch to terminal:
ls -la src/ config/
```

Expected output:
```
src/app.py
src/database.py
src/ai_generated_checkout.py
src/cloud_agent_demo.py
config/settings.py
```

---

## BLOCK 2 — Scan (1:00–1:30)

```bash
localmask scan . --sensitivity strict
```

Expected output (shortened):
```
Scanning: /Users/shaig/Downloads/localmask-demo-app
  src/app.py ................ 18 detections
  src/database.py ........... 6 detections
  config/settings.py ........ 17 detections
  src/ai_generated_checkout.py 6 detections

Total: 47 secrets detected
Scan ID: scan-xxxxxxxx-xxxx
```

```bash
# Copy the scan ID — you'll need it several times
export SCAN_ID=scan-xxxxxxxx-xxxx
echo $SCAN_ID
```

---

## BLOCK 3 — Review detections (1:30–1:50)

```bash
localmask get-detections $SCAN_ID
```

Expected: table of all 47 detections with TYPE, FILE, LINE, PLACEHOLDER columns

```bash
# Approve all detections (or use the VS Code extension review panel)
localmask approve-all $SCAN_ID
```

---

## BLOCK 4 — Publish masked repo (1:50–2:30)

```bash
localmask publish $SCAN_ID \
  --target-url https://github.com/~[GIT_REMOTE_URL_0]~ \
  --private
```

Expected:
```
[OK] Masked repo published: https://github.com/~[GIT_REMOTE_URL_0]~
     47 secrets replaced with ~[TOKEN]~ placeholders
     0 real values in published repo
```

**[Switch to browser — open GitHub masked repo]**
**[Navigate to src/app.py — zoom in on stripe.api_key line]**

```python
# What GitHub shows:
stripe.api_key = "~[STRIPE_SECRET_KEY_0]~"
```

---

## BLOCK 5 — Run the cloud agent (2:45–4:30) ← MONEY SHOT

### Option A: Using Anthropic Claude API (no Azure needed)

```bash
python src/cloud_agent_demo.py \
  --task security-audit \
  --platform claude
```

### Option B: Using Azure AI Foundry (enterprise demo)

```bash
python src/cloud_agent_demo.py \
  --task security-audit \
  --platform azure
```

Expected output (streams to terminal):
```
════════════════════════════════════════════════════════════
  LocalMask ~[NER_PERSON_1]~
  Task     : ~[NER_PERSON_0]~
  Platform : CLAUDE
  Codebase : ShipFast SaaS (masked — no real secrets)
════════════════════════════════════════════════════════════

⚠️  The code passed to the AI has ALL secrets replaced with
   ~[TOKEN]~ placeholders. Real credentials never leave this machine.

[1/3] Fetching masked code...
  [+] Loaded src/app.py (9842 chars)
  [+] Loaded src/database.py (5210 chars)
  [+] Loaded config/settings.py (4891 chars)
  [+] Loaded src/ai_generated_checkout.py (6103 chars)
[2/3] Sending to Claude...
[3/3] Streaming response...

────────────────────────────────────────────────────────────
# ShipFast Security Audit Report

## Summary
6 Critical | 4 High | 3 Medium | 2 Low

---
## CRITICAL: SQL Injection — /auth/login (src/app.py:150)
...
```

---

## BLOCK 6 — Show the report (4:30–4:50)

```bash
# See what was saved
ls agent-output/
# Expected: security-audit-claude-YYYYMMDD-HHMMSS.md

# Preview the report
head -60 agent-output/security-audit-claude-*.md
```

---

## BLOCK 7 — Run the refactor task (4:50–5:20)

```bash
python src/cloud_agent_demo.py \
  --task refactor-dotenv \
  --platform claude
```

Expected: streams the refactored files + .env.example with ~[TOKEN]~ placeholders

---

## BLOCK 8 — Rehydrate (5:20–5:40)

```bash
localmask rehydrate $SCAN_ID \
  agent-output/refactor-dotenv-claude-*.md
```

Expected:
```
[OK] Rehydrated: agent-output/refactor-dotenv-claude-*.md
     47 placeholders restored with real values
     Output saved locally — never transmitted
```

---

## BLOCK 9 — Sync and close (5:40–6:00)

```bash
# Show the sync command for CI/CD integration
bash ~/.localmask/cloud-connections/sync-*.sh
```

Expected:
```
Syncing masked repo (scan: scan-xxxxxxxx-xxxx)...
Sync complete. Masked repo is up-to-date.
All cloud-connected agents will see the latest masked code.
```

---

## TROUBLESHOOTING — Video 4

| Problem | Fix |
|---------|-----|
| `anthropic not installed` | `pip install anthropic` |
| `ANTHROPIC_API_KEY not set` | Add to `.env.demo` |
| Slow streaming | Use `--platform claude` for consistent speed on camera |
| Azure auth error | Run `az login` first, or switch to `--platform claude` |
| No files loaded | Make sure cwd is `localmask-demo-app/` |
| Empty agent-output/ | Check `.env.demo` has API key filled in |

---

# TIMING REFERENCE

| Video | Block | ~[NER_PERSON_2]~ |
|-------|-------|----------------|
| Video 1 | Hook + Show problem | 0:00–1:00 |
| Video 1 | Name the catch-22 | 1:00–1:45 |
| Video 1 | Install + scan | 1:45–2:30 |
| Video 1 | Review detections | 2:30–3:00 |
| Video 1 | Generate masked prompt (REVEAL) | 3:00–4:15 |
| Video 1 | AI does the refactor | 4:15–4:50 |
| Video 1 | Rehydrate + close | 4:50–5:50 |
| — | — | — |
| Video 2 | Hook + show AI file | 0:00–1:00 |
| Video 2 | Name the danger | 1:00–1:45 |
| Video 2 | Install git hook | 1:45–2:15 |
| Video 2 | Stage file | 2:15–2:30 |
| Video 2 | Blocked commit (REVEAL) | 2:30–3:30 |
| Video 2 | Fix + clean commit | 3:30–5:00 |
| Video 2 | Close | 5:00–5:30 |
| — | — | — |
| Video 3 | Hook + show vulnerabilities | 0:00–1:00 |
| Video 3 | Why this is hard | 1:00–1:30 |
| Video 3 | Scan + approve | 1:30–2:15 |
| Video 3 | Build audit prompt | 2:15–3:00 |
| Video 3 | AI audit results (REVEAL) | 3:00–4:30 |
| Video 3 | Ask for fixes + rehydrate | 4:30–5:00 |
| Video 3 | Close | 5:00–5:30 |
| — | — | — |
| Video 4 | Hook + show codebase | 0:00–1:00 |
| Video 4 | Scan + review + publish | 1:00–2:30 |
| Video 4 | ~[NER_PERSON_3]~ tour | 2:30–2:45 |
| Video 4 | Run cloud agent (REVEAL) | 2:45–4:30 |
| Video 4 | Show report + refactor task | 4:30–5:20 |
| Video 4 | Rehydrate + sync + close | 5:20–6:00 |
