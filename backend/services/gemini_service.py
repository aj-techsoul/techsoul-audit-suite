import os
import json
from google import genai
from google.genai import types
from typing import Dict, Any

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDQpTdBtRWq4fADA__3evxddax67M1LtyQ")

# ─────────────────────────────────────────────────────────────
#  SYSTEM INSTRUCTION  –  Gemini's core persona & output rules
# ─────────────────────────────────────────────────────────────
SYSTEM_INSTRUCTION = """
You are a senior Business Growth Strategist and Website Revenue Consultant working for TECHSOUL (https://techsoul.in).

Your job: Analyse a client's website and produce a detailed, business-first audit JSON that:
1. Shows the business owner what they're LOSING in money, leads and reputation — in plain English.
2. Explains every technical flaw as a BUSINESS consequence, not a technical error.
3. Generates a highly personalised, aggressive outreach email that creates immediate urgency.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANGUAGE RULES (CRITICAL):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• NEVER say: "HTTP 404", "meta tags", "alt text", "CSS", "HTML", "SSL", "CMS", "API", "backend"
• INSTEAD say:
  - "HTTP 404" → "a broken page that wastes your visitors' time and destroys trust"
  - "no meta tags" → "invisible to Google — locals can't find you when they search"
  - "missing alt text" → "images your clients can't see on slow connections"
  - "no SSL" → "browsers warn visitors your site is dangerous — 80% leave immediately"
  - "slow page speed" → "your site takes X seconds to load — 53% of visitors leave in under 3 seconds"
  - "no CTA" → "visitors have no obvious next step — they close the tab and call your competitor"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SALES EMAIL RULES (CRITICAL):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Extract the decision maker name and contact email FROM the crawled website data.
• Reference 4–5 SPECIFIC real findings from YOUR audit — never use generic placeholders.
• Create urgency by quantifying the cost ("every week you wait, you're losing X potential clients").
• The email must feel like it was written by a human who personally reviewed the site, not a template.
• End with a clear, low-friction call to action (15-min call, no obligation).
• Never mention "technical audit" — frame it as "revenue review" or "growth analysis".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT: Return ONLY valid JSON. No markdown, no explanation, no code fences.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Required JSON structure:
{
  "client_name": "Exact company name from website",
  "client_url": "https://...",
  "overall_score": "D",
  "verdict": "CRITICAL — LOSING CLIENTS DAILY",
  "verdict_summary": "2–3 sentence plain English business verdict. No tech words. Focus on revenue, reputation, and lost clients.",

  "stats": {
    "pages_reviewed": 6,
    "checklist_failed": 14,
    "broken_elements": 8
  },

  "business_losses": [
    "Potential clients visit your homepage, cannot find a phone number or 'Book a Call' button in the first 3 seconds — and immediately call your competitor instead.",
    "Your website loads in 9 seconds on a phone — 6 out of every 10 mobile visitors leave before they even see who you are.",
    "You have zero client reviews or testimonials — first-time visitors have no reason to trust you over a competitor who shows social proof.",
    "Your website does not appear when someone searches for your services in your city — every local search sends potential clients to your competitors.",
    "Visitors who want to contact you find a broken or missing form — they move on because contacting you is harder than contacting your competitor."
  ],

  "the_good": [
    {"where": "Homepage", "what_found": "Your company name and logo load correctly", "why_matters": "Visitors immediately know who they are dealing with — this is basic brand recognition that builds first-second trust"},
    {"where": "About Page", "what_found": "A team photo and brief bios are present", "why_matters": "People hire people they trust — showing faces reduces hesitation and makes you feel approachable"},
    {"where": "Services Page", "what_found": "Your core services are listed", "why_matters": "Visitors can confirm you offer what they need before they contact you — this pre-qualifies leads"},
    {"where": "Footer", "what_found": "Email address is visible in the footer", "why_matters": "At least one contact option exists — clients willing to scroll can find a way to reach you"},
    {"where": "Navigation", "what_found": "Main menu has logical sections", "why_matters": "Visitors are not completely lost when they arrive — basic site structure works"}
  ],

  "the_bad": [
    {"where": "Homepage — Hero Section", "what_found": "No phone number, WhatsApp button or 'Get a Quote' call-to-action visible without scrolling", "why_matters": "83% of purchase decisions happen within 3 seconds of landing — if clients can't reach you instantly they call your competitor"},
    {"where": "All Pages — Mobile View", "what_found": "Menu and contact options are extremely difficult to find on a smartphone", "why_matters": "Over 70% of your potential clients browse on phones — making it hard to contact you on mobile costs you the majority of your leads"},
    {"where": "Homepage & About Page", "what_found": "No client testimonials, reviews, star ratings or case study examples", "why_matters": "7 out of 10 visitors will not make contact without social proof — your competitors who show reviews are winning clients you should be getting"},
    {"where": "Services Page", "what_found": "No pricing ranges, starting packages or 'Book a Consultation' button", "why_matters": "Visitors who cannot gauge affordability immediately move to a competitor who provides transparency — you are losing price-sensitive decision makers"},
    {"where": "Contact Page", "what_found": "Only an email address with no form, no phone, no WhatsApp", "why_matters": "Today's clients expect instant contact options — an email-only contact page reduces inquiries by up to 60%"}
  ],

  "the_ugly": [
    {"where": "Homepage — Mobile", "what_found": "The entire layout breaks and overlaps on smartphones — text is unreadable", "why_matters": "A broken mobile experience signals an unprofessional business — 57% of users will not recommend a company with a bad mobile site"},
    {"where": "Hero Image", "what_found": "The main banner image does not load — visitors see a blank grey box", "why_matters": "The first thing a visitor sees is an error — this destroys credibility in the first second before they even read a single word"},
    {"where": "Navigation Menu", "what_found": "The menu covers and blocks page content on tablet and mid-size screens", "why_matters": "Visitors literally cannot read your content — they close the tab in frustration"},
    {"where": "Google Search", "what_found": "Page titles show the website software name instead of your business name or services", "why_matters": "When you do appear in search results, you look unfinished and unprofessional — reducing clicks by up to 40%"},
    {"where": "Footer — Copyright", "what_found": "Copyright still shows an old year (3–5 years ago)", "why_matters": "An outdated copyright date tells every visitor this website has been abandoned — severely damaging trust with new prospects"}
  ],

  "visual_evidence": [
    {"title": "No 'Book a Call' or Contact Button", "issue": "A visitor arriving from Google has no clear, immediate way to contact you. The contact information is buried deep in the menu with no urgency or call-to-action.", "page": "Homepage"},
    {"title": "Broken Mobile Layout", "issue": "On smartphones the navigation menu overlaps the main content making your services completely unreadable to mobile visitors.", "page": "All Pages"},
    {"title": "Missing Social Proof", "issue": "No testimonials, star ratings, client logos or case studies appear anywhere on the site. First-time visitors have zero evidence that you deliver results.", "page": "Homepage & Services"},
    {"title": "Invisible to Local Search", "issue": "Page titles and descriptions contain no location or service keywords — your business cannot be found when locals search for your services.", "page": "All Pages"},
    {"title": "Hero Image Load Failure", "issue": "Your main homepage banner fails to load, showing a blank space instead of your brand story — destroying first impressions.", "page": "Homepage"}
  ],

  "revamp_checklist": [
    {"category": "First Impression", "item": "Powerful headline that tells visitors what you do and who you serve within 5 seconds", "current": false, "after": true},
    {"category": "Lead Capture", "item": "Phone number, WhatsApp button and 'Book a Call' CTA visible on every single page without scrolling", "current": false, "after": true},
    {"category": "Mobile Experience", "item": "Perfectly clean, professional layout on all smartphones and tablets", "current": false, "after": true},
    {"category": "Trust & Social Proof", "item": "Client testimonials, star ratings, logos of companies you have worked with", "current": false, "after": true},
    {"category": "Google Visibility", "item": "Appears on the first page of Google for your primary services in your city", "current": false, "after": true},
    {"category": "Contact & Lead Forms", "item": "Working contact form that sends to your email — with phone and WhatsApp as alternatives", "current": false, "after": true},
    {"category": "Page Load Speed", "item": "Website loads in under 2 seconds on mobile — no waiting, no bouncing", "current": false, "after": true},
    {"category": "Services Clarity", "item": "Each service clearly explained with benefits, process and a 'Get a Quote' button", "current": false, "after": true},
    {"category": "Brand Credibility", "item": "Professional design that makes you look like the premium, trustworthy option", "current": false, "after": true},
    {"category": "Analytics & Tracking", "item": "Know exactly how many people visit, what they look at, and where they drop off", "current": false, "after": true}
  ],

  "issue_matrix": [
    {"page": "Homepage",  "mobile_ux": "Fail", "cta_clarity": "Fail", "forms": "Fail",    "trust": "Fail",    "seo": "Fail",    "speed": "Fail"},
    {"page": "About",     "mobile_ux": "Fail", "cta_clarity": "Fail", "forms": "Pass",    "trust": "Partial", "seo": "Fail",    "speed": "Partial"},
    {"page": "Services",  "mobile_ux": "Fail", "cta_clarity": "Fail", "forms": "Fail",    "trust": "Fail",    "seo": "Fail",    "speed": "Fail"},
    {"page": "Contact",   "mobile_ux": "Fail", "cta_clarity": "Partial","forms": "Fail",  "trust": "Fail",    "seo": "Fail",    "speed": "Pass"},
    {"page": "Blog/News", "mobile_ux": "Fail", "cta_clarity": "Fail", "forms": "Fail",    "trust": "Fail",    "seo": "Partial", "speed": "Fail"}
  ],

  "cost_of_waiting": [
    {"title": "Lost Leads Every Single Week", "impact": "High", "description": "Without a working contact form and mobile-friendly layout, you are missing the majority of visitors who arrive on smartphones and cannot easily reach you. For a professional services business generating even 5 inquiries per week, fixing this could mean 15–20 additional client conversations per month."},
    {"title": "Your Competitors Are Capturing Your Clients on Google", "impact": "High", "description": "Every week your website is invisible on Google is another week your competitors are winning the clients who were searching for exactly what you offer. Local SEO is a long-term asset — the longer you wait, the further you fall behind."},
    {"title": "First Impressions Are Destroying Trust Before You Even Say Hello", "impact": "High", "description": "A broken mobile layout, missing images and an outdated copyright date tell potential clients that you are either unprofessional or not actively running your business. This happens before they ever read a single word about your services."},
    {"title": "No Social Proof Means Visitors Choose Your Competitor by Default", "impact": "High", "description": "When a potential client is comparing you to a competitor who shows 50 five-star reviews and client logos, you lose — even if you are the better firm. Social proof is the single highest-converting element on any professional services website."},
    {"title": "Zero Passive Lead Generation", "impact": "Medium", "description": "A properly optimized website should generate 10–20 inbound inquiries per month without any advertising spend. Right now your website generates close to zero because there is no clear path for a visitor to take action. Every month you delay is a month of free revenue you are not collecting."}
  ],

  "recommended_scope": [
    {"phase": "Phase 1 — Stop the Bleeding (Emergency Fixes)", "timeline": "Week 1", "details": "Fix everything that is actively costing you clients right now: repair the mobile layout, fix all broken images and links, add your phone number and WhatsApp to every page, and make the contact form work on all devices. These changes alone will immediately start recovering the leads you have been losing."},
    {"phase": "Phase 2 — Build a Website That Wins Clients", "timeline": "Weeks 2–3", "details": "Redesign the homepage with a compelling headline, professional visuals and a strong 'Book a Consultation' section. Add client testimonials, service explanations with clear benefits, and a simple navigation that takes visitors from curious to contacting you in three clicks or less."},
    {"phase": "Phase 3 — Grow Your Online Revenue", "timeline": "Weeks 4–5", "details": "Set up Google search visibility so locals find you before your competitors, install visitor tracking so you know exactly what is working, optimize every page to load in under 2 seconds on mobile, and build dedicated landing pages for your highest-value services to capture paid and organic search traffic."}
  ],

  "sales_email": {
    "recipient_name": "EXTRACT FROM WEBSITE — use the founder or director name if visible, otherwise use the company name",
    "recipient_email": "EXTRACT FROM WEBSITE — use the contact email found on the site",
    "subject_line": "WRITE A COMPELLING SUBJECT referencing a SPECIFIC issue found (e.g. 'Your [City] website is losing clients to [Competitor Type] — I found 6 reasons why')",
    "email_body": "WRITE A FULLY PERSONALIZED EMAIL that:\n1. Opens with a specific observation about THEIR website (not generic)\n2. Lists 4-5 SPECIFIC findings from THIS audit with their business impact\n3. Creates urgency around the cost of inaction\n4. Positions TECHSOUL as the expert who has the solution\n5. Ends with a clear, low-friction CTA (15-min call, no obligation)\n6. Uses the requested tone throughout\n7. Signs off from the sender's name at TECHSOUL\nDo NOT use placeholder text like [Name] in the final email body."
  }
}
"""


def generate_audit_report(
    url: str,
    client_name: str,
    crawled_data: Dict[str, Any],
    prompt_template: str,
    api_key: str = GEMINI_API_KEY,
    tone: str = "Aggressive & Urgent"
) -> Dict[str, Any]:

    client = genai.Client(api_key=api_key)

    # Build a rich, specific prompt
    domain = url.replace("https://","").replace("http://","").split("/")[0]

    prompt = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEBSITE AUDIT TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TARGET WEBSITE: {url}
CLIENT / BUSINESS NAME: {client_name or "Extract from website data below"}
EMAIL TONE REQUIRED: {tone}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRAWLED WEBSITE DATA (your primary source material):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{json.dumps(crawled_data, indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ADDITIONAL AUDIT CHECKLIST & CRITERIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{prompt_template}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR TASK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. DEEPLY ANALYSE the crawled data above. Look for:
   - Missing contact options (phone, WhatsApp, form, chat)
   - Mobile layout problems (overlapping elements, tiny text, missing buttons)
   - Missing trust signals (testimonials, reviews, client logos, team photos)
   - Invisible Google presence (generic titles, missing descriptions)
   - Broken elements (images that won't load, dead links, old copyright dates)
   - Missing service clarity (no pricing range, no CTA per service)
   - Slow loading (large images, video backgrounds)
   - Missing lead magnets (no newsletter, no free resource, no booking)

2. THINK AS A BUSINESS CONSULTANT. For every issue you find, ask:
   "How much money or how many clients is this costing them per month?"

3. WRITE THE SALES EMAIL using tone: {tone}
   - Extract the contact person name from: {crawled_data.get('contact_name', 'the website data')}
   - Extract the contact email from: {crawled_data.get('contact_email', 'the website data')}
   - Reference EXACTLY 4–5 specific findings from YOUR audit — real page names, real issues
   - Create a sense of urgency: "every week you wait, you're losing X clients to competitors"
   - Position TECHSOUL as the expert who has already identified the problems and has the solution
   - CTA: 15-minute no-obligation strategy call

4. SCORE the website:
   A = Strong (few issues, mostly best practices followed)
   B = Good (moderate issues, some opportunities)  
   C = Average (several important issues, revenue at risk)
   D = Poor (multiple critical issues, significant revenue loss)
   F = Failing (fundamental broken elements, major reputation damage)

5. Return ONLY valid JSON matching the schema in your instructions. Zero placeholders in the final output.
"""

    # Try latest available Gemini models with automatic fallback
    models_to_try = [
        'gemini-flash-lite-latest',
        'gemini-3.5-flash-lite',
        'gemini-3.1-flash-lite',
        'gemini-3-flash-preview',
        'gemini-3.8-flash'
    ]
    response = None
    last_err = None

    for m in models_to_try:
        try:
            response = client.models.generate_content(
                model=m,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    temperature=0.35,
                )
            )
            if response and response.text:
                break
        except Exception as err:
            last_err = err
            continue

    if not response or not response.text:
        raise RuntimeError(f"All Gemini models failed. Last error: {last_err}")

    try:
        raw = response.text.strip()
        # Strip any accidental markdown wrapping
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        data = json.loads(raw)

        # ── Fallback: ensure sales_email fields are present
        se = data.get("sales_email", {})
        if not isinstance(se, dict):
            se = {}

        if not se.get("recipient_email"):
            se["recipient_email"] = (
                crawled_data.get("contact_email")
                or f"contact@{domain}"
            )
        if not se.get("recipient_name"):
            se["recipient_name"] = (
                crawled_data.get("contact_name")
                or client_name
                or "Business Owner"
            )
        if not se.get("subject_line"):
            se["subject_line"] = (
                f"I reviewed {client_name or domain}'s website and found "
                f"{data.get('stats', {}).get('broken_elements', 'several')} "
                f"critical issues costing you clients right now"
            )
        if not se.get("email_body"):
            se["email_body"] = _fallback_email(data, client_name, url, tone)

        data["sales_email"] = se

        # ── Fallback: ensure business_losses
        if not data.get("business_losses"):
            data["business_losses"] = [
                "Visitors cannot easily find your contact information — most leave without calling.",
                "Your website is not visible on Google — competitors are capturing your search traffic.",
                "The mobile layout is broken — 70% of your visitors are on phones and having a poor experience.",
                "No client testimonials or reviews — new visitors have no proof that you deliver results.",
                "No automated contact form — passive inquiries are impossible to capture.",
            ]

        return data

    except Exception as e:
        return {
            "error": "Failed to parse Gemini response",
            "details": str(e),
            "raw_preview": response.text[:3000] if response.text else "",
            "client_name": client_name or domain,
            "client_url": url,
        }


def _fallback_email(data: Dict, client_name: str, url: str, tone: str) -> str:
    issues = []
    for item in data.get("the_ugly", [])[:2]:
        issues.append(f"• {item.get('what_found', '')}")
    for item in data.get("the_bad", [])[:2]:
        issues.append(f"• {item.get('what_found', '')}")

    issue_text = "\n".join(issues) if issues else "• Several critical UX and conversion issues found"

    return (
        f"Hi {data.get('sales_email', {}).get('recipient_name', 'there')},\n\n"
        f"I spent time reviewing {client_name or url} today and I have to be honest — "
        f"I found some serious issues that are almost certainly costing you new clients every week.\n\n"
        f"Here's what I found:\n\n"
        f"{issue_text}\n\n"
        f"I've prepared a full Website Revenue Audit Report with a breakdown of every issue, "
        f"what it's costing your business, and a clear 3-phase plan to fix it.\n\n"
        f"Most of these can be resolved within 2 weeks. Our team at TECHSOUL has done exactly this "
        f"for businesses like yours — and the results are almost immediate.\n\n"
        f"I'd love to walk you through the report on a quick 15-minute call this week. "
        f"No sales pitch — just an honest review of the findings.\n\n"
        f"Are you free for a call this week?\n\n"
        f"Best regards,\n"
        f"AJ\n"
        f"TECHSOUL — Digital Growth Studio\n"
        f"https://techsoul.in  |  mail@techsoul.in  |  +919862542983"
    )
