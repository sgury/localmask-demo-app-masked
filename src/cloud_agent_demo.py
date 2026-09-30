"""
Cloud AI Agent Demo — LocalMask + Azure AI Foundry
===================================================
This script shows the full pipeline:

  1. Scan the ShipFast codebase with LocalMask (secrets masked locally)
  2. Publish a masked copy to GitHub (no real secrets in it)
  3. Connect an Azure AI Foundry agent to the masked repo
  4. Run a security audit task — agent analyzes real code, sees zero real secrets
  5. Rehydrate the agent's output back to a usable report

Run:
    pip install localmask azure-ai-projects anthropic python-dotenv
    python src/cloud_agent_demo.py --task security-audit
    python src/cloud_agent_demo.py --task refactor-dotenv
    python src/cloud_agent_demo.py --task fix-~[SERVER_HOSTNAME_SQL_4]~

Requires .env.demo (see .env.demo.example) — those credentials ARE safe to share
because they only control access to the MASKED repo and AI platform,
not your production systems.
"""

import os
import sys
import json
import time
import argparse
import textwrap
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env.demo")

# ── Azure AI Foundry client ──────────────────────────────────────────────────
try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

# ── Anthropic client (fallback / local dev) ──────────────────────────────────
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# ─── Config ──────────────────────────────────────────────────────────────────

MASKED_REPO_URL   = os.getenv("MASKED_REPO_URL",   "https://github.com/~[GIT_REMOTE_URL_0]~")
LOCALMASK_SCAN_ID = os.getenv("LOCALMASK_SCAN_ID",  "")

# Azure AI Foundry
AZURE_ENDPOINT    = os.getenv("AZURE_AI_ENDPOINT",  "")
AZURE_PROJECT     = os.getenv("AZURE_AI_PROJECT",   "")
AZURE_MODEL       = os.getenv("AZURE_MODEL",         "claude-sonnet-4-6")  # deployed in Foundry

# Anthropic (fallback)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY",  "")


# ─── Task definitions ─────────────────────────────────────────────────────────

TASKS = {
    "security-audit": {
        "name": "Full Security Audit",
        "description": "Find every security vulnerability in the codebase",
        "system": textwrap.dedent("""
            You are a senior application security engineer performing a production
            security audit. Analyze the codebase thoroughly and produce a structured
            report covering:

            1. Critical vulnerabilities (CVSS 9.0+) — must fix before next deploy
            2. High severity issues (CVSS 7.0–8.9)
            3. Medium severity issues
            4. Code patterns that increase attack surface

            For each finding:
            - Issue title
            - File and line number
            - Severity (Critical/High/Medium/Low)
            - Description of the vulnerability
            - Proof of concept (how it could be exploited)
            - Recommended fix with code example

            IMPORTANT: The code you receive has secrets replaced with ~[TOKEN]~ placeholders.
            Treat these as opaque values. Do NOT guess real values. Keep placeholders verbatim
            in any code you write. Focus your analysis on code logic, not the placeholder values.
        """).strip(),
        "prompt": textwrap.dedent("""
            Perform a full security audit of this ShipFast shipping SaaS backend.

            Files to analyze:
            - src/app.py — main FastAPI application
            - src/database.py — database connection and query execution
            - config/settings.py — production configuration
            - src/ai_generated_checkout.py — Cursor-generated checkout module

            Focus especially on:
            - Authentication and authorization flaws
            - SQL injection vulnerabilities
            - Credential and secret handling
            - Input validation gaps
            - Data exposure risks
            - Insecure dependencies or service connections

            Return a full audit report in markdown format.
        """).strip(),
    },

    "refactor-dotenv": {
        "name": "Refactor: Hardcoded Secrets → .env",
        "description": "Extract all hardcoded secrets to a .env file and load them properly",
        "system": textwrap.dedent("""
            You are a senior Python ~[SERVER_HOSTNAME_5]~ performing a security refactor.
            Your job is to extract all hardcoded credentials and secrets from
            the codebase and replace them with environment variable lookups
            using python-dotenv.

            Rules:
            - Every ~[TOKEN]~ placeholder represents a secret — keep the placeholder
              verbatim in the .env file you generate (the real value is substituted locally)
            - Use os.getenv() with sensible defaults or fail-fast on missing vars
            - Generate both the refactored Python files AND a complete .env.example
            - Add validation at startup: if a required env var is missing, raise a
              clear error before the server starts
            - Do not break any existing functionality — only change how secrets are loaded

            Output format:
            1. .env.example file (with ~[TOKEN]~ placeholders)
            2. Updated src/app.py
            3. Updated config/settings.py
            4. A brief migration guide
        """).strip(),
        "prompt": textwrap.dedent("""
            Refactor the ShipFast codebase to move all hardcoded secrets to a .env file.

            Files to refactor:
            - src/app.py
            - config/settings.py
            - src/database.py
            - src/ai_generated_checkout.py

            Generate the complete refactored files and a .env.example.
            Use python-dotenv for loading. Add startup validation.
        """).strip(),
    },

    "fix-sql-injection": {
        "name": "Fix SQL Injection Vulnerabilities",
        "description": "Find and fix all SQL injection points with parameterized queries",
        "system": textwrap.dedent("""
            You are a database security specialist. Your task is to find every SQL
            injection vulnerability in the codebase and fix them using parameterized
            queries. Never use string formatting or concatenation to build SQL.

            For each fix:
            - Show the vulnerable code (before)
            - Show the fixed code (after)
            - Explain why the original was vulnerable

            Use psycopg2's parameterized query syntax: cursor.execute(query, (param,))
            Never use f-strings, .format(), or % formatting in SQL queries.
        """).strip(),
        "prompt": textwrap.dedent("""
            Find and fix all SQL injection vulnerabilities in:
            - src/app.py
            - src/database.py

            Return the complete fixed versions of both files.
        """).strip(),
    },
}


# ─── Code fetcher ─────────────────────────────────────────────────────────────

def fetch_masked_code() -> dict:
    """
    In production this fetches from the masked GitHub repo.
    For the demo, reads local files (same content the masked repo would have
    after localmask publish).
    """
    files = {}
    demo_root = Path(__file__).parent.parent

    targets = [
        "src/app.py",
        "src/database.py",
        "config/settings.py",
        "src/ai_generated_checkout.py",
    ]

    for rel_path in targets:
        full_path = demo_root / rel_path
        if full_path.exists():
            files[rel_path] = full_path.read_text()
            print(f"  [+] Loaded {rel_path} ({len(files[rel_path])} chars)")
        else:
            print(f"  [-] Skipped {rel_path} (not found)")

    return files


def build_user_message(task: dict, code_files: dict) -> str:
    """Combine the task prompt with the masked source files."""
    sections = [task["prompt"], "\n\n---\n\n## Source Files\n"]
    for path, content in code_files.items():
        sections.append(f"### `{path}`\n\n```python\n{content}\n```\n")
    return "\n".join(sections)


# ─── Azure AI Foundry agent ───────────────────────────────────────────────────

def run_azure_agent(task_key: str) -> str:
    """Run the task using an Azure AI Foundry agent connected to the masked repo."""
    if not AZURE_AVAILABLE:
        raise RuntimeError("azure-ai-projects not installed. Run: pip install azure-ai-projects")
    if not AZURE_ENDPOINT:
        raise RuntimeError("AZURE_AI_ENDPOINT not set in .env.demo")

    task = TASKS[task_key]
    print(f"\n[Azure AI Foundry] Running: {task['name']}")
    print(f"  Endpoint : {AZURE_ENDPOINT}")
    print(f"  Project  : {AZURE_PROJECT}")
    print(f"  Model    : {AZURE_MODEL}")
    print(f"  Repo     : {MASKED_REPO_URL}")

    credential = DefaultAzureCredential()
    client = AIProjectClient(
        endpoint=AZURE_ENDPOINT,
        credential=credential,
    )

    print("\n[1/4] Fetching masked code...")
    code_files = fetch_masked_code()

    print("[2/4] Creating agent in Azure AI Foundry...")
    agent = client.agents.create_agent(
        model=AZURE_MODEL,
        name=f"localmask-{task_key}-agent",
        instructions=task["system"],
    )

    print("[3/4] Creating thread and sending task...")
    thread = client.agents.create_thread()
    client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=build_user_message(task, code_files),
    )

    run = client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=agent.id,
    )

    print(f"  Run status: {run.status}")
    if run.status == "failed":
        raise RuntimeError(f"Agent run failed: {run.last_error}")

    print("[4/4] Collecting response...")
    messages = client.agents.list_messages(thread_id=thread.id)
    response = next(
        (m.content[0].text.value for m in messages.data if m.role == "assistant"),
        "No response received."
    )

    # Cleanup
    client.agents.delete_agent(agent.id)
    return response


# ─── Anthropic fallback (local dev / demo without Azure) ─────────────────────

def run_anthropic_agent(task_key: str) -> str:
    """
    Fallback: run the same task using the Anthropic API directly.
    Perfect for demoing locally without an Azure subscription.
    The masked code is passed directly — no real secrets are in it.
    """
    if not ANTHROPIC_AVAILABLE:
        raise RuntimeError("anthropic not installed. Run: pip install anthropic")
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not set in .env.demo")

    task = TASKS[task_key]
    print(f"\n[Anthropic Claude] Running: {task['name']}")
    print(f"  Model    : claude-sonnet-4-6")
    print(f"  Repo     : {MASKED_REPO_URL} (masked)")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    print("\n[1/3] Fetching masked code...")
    code_files = fetch_masked_code()

    print("[2/3] Sending to Claude...")

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=task["system"],
        messages=[
            {"role": "user", "content": build_user_message(task, code_files)}
        ],
    ) as stream:
        print("[3/3] Streaming response...\n")
        print("─" * 60)
        full_response = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text
        print("\n" + "─" * 60)

    return full_response


# ─── Output ───────────────────────────────────────────────────────────────────

def save_report(task_key: str, content: str, platform: str):
    """Save the agent's report to a file."""
    out_dir = Path("agent-output")
    out_dir.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    out_file = out_dir / f"{task_key}-{platform}-{timestamp}.md"
    out_file.write_text(content)
    print(f"\n[SAVED] Report written to: {out_file}")
    return out_file


def rehydrate_report(report_path: Path):
    """
    Locally restore real values in the agent's output.
    Real secrets are substituted back only on this machine.
    """
    if not LOCALMASK_SCAN_ID:
        print("\n[SKIP] LOCALMASK_SCAN_ID not set — skipping rehydration")
        print("  The report contains ~[TOKEN]~ placeholders.")
        print("  To restore real values: localmask rehydrate <scan_id> <report_file>")
        return

    import subprocess
    print(f"\n[Rehydrate] Restoring real values locally...")
    result = subprocess.run(
        ["localmask", "rehydrate", LOCALMASK_SCAN_ID, str(report_path)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"  [OK] Rehydrated: {report_path}")
    else:
        print(f"  [WARN] Rehydration: {result.stderr}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    """CLI entry point for the LocalMask cloud agent demo.

    Parses ``--task``, ``--platform`` and ``--no-rehydrate``, sends the masked
    codebase to the selected AI platform (Azure AI Foundry or the Anthropic API),
    saves the agent's report, and rehydrates masked placeholders locally
    unless ``--no-rehydrate`` is given. Exits with status 1 on any error.
    """
    parser = argparse.ArgumentParser(
        description="LocalMask + Cloud AI Agent Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Tasks:
          security-audit      Full security vulnerability report
          refactor-dotenv     Extract all hardcoded secrets to .env
          fix-~[SERVER_HOSTNAME_SQL_4]~   Find and fix SQL injection with parameterized queries

        Platform:
          --platform azure    Use Azure AI Foundry (requires .env.demo Azure vars)
          --platform claude   Use Anthropic Claude API directly (default)

        Examples:
          python src/cloud_agent_demo.py --task security-audit
          python src/cloud_agent_demo.py --task refactor-dotenv --platform azure
          python src/cloud_agent_demo.py --task fix-~[SERVER_HOSTNAME_SQL_4]~ --platform claude
        """)
    )
    parser.add_argument(
        "--task",
        choices=list(TASKS.keys()),
        default="security-audit",
        help="Task for the agent to perform",
    )
    parser.add_argument(
        "--platform",
        choices=["azure", "claude"],
        default="claude",
        help="AI platform to use (default: claude)",
    )
    parser.add_argument(
        "--no-rehydrate",
        action="store_true",
        help="Skip rehydration step (keep ~[TOKEN]~ placeholders in output)",
    )
    args = parser.parse_args()

    task = TASKS[args.task]

    print("\n" + "═" * 60)
    print(f"  LocalMask Cloud Agent Demo")
    print(f"  Task     : {task['name']}")
    print(f"  Platform : {args.platform.upper()}")
    print(f"  Codebase : ShipFast SaaS (masked — no real secrets)")
    print("═" * 60)

    print("\n⚠️  The code passed to the AI has ALL secrets replaced with")
    print("   ~[TOKEN]~ placeholders. Real credentials never leave this machine.\n")

    try:
        if args.platform == "azure":
            response = run_azure_agent(args.task)
        else:
            response = run_anthropic_agent(args.task)

        report_path = save_report(args.task, response, args.platform)

        if not args.no_rehydrate:
            rehydrate_report(report_path)

        print("\n" + "═" * 60)
        print("  Done. Your secrets stayed local. The AI did the work.")
        print("═" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
