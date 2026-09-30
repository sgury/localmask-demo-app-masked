# Demo Video Script — LocalMask Cloud Connect
### "Connect your private code to AI — without exposing a single secret"

**Runtime**: ~8 minutes | **Format**: Screen recording in VS Code

---

## BEFORE YOU RECORD

### Setup checklist
- [ ] Open VS Code with `localmask-demo-app/` as the workspace
- [ ] Install LocalMask VS Code extension (Marketplace)
- [ ] Font size bumped to 16–18 for readability
- [ ] Terminal open at the bottom (split view)
- [ ] Browser tab open on Azure AI Foundry (ai.azure.com) — logged in
- [ ] ~[NER_PERSON_7]~/notifications (~[NER_PERSON_6]~ on)
- [ ] Screen resolution: 1920×1080 or 2560×1440

---

## SCENE 1 — The Problem (0:00–1:00)

**[Show `src/app.py` open in VS Code, scroll slowly from top]**

> "This is a real SaaS backend. It processes payments, manages users,
> talks to a dozen services. And like most real codebases — it has
> secrets everywhere."

**[Pause on the Stripe key line]**

> "Stripe live keys. Database passwords. JWT signing secrets.
> AWS credentials. OpenAI keys."

**[Scroll to `config/settings.py`]**

> "Twilio, HubSpot, Sentry, Datadog — more secrets in the config."

**[Scroll to `.env`]**

> "And the .env file — the one that's supposed to never be committed —
> full of production credentials."

**[PAUSE — look at camera or take a breath]**

> "Now — imagine you want an AI agent to review this code.
> Find the bugs. Suggest improvements. Help your team move faster.
> You'd have to hand all of this to a cloud platform.
> Every key. Every password. Every token."

> "That's the problem LocalMask solves."

---

## SCENE 2 — The Solution (1:00–1:45)

**[Open integrated terminal in VS Code]**

> "LocalMask sits between your code and any AI platform.
> It scans your repo, replaces every secret with a safe placeholder,
> and publishes a masked copy that's safe to share."

> "The real values never leave your machine."

**[Type the scan command]**

```bash
localmask scan . --sensitivity strict
```

> "We're scanning with strict sensitivity — that catches not just
> API keys and passwords, but also internal URLs, org identifiers,
> and infrastructure details."

**[Watch the output scroll — detections appearing]**

> "Watch it go. Stripe keys... database credentials... JWT secrets...
> AWS keys... OpenAI... SendGrid... Slack... Twilio..."

**[Scan completes — show the summary table]**

> "47 secrets detected across 4 files. Every single one of them
> flagged before anything leaves this machine."

---

## SCENE 3 — Review Detections (1:45–2:30)

**[Run detections review]**

```bash
localmask get-detections <scan_id>
```

> "Before we publish anything, we review. This is the approval gate."

**[Show the review table — highlight different secret types]**

> "Each detection shows the type, where it was found, and the
> placeholder it'll be replaced with."

> "~[STRIPE_KEY_0]~... ~[DB_CONNECTION_0]~... ~[JWT_SECRET_0]~...
> ~[AWS_ACCESS_KEY_0]~..."

> "If anything is a false positive — say, a public API URL that
> doesn't need masking — you reject it here. Everything else
> gets approved."

---

## SCENE 4 — The Masked Repo (2:30–3:30)

**[Publish the masked repo]**

```bash
localmask publish <scan_id> \
  --target-url https://github.com/~[GIT_REMOTE_URL_1]~ \
  --private
```

> "Now we publish. LocalMask pushes a clean copy to a private
> GitHub repo — with every secret replaced."

**[Switch to browser — open the masked repo on GitHub]**

> "Here's what the AI will see."

**[Navigate to `src/app.py` in the masked GitHub repo]**

> "The code is 100% intact. Structure, logic, variable names,
> comments — everything the AI needs to understand and analyze."

> "But look here — where the Stripe key was..."

**[Zoom in on a masked line]**

```python
stripe.api_key = "~[STRIPE_KEY_0]~"
```

> "A placeholder. Opaque. Meaningless to anyone outside this machine."

**[Scroll through a few more masked lines]**

> "Database connection — masked.
> JWT secret — masked.
> AWS credentials — masked.
> OpenAI key — masked."

> "The AI gets everything it needs. Your secrets go nowhere."

---

## SCENE 5 — Cloud Setup (3:30–5:00)

**[Switch back to VS Code terminal]**

> "Now we connect this masked repo to an AI platform.
> That's where `localmask-cloud-connect` comes in."

```bash
./localmask-cloud-connect.sh
```

> "This wizard provisions everything — service principals,
> IAM roles, storage — with least-privilege permissions."

**[Walk through the prompts, narrating each choice]**

- Repo path → `.` (current project)
- Masked repo → `payflow-masked`
- Permission → **READ-WRITE** _(we want the AI to suggest fixes)_
- Write target → **Cloud storage** _(agent outputs go to ~[NER_PERSON_10]~)_
- Platforms → **Azure AI Foundry** _(for this demo)_
- Sensitivity → **strict**

**[Wizard runs — show the output scrolling]**

> "The wizard generates a provisioning script. Let's run it."

```bash
bash ~/.localmask/cloud-connections/azure-*.sh
```

> "Creating a service principal with Reader access — scoped only
> to this resource group. Not admin. Not subscription-wide.
> Just what it needs."

**[Switch to Azure portal tab]**

> "And here in Azure AI Foundry — the connection to our masked repo
> just appeared. The agent can now read our code."

---

## SCENE 6 — AI Agent in Action (5:00–6:30)

**[~[NER_PERSON_12]~ AI Foundry — open the Agents panel]**

> "We have an agent connected to our masked codebase.
> Let's ask it something real."

**[Type into the agent chat]**

```
Review the payment processing logic in src/app.py.
Are there any error handling gaps or security issues?
```

**[Agent responds — show the response]**

> "The agent reads the full code... understands the Stripe integration...
> the database queries... the authentication flow..."

> "And it found a real issue — the charge endpoint doesn't validate
> the token parameter before passing it to Stripe. A bad actor could
> inject a malformed value."

> "And notice — the agent's response references the code accurately.
> It talks about the structure, the logic, the patterns.
> It doesn't need to see 'sk_live_51Nx...' to do its job."

**[Ask a second question]**

```
Generate a fix for the token validation issue and
add input validation to all payment endpoints.
```

**[Agent generates the fixed code — with masked placeholders intact]**

> "The fix comes back. The agent preserved every placeholder exactly.
> ~[STRIPE_KEY_0]~ is still ~[STRIPE_KEY_0]~."

---

## SCENE 7 — Rehydration (6:30–7:15)

**[In VS Code terminal]**

> "The AI suggested a fix. Now we apply it to our real codebase —
> with real values restored."

```bash
localmask rehydrate <fix_output_file>
```

> "LocalMask substitutes every placeholder back to its real value —
> locally, on this machine. The fix is ready to review and merge."

**[Show the rehydrated file — real values are back]**

> "~[NER_PERSON_8]~ key. Real database connection. Ready for a PR."

> "The AI fixed our code. It never saw a single credential."

---

## SCENE 8 — VS Code Integration (7:15–7:45)

**[Back in VS Code — open the LocalMask extension panel]**

> "And because we set up the VS Code integration —
> this is part of the everyday workflow."

> "Every time you save a file, LocalMask checks for new secrets.
> If it finds one, it flags it inline before it can be accidentally
> committed or shared."

**[Show the sync status in the status bar]**

> "The status bar shows when the masked repo is in sync.
> One click to push the latest masked version."

> "Your team codes normally. LocalMask works in the background.
> AI agents always see a clean, current, masked copy."

---

## SCENE 9 — Closing (7:45–8:00)

**[Show the project structure in VS Code sidebar]**

> "To recap:
> Your code stays private.
> Your secrets stay local.
> Your AI agents get full context.
> And your team moves faster — without the risk."

> "LocalMask. Your code, your secrets, your control."

**[Fade out]**

---

## RECORDING TIPS

- **Pace**: Slow down at key moments — especially the masking reveal (Scene 4)
- **Zoom**: Use VS Code's `Ctrl+=/Cmd+=` to zoom in on important lines
- **Highlights**: Select the secret values briefly before they get masked — let viewers see the contrast
- **Terminal font**: Use a large, clear monospace font (JetBrains Mono or ~[NER_PERSON_11]~)
- **Mouse**: Move deliberately — fast mouse movements are hard to follow on screen recordings
- **Retakes**: Scene 4 (the GitHub masked repo reveal) and Scene 6 (agent response) are your money shots — get multiple takes

## THUMBNAIL IDEAS

- Split screen: left = code with red-highlighted real secrets, right = code with `~[TOKEN]~` placeholders
- Text overlay: "Your AI can see your code. But not your secrets."
- Before/after of a single code line

## TITLES TO A/B TEST

- "Connect GitHub to Azure AI — without exposing secrets"
- "How to safely give AI access to your private code"
- "LocalMask: The privacy layer every AI dev workflow needs"
- "~[NER_PERSON_9]~ keys are safe. Your AI still works. Here's how."
