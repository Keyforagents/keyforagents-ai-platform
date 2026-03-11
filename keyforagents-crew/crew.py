#!/usr/bin/env python3
"""
keyforagents.com — CrewAI Crew
Integrates: agency-agents NEXUS framework + Stripe MCP + Notion MCP
Usage:
  python crew.py outreach "real estate agents in Melbourne"
  python crew.py sell "Growth Package" 1500 "3 AI workflows"
  python crew.py campaign "AI automation for NDIS providers"
  python crew.py build-mvp "keyforagents.com homepage"
"""
import os, sys, json
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY    = os.getenv("GROK_API_KEY")
NOTION_TOKEN    = os.getenv("NOTION_TOKEN")
STRIPE_API_KEY  = os.getenv("STRIPE_API_KEY")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")   # fallback if no Grok
TELEGRAM_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT   = os.getenv("TELEGRAM_CHAT_ID", "-1002505269710")

# ── Notion DB IDs ────────────────────────────────────────────────────────────
NOTION_DBS = {
    "revenue":   "4802d6b5-a24e-4769-9069-e433f48605f6",
    "ideas":     "e1e413ca-69eb-4735-925c-2477d6b28482",
    "content":   "30de536a-4462-4246-988e-346d7147c85e",
    "commands":  "a4403bbc-c1ef-4805-b9f1-0bec03b4f3a5",
}

# ── LLM Setup (Grok primary, OpenAI fallback) ────────────────────────────────
try:
    from langchain_openai import ChatOpenAI
    if GROK_API_KEY:
        llm = ChatOpenAI(
            model="grok-3",
            openai_api_key=GROK_API_KEY,
            openai_api_base="https://api.x.ai/v1",
            temperature=0.7,
        )
    else:
        llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0.7)
    print(f"✅ LLM: {'Grok-3 (xAI)' if GROK_API_KEY else 'GPT-4o-mini (OpenAI)'}")
except ImportError:
    llm = None
    print("⚠️  langchain_openai not installed — LLM disabled")

# ── Stripe Toolkit ───────────────────────────────────────────────────────────
stripe_tools = []
if STRIPE_API_KEY:
    try:
        from stripe_agent_toolkit.crewai.toolkit import StripeAgentToolkit
        stripe_toolkit = StripeAgentToolkit(
            secret_key=STRIPE_API_KEY,
            configuration={
                "actions": {
                    "payment_links": {"create": True},
                    "products": {"create": True, "list": True},
                    "prices": {"create": True, "list": True},
                    "customers": {"create": True, "list": True},
                    "invoices": {"create": True, "list": True},
                    "subscriptions": {"create": True, "list": True},
                    "balance": {"retrieve": True},
                }
            },
        )
        stripe_tools = stripe_toolkit.get_tools()
        print(f"✅ Stripe: {len(stripe_tools)} tools loaded")
    except ImportError:
        print("⚠️  stripe_agent_toolkit not installed")

# ── CrewAI Agents ────────────────────────────────────────────────────────────
try:
    from crewai import Agent, Task, Crew, Process

    orchestrator = Agent(
        role="Master Orchestrator",
        goal="Coordinate all specialist agents to deliver results for keyforagents.com",
        backstory="""You are the NEXUS Orchestrator — the master coordinator of the 
        keyforagents.com AI automation platform. You delegate to specialist agents, 
        ensure quality, and synthesize final outputs. You move fast and deliver results.""",
        verbose=True,
        allow_delegation=True,
        llm=llm,
    )

    outbound_agent = Agent(
        role="Outbound Sales Strategist",
        goal="Generate high-converting outreach sequences for Australian B2B prospects",
        backstory="""You are a world-class B2B sales strategist specialising in Australian 
        markets. You craft 8-touch outreach sequences for real estate agents, law firms, 
        NDIS providers, and pest control companies. Your emails convert at 3x industry average.""",
        verbose=True,
        llm=llm,
    )

    stripe_agent = Agent(
        role="Revenue Engineer",
        goal="Create Stripe products, payment links, and subscription plans for keyforagents.com",
        backstory="""You manage all revenue operations for keyforagents.com. You create 
        Stripe products and payment links for our service tiers: Starter $500/mo, 
        Growth $1,500/mo, Scale $3,500/mo, Enterprise custom. You track MRR and churn.""",
        verbose=True,
        tools=stripe_tools,
        llm=llm,
    )

    growth_agent = Agent(
        role="Growth Hacker",
        goal="Identify and execute growth opportunities across all channels for keyforagents.com",
        backstory="""You are an elite growth hacker who finds hidden revenue streams and 
        viral loops. You analyse markets, identify quick wins, and build systematic growth 
        engines for keyforagents.com and its side hustles.""",
        verbose=True,
        llm=llm,
    )

    content_agent = Agent(
        role="Content Automation Specialist",
        goal="Create viral X/Twitter threads, LinkedIn posts, and blog content at scale",
        backstory="""You produce high-engagement content for keyforagents.com's social channels. 
        You understand Australian B2B audiences and write content that drives inbound leads. 
        You create 4-channel content campaigns (X, LinkedIn, email, blog) simultaneously.""",
        verbose=True,
        llm=llm,
    )

    qa_agent = Agent(
        role="Quality Assurance Lead",
        goal="Verify all outputs meet keyforagents.com standards before delivery",
        backstory="""You are the final checkpoint — nothing ships without your approval. 
        You check outreach for compliance, Stripe setups for accuracy, and content for 
        brand voice alignment. You catch errors and ensure 100% delivery quality.""",
        verbose=True,
        llm=llm,
    )

    print("✅ CrewAI: 6 agents ready (Orchestrator, Outbound, Stripe, Growth, Content, QA)")

except ImportError:
    print("⚠️  crewai not installed — run: pip install crewai")
    sys.exit(1)


# ── Notion helpers ───────────────────────────────────────────────────────────
def notion_add_command(command: str, agent: str, status: str = "Queued",
                        priority: str = "High", source: str = "Manual"):
    """Append a row to the ⚡ Agent Command Center database."""
    import requests
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    data = {
        "parent": {"database_id": NOTION_DBS["commands"]},
        "properties": {
            "Command": {"title": [{"text": {"content": command}}]},
            "Agent":   {"select": {"name": agent}},
            "Status":  {"select": {"name": status}},
            "Priority": {"select": {"name": priority}},
            "Source":  {"select": {"name": source}},
        },
    }
    r = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    if r.status_code == 200:
        print(f"✅ Notion: logged command '{command}'")
    else:
        print(f"⚠️  Notion: {r.status_code} {r.text[:200]}")


def telegram_alert(msg: str):
    """Send a message to Termux88 Telegram channel."""
    if not TELEGRAM_TOKEN:
        return
    import requests
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT, "text": msg, "parse_mode": "Markdown"},
    )


# ── Crew Runners ─────────────────────────────────────────────────────────────

def run_outreach(target: str):
    """Generate 8-touch outreach sequence for a target niche."""
    print(f"\n🚀 OUTREACH CREW → target: {target}")
    notion_add_command(f"outreach: {target}", "Outbound Sales Strategist", priority="🔥 Now")

    task_research = Task(
        description=f"""Research the target niche: {target}
        Find: common pain points, current tech stack, decision-maker titles, 
        average deal sizes, and best outreach timing for Australian businesses.""",
        expected_output="Research brief with 5 pain points, decision-maker personas, timing",
        agent=growth_agent,
    )

    task_sequence = Task(
        description=f"""Using the research brief, create an 8-touch outreach sequence for {target}.
        Include: Subject lines, email bodies (under 150 words each), LinkedIn messages,
        and a cold call script. Make it specific to Australian B2B. CTA = book a 15-min call.""",
        expected_output="Complete 8-touch sequence: 5 emails + 2 LinkedIn + 1 call script",
        agent=outbound_agent,
        context=[task_research],
    )

    task_qa = Task(
        description="Review the outreach sequence for compliance, personalisation, and conversion potential. Score each touch 1-10.",
        expected_output="QA report with scores and 3 improvement suggestions",
        agent=qa_agent,
        context=[task_sequence],
    )

    crew = Crew(
        agents=[growth_agent, outbound_agent, qa_agent],
        tasks=[task_research, task_sequence, task_qa],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    telegram_alert(f"✅ Outreach sequence ready for: *{target}*\n\n{str(result)[:500]}")
    return result


def run_sell(product_name: str, price_cents: int, description: str):
    """Create Stripe product + payment link."""
    print(f"\n💰 SELL CREW → {product_name} @ ${price_cents/100:.0f}/mo")
    notion_add_command(f"sell: {product_name} ${price_cents/100:.0f}", "Revenue Engineer", priority="🔥 Now")

    task_create = Task(
        description=f"""Create a Stripe product and recurring payment link:
        - Product name: {product_name}
        - Price: ${price_cents/100:.0f}/month (AUD)
        - Description: {description}
        - Billing: monthly recurring subscription
        Return the payment link URL.""",
        expected_output="Stripe payment link URL + product ID + price ID",
        agent=stripe_agent,
    )

    crew = Crew(agents=[stripe_agent], tasks=[task_create], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    telegram_alert(f"💰 Stripe product created: *{product_name}*\n${price_cents/100:.0f}/mo\n{str(result)[:300]}")
    return result


def run_campaign(topic: str):
    """Create 4-channel content campaign."""
    print(f"\n📢 CAMPAIGN CREW → topic: {topic}")
    notion_add_command(f"campaign: {topic}", "Content Automation Specialist", priority="High")

    task_content = Task(
        description=f"""Create a 4-channel content campaign for: {topic}
        Produce:
        1. X/Twitter thread (10 tweets, hook + value + CTA)
        2. LinkedIn article (500 words, B2B professional tone)
        3. Email newsletter (300 words, keyforagents.com subscribers)
        4. Blog post outline (H1 + 5 H2s + meta description, SEO-optimised)
        Target audience: Australian B2B decision-makers.""",
        expected_output="Full 4-channel campaign content ready to publish",
        agent=content_agent,
    )

    task_qa = Task(
        description="Review all 4 pieces for brand voice, accuracy, and engagement potential. Give go/no-go for each.",
        expected_output="QA verdicts + any edits needed",
        agent=qa_agent,
        context=[task_content],
    )

    crew = Crew(
        agents=[content_agent, qa_agent],
        tasks=[task_content, task_qa],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    telegram_alert(f"📢 Campaign ready: *{topic}*")
    return result


def run_build_mvp(spec: str):
    """NEXUS-Sprint: Full product build prompt."""
    print(f"\n🏗️  BUILD-MVP CREW → spec: {spec}")
    notion_add_command(f"build-mvp: {spec}", "Master Orchestrator", priority="🔥 Now")

    task_plan = Task(
        description=f"""Using the NEXUS-Sprint framework, create a complete build plan for: {spec}
        Include: PM brief, architecture decision, component breakdown, 
        5-day sprint plan, and acceptance criteria.""",
        expected_output="Full NEXUS-Sprint build plan with all sections",
        agent=orchestrator,
    )

    task_execute = Task(
        description=f"Execute the build plan for {spec}. Write the complete implementation code/content.",
        expected_output="Fully implemented artifact ready for deployment",
        agent=orchestrator,
        context=[task_plan],
    )

    crew = Crew(
        agents=[orchestrator],
        tasks=[task_plan, task_execute],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    telegram_alert(f"🏗️  MVP build complete: *{spec}*")
    return result


# ── CLI Entry ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════╗
║          keyforagents.com — CrewAI Command Crew          ║
╠══════════════════════════════════════════════════════════╣
║  outreach  <target>              8-touch outreach seq    ║
║  sell      <name> <price> <desc> Stripe product+link     ║
║  campaign  <topic>               4-channel content       ║
║  build-mvp <spec>                NEXUS-Sprint build      ║
╚══════════════════════════════════════════════════════════╝
        """)
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "outreach":
        run_outreach(sys.argv[2] if len(sys.argv) > 2 else "real estate agents in Melbourne")
    elif cmd == "sell":
        run_sell(
            sys.argv[2] if len(sys.argv) > 2 else "Growth Package",
            int(sys.argv[3]) * 100 if len(sys.argv) > 3 else 150000,
            sys.argv[4] if len(sys.argv) > 4 else "3 AI workflows + monthly reporting",
        )
    elif cmd == "campaign":
        run_campaign(sys.argv[2] if len(sys.argv) > 2 else "AI automation for Australian SMBs")
    elif cmd == "build-mvp":
        run_build_mvp(sys.argv[2] if len(sys.argv) > 2 else "keyforagents.com homepage")
    else:
        print(f"❌ Unknown command: {cmd}")
        sys.exit(1)
