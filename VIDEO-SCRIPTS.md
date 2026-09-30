# LocalMask Video Scripts — ~[SERVER_HOSTNAME_2]~ Series
### Three Scenarios. Three Videos. Zero Leaked Secrets.

---

## BEFORE YOU RECORD — GLOBAL CHECKLIST

- [ ] Terminal font: JetBrains Mono or ~[NER_PERSON_11]~, size 16+
- [ ] VS Code font size bumped to 16 (Cmd+= three times)
- [ ] ~[NER_PERSON_6]~ ON — no Slack popups mid-take
- [ ] Screen resolution: 1920×1080 or 2560×1440
- [ ] LocalMask installed and licensed: `localmask license status`
- [ ] Repo at `/Users/shaig/Downloads/localmask-demo-app` open in VS Code
- [ ] All four src/config files visible in the sidebar
- [ ] Terminal split at bottom, cwd = project root
- [ ] Get multiple takes of every "reveal" moment — those are your money shots

---

---

# VIDEO 1 — "The Catch-22"
### Scenario 1: ~[SERVER_HOSTNAME_2]~ wants AI to refactor hardcoded secrets into .env — but can't share the code because the code HAS the secrets in it.

**Estimated runtime**: 5–6 minutes
**Format**: Terminal + VS Code screen recording, talking-head optional intro

---

## TITLE OPTIONS

1. **"The AI Catch-22 ~[NER_PERSON_23]~ (~[NER_PERSON_51]~ to ~[NER_PERSON_49]~)"** — curiosity gap, broad
2. **"~[NER_PERSON_25]~. AI ~[NER_PERSON_43]~. But I Can't Show AI the Code."** — states the problem perfectly
3. **"How to ~[NER_PERSON_44]~ AI to ~[NER_PERSON_13]~"** — SEO, very searchable
4. **"29 ~[NER_PERSON_20]~ on GitHub in 2025. Here's the Fix."** — statistic hook
5. **"LocalMask: ~[NER_PERSON_21]~ AI ~[NER_PERSON_26]~"** — brand-first

**Recommended**: Title #3 for SEO traction, Title #1 for curiosity clicks. A/B test both.

## THUMBNAIL CONCEPT

Split screen, high contrast:
- LEFT: `app.py` open, Stripe key `~[STRIPE_SECRET_KEY_3]~` highlighted in red, label: "What AI needs to see"
- RIGHT: same file, key replaced with `~[STRIPE_KEY_0]~` highlighted in green, label: "What AI actually sees"
- Bottom text: "Your code. AI's problem. Zero leaked keys."
- Dark background, bold sans-serif font

## BEST SUBREDDITS

- r/programming — broad reach, good for "how-to" framing
- r/webdev — practical devs who deal with this daily
- r/~[SERVER_HOSTNAME_3]~ — infrastructure angle, secrets management
- r/Python — specific to the Python FastAPI demo
- r/SideProject — if framed as a tool discovery
- r/netsec — security angle on the 29M statistic

---

## SCRIPT

### HOOK — 0:00 to 0:15

**[Screen: VS Code open on `src/app.py`. Scroll slowly. Stripe key is visible on screen.]**

> "Quick question. You've got hardcoded secrets in your codebase — API keys, database
> passwords, all the usual stuff. And you want AI to help you clean it up. Move everything
> to environment variables. Standard refactor.
>
> Here's the problem: to get AI to help, you have to *show* AI the code.
> But the code has your production Stripe key in it.
> So you can't show it to AI.
> But you can't fix it without AI because it's everywhere.
>
> That's the catch-22. Let me show you how to break it."

---

### SCENE 1 — Show the Problem — 0:15 to 1:00

**[Stay on `src/app.py`. Scroll from the top slowly.]**

> "This is ShipFast — a shipping SaaS backend. It's a real production app.
> And like basically every codebase that started as a side project and grew into
> something real — the secrets are everywhere."

**[Pause on the Stripe key line. Click to highlight it.]**

> "Stripe production key. Hardcoded. Line 28.
> Right there in the source file."

**[Slowly scroll down.]**

> "AWS credentials. JWT signing secret. Redis password. Twilio auth token.
> SendGrid API key. Three separate database connection strings."

**[Open `config/settings.py` in a tab]**

> "And then there's the config file. Which is... more of the same.
> Fifteen secrets across payments, email, monitoring, carriers.
> Every one of them hardcoded with a little TODO comment that's been
> sitting there since the first sprint."

**[Zoom in on a TODO comment]**

> "'TODO: move to env.' Classic. We've all written that comment.
> We've all left it there for three months."

---

### SCENE 2 — Name the Catch-22 — 1:00 to 1:45

**[Switch to a text editor or just narrate over the code]**

> "So here's the workflow you'd normally want:
>
> Step 1 — open Cursor or Claude or ChatGPT.
> Step 2 — paste the code.
> Step 3 — say 'move all these hardcoded values to environment variables.'
> Step 4 — AI gives you the refactored code plus a clean .env file.
> Step 5 — done in 10 minutes.
>
> Except you can't do Step 2.
> Because pasting this code means pasting `~[STRIPE_SECRET_KEY_3]~` into a cloud model.
> That key is live. That key authorizes real charges on your production Stripe account.
>
> So you either don't use AI — and spend two hours doing a boring refactor manually.
> Or you use AI — and your production key is sitting in OpenAI's API logs."

**[Pause for emphasis.]**

> "Neither of those options is good. And this is the exact moment that
> 29 million secrets got leaked on GitHub in 2025. Not because ~[SERVER_HOSTNAME_1]~
> are careless. Because the tooling put them in a no-win situation."

---

### SCENE 3 — Install and Scan — 1:45 to 2:30

**[Switch to terminal]**

> "LocalMask breaks the loop. Here's how it works in about 60 seconds."

**[Type the scan command]**

```bash
localmask scan .
```

**[Watch output scroll — secrets being detected]**

> "It's scanning every file in the project. Looking for secrets, credentials,
> connection strings, anything that shouldn't leave this machine.
>
> There's the Stripe key. The database passwords. JWT secret. AWS credentials.
> Twilio. SendGrid. Redis. All of them."

**[Scan completes — summary table appears]**

> "Done. 47 detections across 4 files.
> And none of that just left your machine — we haven't published anything yet.
> This is just the detection pass."

---

### SCENE 4 — Review the Detections — 2:30 to 3:00

> "Before we do anything, we can review exactly what got flagged."

**[Run the review command with the scan ID from the previous output]**

```bash
localmask get-review-queue
```

**[Table appears with secret types, file locations, placeholder names]**

> "Each detection shows the secret type, which file it's in, and the
> placeholder it'll be replaced with. `~[STRIPE_KEY_0]~`. `~[URL_EMBEDDED_PASSWORD_0]~`.
> `~[JWT_SECRET_0]~`.
>
> If anything is a false positive — some public URL that got flagged —
> you reject it here. Everything legit gets approved.
> In this case, everything looks right, so we approve the whole queue."

**[Approve the scan]**

```bash
localmask approve-scan <scan_id>
```

---

### SCENE 5 — THE REVEAL — Masked Prompt — 3:00 to 4:15

**[This is the money shot. Slow down. Let it breathe.]**

> "Now here's where it gets interesting.
>
> Instead of pasting the raw code into your AI — which would expose every secret —
> you use LocalMask to create the prompt."

**[Type the mask-prompt command]**

```bash
localmask mask-prompt "Refactor all hardcoded credentials in src/app.py and config/settings.py into environment variables. Create a .env.example file with placeholder values and update all references to use os.getenv()."
```

**[Watch the masked prompt appear in the output]**

> "Look at what just happened.
>
> LocalMask attached the code to the prompt — but every secret is now a placeholder.
> `~[STRIPE_KEY_0]~`. `~[URL_EMBEDDED_PASSWORD_0]~`. `~[JWT_SECRET_0]~`.
>
> The AI gets the full code. It sees the structure, the imports, the function names,
> the comments, everything it needs to do the refactor.
>
> But it doesn't see `~[STRIPE_SECRET_KEY_3]~`
> It doesn't see `Tr0ubl3d!Pass#92xK`.
> It doesn't see a single real credential."

**[Pause. Let this land.]**

> "You just broke the catch-22.
> The AI can now help you with the refactor.
> And your production keys never left your machine."

---

### SCENE 6 — AI Does the Refactor — 4:15 to 4:50

**[Show the AI response — either pre-recorded or a real interaction]**

> "The AI does exactly what you asked. It refactors every hardcoded value
> into an os.getenv() call. It writes a .env.example with the placeholder names.
> And crucially — it preserved every LocalMask placeholder exactly."

**[Highlight a line in the AI output]**

> "`stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '~[STRIPE_KEY_0]~')`
>
> That placeholder is still there. The AI didn't try to fill in a key.
> It worked with the masked values exactly as intended."

---

### SCENE 7 — Rehydrate — 4:50 to 5:30

**[Back to terminal]**

> "Last step. The AI gave us the refactored code with placeholders.
> We want to apply it to our actual codebase with real values restored."

**[Run rehydrate]**

```bash
localmask rehydrate-answer "<paste the AI response here>"
```

**[Output shows the rehydrated code]**

> "LocalMask substitutes every `~[STRIPE_KEY_0]~` back to the real value —
> locally, on this machine, offline, no network call.
>
> The refactored file is ready. Real keys. Clean code. os.getenv() everywhere."

**[Show the before/after in VS Code — two tabs side by side if possible]**

> "Before: `stripe.api_key = '~[STRIPE_SECRET_KEY_3]~'`
> After: `stripe.api_key = os.getenv('STRIPE_SECRET_KEY')`
>
> Same key. Different risk profile. The AI did the work."

---

### CLOSING — 5:30 to 5:50

**[Terminal visible, VS Code in background]**

> "The catch-22 only exists if you let it.
>
> LocalMask is a local process — no cloud, no accounts for the basic workflow,
> no data leaving your machine. Install it, run a scan, and your AI workflow
> stays private.
>
> Link in the description. If this saved you from a very bad day,
> hit like — it genuinely helps."

**[Fade out]**

---

---

# VIDEO 2 — "AI Hardcoded My Key"
### Scenario 4: ~[SERVER_HOSTNAME_2]~ asks Cursor to add Stripe payments. AI helpfully copies the production key straight into the code. LocalMask catches it before the commit.

**Estimated runtime**: 5–6 minutes
**Format**: VS Code + terminal, showing the git pre-commit hook catching the secret

---

## TITLE OPTIONS

1. **"~[NER_PERSON_15]~ ~[NER_PERSON_45]~. Here's ~[STRIPE_SECRET_KEY_4]~."** — specific, alarming, accurate
2. **"AI-~[NER_PERSON_16]~ at 2× the Rate. Here's the Fix."** — statistic-first
3. **"Your AI ~[NER_PERSON_17]~ a ~[NER_PERSON_29]~"** — provocative
4. **"~[NER_PERSON_31]~ Every AI-~[NER_PERSON_24]~"** — practical/tooling angle
5. **"I Let AI Write the ~[NER_PERSON_38]~. ~[NER_PERSON_28]~ API Key."** — first-person narrative

**Recommended**: Title #1 is the strongest — it's specific, it names the tool, and it's alarming enough to click. Title #2 is good for LinkedIn.

## THUMBNAIL CONCEPT

Terminal output showing a git commit being blocked:
```
✗ COMMIT BLOCKED
  src/ai_generated_checkout.py: STRIPE_KEY detected
  ~[STRIPE_SECRET_KEY_3]~ → ~[STRIPE_KEY_0]~
```
Red background on the blocked line, green on the masked line.
Text overlay: "Cursor hardcoded my key. This caught it."

## BEST SUBREDDITS

- r/programming — the AI-coding-assistants angle is very current
- r/cursor — directly relevant community
- r/ChatGPTCoding — large, active
- r/netsec — the stat about AI-assisted leaks is a hook
- r/~[SERVER_HOSTNAME_3]~ — git hook / secrets management angle
- r/ExperiencedDevs — skeptics of AI-generated code, great engagement

---

## SCRIPT

### HOOK — 0:00 to 0:15

**[Screen: Show `src/ai_generated_checkout.py` open in VS Code. Scroll to the hardcoded key line.]**

> "This file was generated by Cursor. I asked it to add a Stripe checkout flow
> to my app. It did a great job — clean code, good structure, handles webhooks,
> manages subscriptions.
>
> And on line 21, it hardcoded my production Stripe API key.
>
> Not a test key. The live one. Straight from the codebase it had access to.
> Because it was trying to be helpful.
>
> Let me show you how LocalMask catches this before it becomes a very expensive lesson."

---

### SCENE 1 — Show the AI-Generated File — 0:15 to 1:00

**[Open `src/ai_generated_checkout.py` in VS Code]**

> "Here's the file. Cursor generated it on September 18th — you can see the
> comment at the top. And honestly, the code is good. It handles the checkout
> session, the ~[SERVER_HOSTNAME_SQL_1]~ portal, the webhooks. It even validates Stripe signatures
> properly — which a lot of ~[SERVER_HOSTNAME_1]~ skip."

**[Scroll down to line 21]**

> "But here. Line 21.
>
> `STRIPE_API_KEY = '~[STRIPE_SECRET_KEY_1]~'`
>
> And the comment above it: 'Using your API key from the codebase.'
>
> Cursor found the key in `src/app.py`, which was already open in the workspace.
> It copied it into the new file to make the code runnable. Because that's what
> it was trying to do. It was being helpful.
>
> This is not Cursor being malicious. This is Cursor being Cursor.
> The model doesn't distinguish between 'this is a real production key'
> and 'this is a string I should preserve.' It sees text. It copies text."

---

### SCENE 2 — The Danger — 1:00 to 1:45

**[Switch to a split terminal, show a git log or file listing]**

> "Now imagine the normal workflow here.
>
> You review the file. The code looks clean. You see the Stripe key —
> but you recognize it. It's your key. You put it in app.py.
> So your brain registers it as correct and moves on.
>
> You run `git add src/ai_generated_checkout.py`.
> You run `git commit -m 'add stripe checkout flow'`.
> You push to GitHub.
>
> And now your live Stripe key is in your git history.
> Forever. Even if you delete the file, it's in the history.
>
> Stripe rotates it when they catch it — but the window between push and rotation
> is where someone drains your account.
>
> AI-assisted codebases leak secrets at twice the rate of human-written code.
> Not because ~[SERVER_HOSTNAME_1]~ are less careful. Because the AI introduces content
> it found in context — and ~[SERVER_HOSTNAME_1]~ trust AI output more than they should."

---

### SCENE 3 — Set Up the Git Hook — 1:45 to 2:15

**[Terminal, project root]**

> "The fix is a pre-commit hook that runs LocalMask before every commit.
> One command."

**[Type the setup command]**

```bash
localmask setup-git-hook
```

**[Output shows the hook being installed]**

> "That's it. LocalMask just installed a pre-commit hook in this repo's
> `.git/hooks/` directory. From this point on, every `git commit` runs
> a LocalMask scan first.
>
> If it finds a secret — any secret — the commit is blocked.
> You see exactly what was found and where.
> You fix it. Then you commit."

---

### SCENE 4 — THE REVEAL — Trigger the Hook — 2:15 to 3:30

**[This is the main moment. Slow down. Let the output speak.]**

**[Stage the file as if committing normally]**

```bash
git add src/ai_generated_checkout.py
```

```bash
git commit -m "add stripe checkout flow"
```

**[The pre-commit hook fires. Output appears. Commit is blocked.]**

> "Watch what happens."

**[Hook output scrolls — shows the detection]**

```
Running LocalMask pre-commit scan...

  SECRETS DETECTED — commit blocked

  File: src/ai_generated_checkout.py
    Line 21 — STRIPE_SECRET_KEY
    Value: ~[STRIPE_SECRET_KEY_1]~ → ~[STRIPE_KEY_0]~

  File: src/ai_generated_checkout.py
    Line 25 — STRIPE_WEBHOOK_SECRET
    Value: whsec_9mK3nPpX8vLqS5... → ~[STRIPE_WEBHOOK_1]~

  2 secrets found. Commit blocked.
  Run: localmask review to see all detections.
  Run: git commit --no-verify to override (not recommended).

Aborting commit.
```

**[Pause. Let that output sit for two full seconds.]**

> "Blocked.
>
> Two secrets detected. ~[NER_PERSON_4]~ key and the webhook secret.
> Both hardcoded in the AI-generated file. Both caught before the push.
>
> And notice — the output tells you exactly what to do next.
> It shows you the placeholder each secret will be replaced with.
> It even tells you how to override if you're absolutely sure it's a false positive —
> but it makes you do that consciously. You can't accidentally commit a secret."

---

### SCENE 5 — Fix It — 3:30 to 4:30

**[Back to VS Code — open the file]**

> "Now we fix the actual problem. We have two options:
>
> Option 1 — edit the file manually and replace the hardcoded keys
> with `os.getenv()` calls. Fine. A little tedious.
>
> Option 2 — ask AI to fix its own mistake. Using LocalMask."

**[Terminal]**

```bash
localmask mask-prompt "The file src/ai_generated_checkout.py has hardcoded Stripe credentials on lines 21 and 25. Replace them with os.getenv() calls using standard env variable names. Show me the corrected lines only."
```

**[Masked prompt is generated — AI can see the file structure but not the real key values]**

> "The prompt goes to the AI with the file attached — masked.
> The AI sees the placeholder `~[STRIPE_KEY_0]~` instead of the real key.
> It can still understand the context. It can still fix the problem.
> It just can't extract the value."

**[AI responds with the fix]**

> "And the fix comes back clean. `os.getenv('STRIPE_SECRET_KEY')`.
> `os.getenv('STRIPE_WEBHOOK_SECRET')`. Exactly right.
>
> The AI fixed the mistake it made — without ever seeing the real key values.
> Kind of poetic."

---

### SCENE 6 — Clean Commit — 4:30 to 5:00

**[Apply the fix, stage the file, try to commit again]**

```bash
git add src/ai_generated_checkout.py
git commit -m "add stripe checkout flow — keys via env vars"
```

**[Pre-commit hook runs again. This time: clean.]**

```
Running LocalMask pre-commit scan...
  No secrets detected. Proceeding with commit.
[main 3f8c2a1] add stripe checkout flow — keys via env vars
 1 file changed, 4 insertions(+), 2 deletions(-)
```

**[Commit succeeds.]**

> "Clean. No secrets. Commit goes through.
>
> The AI-generated code is in the repo. The credentials are not.
> And your git history doesn't have a six-month-old live Stripe key
> waiting to be found by a scanner."

---

### CLOSING — 5:00 to 5:30

**[Terminal with the clean commit visible]**

> "AI coding assistants are going to keep doing this.
> They're trained to produce runnable code, and runnable code needs credentials.
> They copy what they find in context. That's how they work.
>
> The hook doesn't slow you down — it takes about half a second.
> But it gives you a hard stop before the mistake becomes permanent.
>
> `localmask setup-git-hook`. One command. Run it in every repo you have
> an AI touching.
>
> Link in the description."

**[Fade out]**

---

---

# VIDEO 3 — "The Security Audit"
### Scenario 5: ~[SERVER_HOSTNAME_2]~ asks AI to find all security vulnerabilities. But the code is full of real credentials — sharing it exposes them. LocalMask lets the AI do a full audit without seeing a single real secret.

**Estimated runtime**: 5–6 minutes
**Format**: Terminal + VS Code + AI chat interface visible

---

## TITLE OPTIONS

1. **"I Asked AI to ~[NER_PERSON_39]~ for ~[NER_PERSON_35]~. Here's ~[NER_PERSON_40]~."** — outcome-first, curiosity gap
2. **"How to Get a Full AI ~[NER_PERSON_14]~ ~[NER_PERSON_32]~"** — how-to, practical
3. **"~[NER_PERSON_46]~ 4 ~[NER_PERSON_19]~. AI ~[NER_PERSON_36]~ — ~[NER_PERSON_18]~."** — specific, alarming
4. **"SQL Injection, ~[NER_PERSON_33]~, Passwords in Logs: AI ~[NER_PERSON_30]~"** — technical specifics
5. **"~[NER_PERSON_41]~ to Use AI for ~[NER_PERSON_22]~"** — authority positioning

**Recommended**: Title #1 drives the most clicks. Title #3 is strong if you want a more dramatic hook. Post title #3 on Reddit, title #1 on YouTube.

## THUMBNAIL CONCEPT

AI chat interface visible with a response listing vulnerabilities:
- "SQL Injection: line 94"
- "Credentials in logs: line 107"
- "No rate limiting on /auth/login"
Overlaid text: "4 critical issues found. Zero secrets leaked."
Red warning triangles on each item.

## BEST SUBREDDITS

- r/netsec — the target audience, strong engagement on practical demos
- r/webdev — broader reach
- r/programming — safe bet for any technical content
- r/AskNetsec — more question-oriented but discovery is good
- r/~[SERVER_HOSTNAME_3]~ — CI/CD security integration angle
- r/SoftwareEngineering — professional devs, good discussion

---

## SCRIPT

### HOOK — 0:00 to 0:15

**[Screen: VS Code, `src/app.py` open. Scroll past the credentials to the login function.]**

> "There are four critical security vulnerabilities in this codebase.
> SQL injection. Passwords logged to the console. No rate limiting on the
> login endpoint. Admin route with no role check.
>
> I know this because I asked AI to find them.
> And I'm about to show you how to do the same thing — without handing
> your production credentials to a language model.
>
> Because this file also has your Stripe key, your database password,
> and your JWT signing secret in it. And those need to stay local."

---

### SCENE 1 — Show the Codebase — 0:15 to 1:00

**[Slowly scroll through `src/app.py`]**

> "ShipFast. A shipping SaaS backend. Real production code.
> And it has real problems baked in — the kind that accumulate when a small
> team is moving fast and there's no security review in the sprint cycle.
>
> I'm not going to show you all of them right now — that's the AI's job.
> But I'll give you a hint."

**[Scroll to the login function — line 94]**

> "Line 94. Login endpoint. The email parameter goes straight into a
> string-formatted SQL query.
>
> `WHERE email = '{email}'`
>
> Not parameterized. Classic SQL injection.
> Send in `' OR '1'='1` and you're in.
> Your whole users table is exposed."

**[Scroll to the logging line]**

> "And a few lines up — `logger.debug(f'Login attempt: email={email}, password={password}')`
>
> Passwords. Logged. To the console. In production. With `DEBUG=True`.
> Which means they're going to whatever log aggregation system you have.
> Splunk, CloudWatch, Datadog — now your users' passwords are in your observability platform."

**[Scroll back up to show the credentials block]**

> "And all of this is in the same file as your Stripe production key,
> three database connection strings, your JWT secret, and your AWS credentials.
>
> So when you want to ask AI to find the security bugs — what do you do?
> You can't paste this file. You'd be including `~[STRIPE_SECRET_KEY_3]~`
> in your chat message."

---

### SCENE 2 — Why This Is Hard — 1:00 to 1:30

> "This is the friction that makes security reviews painful.
>
> The people who most need a security audit are the ones working on
> codebases that haven't had time for proper secrets hygiene yet.
> The code has both problems — vulnerabilities AND credentials — together.
>
> The standard advice is 'move your secrets to environment variables first,
> then do the audit.' Fine advice. But that's a separate project.
> And security issues don't wait for your tech-debt sprint.
>
> LocalMask lets you do both at the same time."

---

### SCENE 3 — Scan and Get Context — 1:30 to 2:15

**[Terminal, project root]**

> "Step one — scan the repo. This builds LocalMask's map of what's sensitive
> and what isn't. Everything it finds gets a placeholder."

```bash
localmask scan .
```

**[Output scrolls — detections accumulating]**

> "It's finding everything. All the expected suspects.
>
> Stripe key, webhook secret, three database connection strings,
> JWT secrets, AWS credentials, Redis password, SendGrid key,
> Twilio credentials, carrier API keys, monitoring tokens.
>
> Plus the internal HTTP service URLs — those count as infrastructure
> details you probably don't want in an AI's context window either."

**[Scan completes]**

> "54 detections across 4 files. Everything gets a placeholder.
> Now the repo is ready to share — or in this case, to query."

---

### SCENE 4 — Build the Audit Prompt — 2:15 to 3:00

**[Terminal]**

> "Now we build the security audit prompt. We're going to send the full
> codebase to an AI and ask for a complete vulnerability assessment."

```bash
localmask mask-prompt "You are a senior application security engineer. Perform a thorough security audit of this codebase. Identify all vulnerabilities across: injection attacks, authentication weaknesses, authorization gaps, insecure data handling, secrets management, logging and monitoring issues, and any missing security controls. For each finding, include: severity (Critical/High/Medium/Low), affected file and line number, description of the vulnerability, and recommended fix. Be specific and exhaustive."
```

**[Masked prompt is generated — shows the files will be attached]**

> "This generates a prompt that includes the full codebase content —
> but with every credential replaced by a placeholder.
>
> The AI is going to get everything it needs to find every vulnerability.
> The SQL injection. The logging problem. The rate limiting gaps.
> The signature verification that was commented out.
>
> It just won't get the Stripe key. Or the database passwords.
> Those stay here."

---

### SCENE 5 — THE REVEAL — AI Audit Results — 3:00 to 4:30

**[Show the AI's response — either pre-recorded or live. This is the key scene.]**

> "Here's what comes back."

**[Read through the findings with narration. Slow down. Let each one land.]**

> "Finding 1 — Critical — SQL Injection.
> `src/app.py` line 94, line 153, line 181.
> Three separate injection points. The login query, the shipment lookup,
> the admin user search. All three use string formatting instead of
> parameterized queries.
>
> The AI is right. That's a `' OR '1'='1` away from full database access."

**[Pause]**

> "Finding 2 — Critical — Credentials in application logs.
> Line 107. Password logged in plaintext on every login attempt.
>
> Also right. That one I put in there myself — and it's the kind of thing
> that looks innocuous until someone mentions that your log shipper
> is sending those to a third-party SaaS platform."

**[Continue scrolling through results]**

> "Finding 3 — High — No rate limiting on authentication endpoints.
> The login endpoint at `/auth/login` has no brute-force protection.
> An attacker can try passwords indefinitely.
>
> Finding 4 — High — Broken authorization on admin endpoint.
> `/admin/users` checks for a valid JWT but doesn't verify the user's role.
> Any authenticated user can enumerate your entire user table.
>
> Finding 5 — High — Stripe webhook signature verification disabled.
> In `src/app.py` the signature check is commented out with a TODO.
> Anyone who knows your webhook URL can trigger subscription activations.
>
> Finding 6 — Medium — Internal services called over HTTP, not HTTPS.
> Three internal service calls use plain HTTP. Man-in-the-middle on your
> internal network is now a viable attack vector."

**[Look at camera or pause significantly]**

> "Six findings. Two critical. Three high. One medium.
>
> A real, useful security audit. Findings your team can action.
> Findings that would have cost several thousand dollars from a pen-test firm.
>
> And the AI mentioned credentials exactly zero times.
> Because it never saw any."

---

### SCENE 6 — Ask for Fixes — 4:30 to 5:00

> "And now the fun part. We can ask AI to fix the issues it found."

```bash
localmask mask-prompt "Based on the security audit, provide a patched version of the login endpoint in src/app.py that: 1) uses parameterized SQL queries, 2) removes password logging, 3) adds rate limiting using a Redis-based counter. Preserve all existing functionality and placeholder values exactly."
```

**[AI returns patched code with placeholders intact]**

> "The fix comes back with `~[REDIS_URL_0]~` and `~[JWT_SECRET_0]~` intact.
> The AI didn't try to fill them in. It worked with the masked values,
> which is exactly what we want."

**[Run rehydrate]**

```bash
localmask rehydrate-answer "<AI response>"
```

> "Rehydrate. Real values restored. Patch ready for review and PR."

---

### CLOSING — 5:00 to 5:30

**[VS Code visible in background, terminal in foreground]**

> "Security audits and secrets management are usually two separate problems.
> LocalMask makes them one workflow.
>
> You scan once. You mask the context. You send it to any AI you want —
> Claude, GPT-4, Gemini, a local model, whatever. The AI finds the bugs.
> You rehydrate the fixes. Your credentials never moved.
>
> The 29 million secrets that leaked on GitHub in 2025 — most of them weren't
> caused by ~[SERVER_HOSTNAME_1]~ not caring. They were caused by friction. The tools made
> it easier to leak than to protect.
>
> LocalMask removes the friction.
>
> Link in the description. Run `pip install localmask` and do your own audit
> today — I'd be curious what you find."

**[Fade out]**

---

---

---

## SCENARIO 6 — The Cloud AI Agent (6 minutes)
### "I connected my private codebase to an AI agent in Azure — and kept every secret local"

**Platform**: Azure AI Foundry (visual, enterprise, supports Claude)
**Why this works**: Shows the full end-to-end production workflow — not just masking, but an actual AI agent doing real work on real code. This is the "wow" demo for technical leads, CTOs, and enterprise teams.

---

### HOOK (0:00–0:20)

**[Terminal open, split screen with VS Code showing src/app.py]**

> "This is a real production codebase. Stripe keys, database passwords,
> JWT secrets, AWS credentials — all hardcoded, all real-looking."

> "I'm going to connect it to an Azure AI agent.
> The agent is going to do a full security audit —
> find every vulnerability, explain how to exploit it,
> and tell me how to fix it."

> "And at no point will Azure see a single real secret."

> "Let me show you exactly how."

---

### SCENE 1 — Scan the codebase (0:20–1:00)

**[Terminal]**

```bash
localmask scan . --sensitivity strict
```

**[Watch detections stream in — Stripe, DB, JWT, AWS, Redis...]**

> "LocalMask finds 47 secrets across 4 files.
> Every one of them will be replaced before this code touches any cloud."

**[Show the detection summary table]**

> "Stripe live keys — masked.
> Database admin password — masked.
> JWT signing secret — masked.
> AWS credentials — masked."

> "These never leave this terminal."

---

### SCENE 2 — Review and publish (1:00–1:45)

**[Run review, scan through detections quickly]**

```bash
localmask get-detections <scan_id>
```

> "Quick review — approve everything.
> One false positive here — our internal service URL isn't a secret.
> Reject that one."

**[Publish masked repo]**

```bash
localmask publish <scan_id> \
  --target-url https://github.com/~[GIT_REMOTE_URL_0]~ \
  --private
```

> "Published. GitHub now has a clean copy of our code.
> Same logic, same structure — every credential is a placeholder."

**[Switch to browser — open GitHub masked repo]**

**[Click on src/app.py — scroll to stripe.api_key line]**

> "Here's what Azure will see for the Stripe key."

```python
stripe.api_key = "~[STRIPE_SECRET_KEY_0]~"
```

> "And the database connection."

```python
DB_WRITE_URL = "~[DATABASE_URL_1]~"
```

> "The AI can understand what these are — a Stripe key, a database URL.
> It just can't read the actual values. That's the whole trick."

---

### SCENE 3 — Azure AI Foundry setup (1:45–2:45)

**[Switch to Azure portal — ai.azure.com]**

> "Azure AI Foundry — this is where enterprise teams build AI agents.
> We already provisioned our agent using the setup script.
> Let me show you what it looks like."

**[Navigate to Project → ~[NER_PERSON_27]~]**

> "The masked GitHub repo is connected here.
> The agent has read access. That's it — no write, no admin."

**[Navigate to Agents panel — show the pre-created agent]**

> "Our security audit agent. System prompt tells it to treat
> ~[TOKEN]~ placeholders as opaque — don't guess, don't invent,
> just analyze the logic around them."

**[Show the agent's system prompt — zoom in on the key line]**

> *"Keep all ~[TOKEN]~ placeholders verbatim in any code you write.
> Real values are restored locally after you respond."*

---

### SCENE 4 — Run the agent (2:45–4:30) ← THE MONEY SHOT

**[Switch to VS Code terminal]**

```bash
python src/cloud_agent_demo.py \
  --task security-audit \
  --platform azure
```

> "This script fetches the masked code, ships it to the Azure agent,
> and streams the response back."

**[Watch the output — agent analyzing, findings appearing]**

> "The agent is reading the codebase now. Real code. Masked secrets."

**[First finding appears — SQL injection in login endpoint]**

> "There it is. SQL injection in the login endpoint.
> Line 150. String formatting directly in the query — classic."

**[More findings stream in]**

> "Passwords being logged in plain text — line 144.
> ~[NER_PERSON_47]~-generated checkout file has a hardcoded API key.
> Internal service running over HTTP, not HTTPS.
> CORS wildcard — allows requests from any origin."

**[Final summary appears — 6 Critical, 4 High, 3 Medium]**

> "6 critical issues. 4 high. Found in about 30 seconds.
> A human security consultant would charge ~[NER_MONEY_0]~ for this review
> and take two weeks."

**[Pause — let that land]**

> "~[NER_PERSON_48]~ never saw a single real password."

---

### SCENE 5 — Rehydration (4:30–5:15)

**[Show the saved report file]**

```bash
cat agent-output/security-audit-azure-*.md | head -40
```

> "The agent's report has ~[TOKEN]~ placeholders wherever it
> referenced credentials. For a security audit that's fine —
> we want to know about the code patterns, not the actual values."

> "But if we'd run the refactor-dotenv task instead —
> the agent would have written a whole new .env file,
> with placeholders where the real secrets go."

```bash
python src/cloud_agent_demo.py \
  --task refactor-dotenv \
  --platform azure
```

> "And to apply that output with real values restored:"

```bash
localmask rehydrate <scan_id> agent-output/refactor-dotenv-azure-*.md
```

> "Real credentials injected locally. The AI did the refactor.
> Your secrets never left the machine."

---

### SCENE 6 — Sync and close (5:15–6:00)

**[Terminal]**

```bash
bash ~/.localmask/cloud-connections/sync-*.sh
```

> "Every time you push new code, one command re-scans and
> re-publishes the masked copy. The agent is always looking
> at the latest version of your codebase."

> "For your CI pipeline:"

```yaml
# .github/workflows/localmask-sync.yml
- run: localmask sync "${{ secrets.LOCALMASK_SCAN_ID }}"
```

> "That's it. Commit, push, sync. The agent stays current.
> Your secrets stay local."

**[VS Code — show the full project structure]**

> "Three cloud platforms. One masked repo.
> Azure AI Foundry. AWS Bedrock. GCP Vertex AI.
> Any agent, any model, any task."

> "Your code is readable. Your secrets are not."

> "LocalMask."

**[Fade out]**

---

### RECORDING NOTES — Scenario 6

- **Best take**: Scene 4 — run the agent and let findings stream in real time. Don't cut. Let the findings land one by one.
- **Pre-run**: Do a dry run before recording — confirm the Azure agent responds and the output is clean
- **Fallback**: ~[NER_PERSON_50]~ has latency issues on the day, the `--platform claude` flag runs the same task locally via the Anthropic API. Identical output, no Azure dependency.
- **Screen layout**: VS Code left, terminal right, browser in the background for Azure portal shots

### Title options — Scenario 6

1. *"I gave an Azure AI agent access to my production codebase — safely"*
2. *"Azure AI Foundry + your private repo — the right way"*
3. *"AI security audit in 30 seconds (your secrets stay local)"*
4. *"How to connect any cloud AI agent to private code — without leaking credentials"*
5. *"I ran a full security audit with AI. Here's what it found — and what it never saw."*

### Thumbnail concept

Azure AI Foundry dashboard on the left, VS Code with masked code on the right.
Big text: **"47 secrets. AI saw 0."**

### Best communities for this video

- r/azure (Azure-specific — very engaged)
- r/~[SERVER_HOSTNAME_3]~
- r/netsec
- r/MachineLearning
- LinkedIn (enterprise CTO/tech lead audience)
- ~[NER_PERSON_42]~ (title: "Show HN: Running AI agents on private codebases without leaking secrets")

---

## CROSS-VIDEO NOTES

### Posting Strategy
- ~[NER_PERSON_34]~ 4 first — "AI hardcoded my key" is the most clickable and taps into current discourse around AI coding assistants
- ~[NER_PERSON_34]~ 1 second — broader audience, good SEO
- ~[NER_PERSON_34]~ 5 third — security community is loyal once you earn it

### Linking
- Each video should reference the other two as "part of a series"
- Pin a comment on each with the timestamp breakdown for fast navigation
- Add timestamps to YouTube description for all major sections

### The 29 Million Statistic
This is a real number — GitGuardian's State of ~[NER_PERSON_37]~ 2025 report.
Cite it verbatim: "GitGuardian detected 29 million new leaked secrets on GitHub in 2025 —
up from 12.8 million in 2023. AI-assisted repositories leak secrets at 2× the rate of
non-AI repositories."

### Tone Calibration
These scripts are written ~[SERVER_HOSTNAME_0]~. Do not:
- Say "leverage" or "utilize"
- Use corporate passive voice ("it has been determined that...")
- Over-explain what a JWT is
Do:
- Use "you" directly
- Name specific tools (Cursor, GitHub, Stripe) — specificity builds credibility
- Let silence do work — pause after the big reveal moments
- Be slightly self-deprecating about the vulnerabilities ("I put that one in there myself")
