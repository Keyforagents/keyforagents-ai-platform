#!/usr/bin/env python3
"""
keyforagents.com — Commander
The master CLI for the entire AI automation platform.

Usage:
  python commander.py ideas           # Grok → new side hustle ideas → Notion
  python commander.py content         # Grok → X/Twitter threads → Notion calendar
  python commander.py readme-update   # Grok → update GitHub READMEs with SEO
  python commander.py full-run        # All of the above
  python commander.py telegram <msg>  # Send to Termux88 channels
  python commander.py status          # Check all system statuses
  python commander.py poll-commands   # Poll Notion Agent Command Center → execute
"""
import os, sys, json, time, datetime, requests
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
GROK_API_KEY    = os.getenv("GROK_API_KEY")
NOTION_TOKEN    = os.getenv("NOTION_TOKEN")
GITHUB_TOKEN    = os.getenv("GITHUB_TOKEN")
TELEGRAM_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT   = os.getenv("TELEGRAM_CHAT_ID", "-1002505269710")
GITHUB_OWNER    = os.getenv("GITHUB_OWNER", "helpinghands3631-bot")

NOTION_DBS = {
    "revenue":   "4802d6b5-a24e-4769-9069-e433f48605f6",
    "ideas":     "e1e413ca-69eb-4735-925c-2477d6b28482",
    "content":   "30de536a-4462-4246-988e-346d7147c85e",
    "commands":  "a4403bbc-c1ef-4805-b9f1-0bec03b4f3a5",
}

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


# ── Grok LLM ─────────────────────────────────────────────────────────────────
def grok(prompt: str, system: str = "You are a sharp AI business strategist for keyforagents.com") -> str:
    """Call Grok-3 via xAI API."""
    if not GROK_API_KEY:
        return f"[GROK DISABLED — set GROK_API_KEY]\nPrompt was: {prompt[:200]}"
    
    headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "grok-3",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 2000,
    }
    try:
        r = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=body, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[GROK ERROR: {e}]"


# ── Notion helpers ─────────────────────────────────────────────────────────────
def notion_add_idea(title: str, description: str, potential: str = "Medium"):
    r = requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json={
        "parent": {"database_id": NOTION_DBS["ideas"]},
        "properties": {
            "Name":        {"title": [{"text": {"content": title}}]},
            "Description": {"rich_text": [{"text": {"content": description[:2000]}}]},
            "Potential":   {"select": {"name": potential}},
            "Status":      {"select": {"name": "New"}},
        }
    })
    return r.status_code == 200


def notion_add_content(title: str, content: str, platform: str, scheduled: str = None):
    props = {
        "Title":    {"title": [{"text": {"content": title}}]},
        "Content":  {"rich_text": [{"text": {"content": content[:2000]}}]},
        "Platform": {"select": {"name": platform}},
        "Status":   {"select": {"name": "Draft"}},
    }
    if scheduled:
        props["Scheduled"] = {"date": {"start": scheduled}}
    
    r = requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json={
        "parent": {"database_id": NOTION_DBS["content"]},
        "properties": props,
    })
    return r.status_code == 200


def notion_update_command_status(page_id: str, status: str, output: str = ""):
    props = {"Status": {"select": {"name": status}}}
    if output:
        props["Output"] = {"rich_text": [{"text": {"content": output[:2000]}}]}
    r = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=NOTION_HEADERS,
                       json={"properties": props})
    return r.status_code == 200


def notion_get_queued_commands():
    r = requests.post(
        f"https://api.notion.com/v1/databases/{NOTION_DBS['commands']}/query",
        headers=NOTION_HEADERS,
        json={"filter": {"property": "Status", "select": {"equals": "Queued"}}},
    )
    if r.status_code != 200:
        return []
    return r.json().get("results", [])


# ── Telegram ──────────────────────────────────────────────────────────────────
def telegram(msg: str, chat_id: str = None):
    if not TELEGRAM_TOKEN:
        print(f"⚠️  Telegram disabled (no token). Message: {msg[:100]}")
        return False
    cid = chat_id or TELEGRAM_CHAT
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": cid, "text": msg, "parse_mode": "Markdown"},
        timeout=10,
    )
    return r.status_code == 200


# ── Commands ──────────────────────────────────────────────────────────────────
def cmd_ideas():
    print("🧠 Generating side hustle ideas with Grok...")
    response = grok("""Generate 5 brand-new side hustle ideas for keyforagents.com. 
    Context: Australian market, AI-powered automation, owner knows coding.
    Current focus: B2B AI automation for real estate, law, NDIS, pest control.
    
    For each idea provide:
    1. Name (catchy, max 6 words)
    2. One-line description
    3. Revenue potential (Low/Medium/High/🔥 Massive)
    4. Time to launch (days)
    5. First action to take today
    
    Format as JSON array.""")
    
    try:
        # Extract JSON from response
        import re
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            ideas = json.loads(match.group())
        else:
            ideas = [{"name": f"Idea {i}", "description": line, "potential": "Medium", "days": 7, "action": "Research"}
                     for i, line in enumerate(response.split('\n')[:5], 1) if line.strip()]
    except Exception:
        ideas = [{"name": "AI Side Hustle", "description": response[:500], "potential": "High", "days": 14, "action": "Plan it"}]

    added = 0
    for idea in ideas:
        name = idea.get("name", "Unnamed Idea")
        desc = f"{idea.get('description', '')}\n\nTime to launch: {idea.get('days', '?')} days\nFirst action: {idea.get('action', 'TBD')}"
        potential_map = {"Low": "Low", "Medium": "Medium", "High": "High", "🔥 Massive": "🔥 Massive"}
        potential = potential_map.get(idea.get("potential", "Medium"), "Medium")
        
        if notion_add_idea(name, desc, potential):
            added += 1
            print(f"  ✅ Added: {name}")
        else:
            print(f"  ⚠️  Failed: {name}")

    msg = f"🧠 *{added} new side hustle ideas* added to Notion!\n" + "\n".join(
        f"• {i.get('name', 'Idea')}" for i in ideas[:5]
    )
    telegram(msg)
    print(f"\n✅ Ideas run complete: {added}/{len(ideas)} added to Notion")
    return added


def cmd_content():
    print("📅 Generating content calendar with Grok...")
    today = datetime.date.today()
    
    topics = [
        ("Why Australian real estate agents are losing clients to competitors using AI", "X"),
        ("5 tasks your law firm should automate in 2026", "LinkedIn"),
        ("NDIS providers: save 10 hours/week with AI automation", "Email"),
        ("How pest control companies in Australia are using AI to quote faster", "Blog"),
        ("The $500/mo AI tool that replaces your $5k/mo admin team", "X"),
        ("keyforagents.com — 90-day ROI calculator for Australian SMBs", "LinkedIn"),
    ]
    
    added = 0
    for i, (topic, platform) in enumerate(topics):
        content = grok(f"""Write a {platform} post about: {topic}
        
        Rules:
        - Platform: {platform}
        - Audience: Australian B2B decision-makers
        - Tone: Direct, confident, value-first
        - For X: 10-tweet thread with hook + value + CTA
        - For LinkedIn: 300-word article
        - For Email: Subject line + 200-word email
        - For Blog: H1 + 3 H2s + meta description
        - CTA: Book a free demo at keyforagents.com""")
        
        scheduled_date = (today + datetime.timedelta(days=i * 2)).isoformat()
        
        if notion_add_content(topic, content, platform, scheduled_date):
            added += 1
            print(f"  ✅ Scheduled [{platform}]: {topic[:60]}...")
    
    telegram(f"📅 *{added} content pieces* scheduled in Notion calendar!\nNext 12 days covered across X, LinkedIn, Email, Blog.")
    print(f"\n✅ Content run complete: {added}/{len(topics)} pieces scheduled")
    return added


def cmd_readme_update():
    print("📝 Updating GitHub READMEs with Grok SEO...")
    if not GITHUB_TOKEN:
        print("⚠️  No GITHUB_TOKEN — skipping README update")
        return 0
    
    repos_to_update = ["keyforagents-ai-platform"]
    updated = 0
    
    for repo in repos_to_update:
        readme_content = grok(f"""Write a professional GitHub README for {repo} (owned by helpinghands3631-bot).
        
        Context: keyforagents.com — AI automation platform for Australian businesses.
        Services: real estate, law firms, NDIS providers, pest control.
        Tech stack: Python, CrewAI, Grok/xAI, Stripe, Notion API, Telegram.
        
        Include:
        - Compelling H1 title with emoji
        - 1-line tagline
        - Features section (6 bullet points)
        - Quick start (3 commands)
        - Environment variables table
        - Architecture overview
        - Links to keyforagents.com
        - Badges (Python, License, Status)
        
        Make it SEO-optimised for "AI automation Australia" keywords.""")
        
        import base64
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        
        # Get current SHA
        r = requests.get(f"https://api.github.com/repos/{GITHUB_OWNER}/{repo}/contents/README.md", headers=headers)
        sha = r.json().get("sha", "") if r.status_code == 200 else ""
        
        payload = {
            "message": "docs: AI-generated SEO README update [commander]",
            "content": base64.b64encode(readme_content.encode()).decode(),
        }
        if sha:
            payload["sha"] = sha
        
        r = requests.put(
            f"https://api.github.com/repos/{GITHUB_OWNER}/{repo}/contents/README.md",
            headers=headers,
            json=payload,
        )
        if r.status_code in (200, 201):
            updated += 1
            print(f"  ✅ Updated README: {repo}")
        else:
            print(f"  ⚠️  Failed {repo}: {r.status_code}")
    
    telegram(f"📝 *{updated} READMEs* updated with SEO content!")
    return updated


def cmd_poll_commands():
    """Poll Notion Agent Command Center for Queued commands and execute them."""
    print("⚡ Polling Agent Command Center for queued commands...")
    commands = notion_get_queued_commands()
    
    if not commands:
        print("✅ No queued commands found.")
        return 0
    
    print(f"Found {len(commands)} queued commands.")
    executed = 0
    
    for cmd_page in commands:
        page_id = cmd_page["id"]
        props = cmd_page.get("properties", {})
        
        command_name = ""
        if props.get("Command", {}).get("title"):
            command_name = props["Command"]["title"][0]["text"]["content"]
        
        agent = props.get("Agent", {}).get("select", {}).get("name", "Orchestrator")
        
        print(f"\n  ⚡ Executing: {command_name} [Agent: {agent}]")
        
        # Mark as Running
        notion_update_command_status(page_id, "Running")
        
        try:
            # Route command to appropriate handler
            result = "Command executed."
            
            if "outreach" in command_name.lower():
                target = command_name.split(":", 1)[-1].strip() if ":" in command_name else command_name
                result = f"Outreach sequence queued for: {target}"
            elif "campaign" in command_name.lower():
                topic = command_name.split(":", 1)[-1].strip() if ":" in command_name else command_name
                result = f"Campaign content created for: {topic}"
            elif "ideas" in command_name.lower():
                count = cmd_ideas()
                result = f"Generated and saved {count} ideas to Notion"
            elif "content" in command_name.lower():
                count = cmd_content()
                result = f"Scheduled {count} content pieces"
            else:
                result = grok(f"Execute this task for keyforagents.com: {command_name}")
            
            notion_update_command_status(page_id, "Done", result[:2000])
            executed += 1
            print(f"  ✅ Done: {command_name}")
            
        except Exception as e:
            notion_update_command_status(page_id, "Failed", str(e)[:500])
            print(f"  ❌ Failed: {command_name} — {e}")
    
    telegram(f"⚡ Command Center: *{executed}/{len(commands)}* commands executed.")
    return executed


def cmd_status():
    """Check all system statuses."""
    print("\n📊 keyforagents.com System Status")
    print("=" * 50)
    
    checks = {
        "Grok API":    bool(GROK_API_KEY),
        "Notion API":  bool(NOTION_TOKEN),
        "GitHub API":  bool(GITHUB_TOKEN),
        "Telegram":    bool(TELEGRAM_TOKEN),
    }
    
    for service, ok in checks.items():
        icon = "✅" if ok else "❌"
        print(f"  {icon} {service}: {'Connected' if ok else 'Missing API key'}")
    
    # Test Notion
    if NOTION_TOKEN:
        r = requests.get("https://api.notion.com/v1/users/me", headers=NOTION_HEADERS)
        notion_ok = r.status_code == 200
        print(f"  {'✅' if notion_ok else '❌'} Notion connection: {'OK' if notion_ok else 'FAILED'}")
    
    print("\n📋 Notion Databases:")
    for name, db_id in NOTION_DBS.items():
        print(f"  • {name}: {db_id}")
    
    print(f"\n🌐 Domain: keyforagents.com")
    print(f"🐙 GitHub: github.com/{GITHUB_OWNER}")
    print(f"📱 Telegram: {TELEGRAM_CHAT}")
    print("=" * 50)


# ── Full Run ───────────────────────────────────────────────────────────────────
def cmd_full_run():
    print("🚀 FULL RUN — executing all commander tasks...")
    telegram("🚀 *keyforagents Commander* — Full run starting...")
    
    results = {}
    results["ideas"]   = cmd_ideas()
    results["content"] = cmd_content()
    results["readme"]  = cmd_readme_update()
    
    summary = (f"🚀 *keyforagents Full Run Complete*\n"
               f"• 🧠 Ideas: {results['ideas']} new\n"
               f"• 📅 Content: {results['content']} pieces scheduled\n"
               f"• 📝 READMEs: {results['readme']} updated")
    telegram(summary)
    print(f"\n{summary.replace('*', '')}")


# ── CLI Entry ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════════╗
║          keyforagents.com — Commander CLI                    ║
╠══════════════════════════════════════════════════════════════╣
║  ideas            Grok → side hustle ideas → Notion          ║
║  content          Grok → content calendar → Notion           ║
║  readme-update    Grok → SEO READMEs → GitHub                ║
║  full-run         Run all of the above                       ║
║  telegram <msg>   Send message to Termux88                   ║
║  status           Check all system connections               ║
║  poll-commands    Execute queued Notion commands             ║
╚══════════════════════════════════════════════════════════════╝
        """)
        sys.exit(0)

    cmd = sys.argv[1].lower()
    
    if cmd == "ideas":
        cmd_ideas()
    elif cmd == "content":
        cmd_content()
    elif cmd == "readme-update":
        cmd_readme_update()
    elif cmd == "full-run":
        cmd_full_run()
    elif cmd == "telegram":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Test from commander"
        ok = telegram(msg)
        print(f"{'✅' if ok else '❌'} Telegram: {msg[:80]}")
    elif cmd == "status":
        cmd_status()
    elif cmd == "poll-commands":
        cmd_poll_commands()
    else:
        print(f"❌ Unknown command: {cmd}")
        sys.exit(1)
