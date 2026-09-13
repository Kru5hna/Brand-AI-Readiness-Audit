"""
Engagement & Conversion Audit Check
Audits above-the-fold value proposition, deep-link context retention,
intrusive popup friction, and conversion CTA pathways for AI citation arrivals.
"""

import argparse
import json
import re
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests

ACTIONABLE_CTA_TERMS = [
    "get started", "start free", "try free", "sign up", "book demo",
    "request demo", "schedule demo", "contact sales", "download",
    "start trial", "explore", "learn more", "buy now", "documentation"
]


def audit_page_engagement(html: str, target_url: str) -> tuple:
    findings = []
    metadata = {}
    soup = BeautifulSoup(html, "html.parser")
    parsed = urlparse(target_url)
    is_deep_page = bool(parsed.path and parsed.path.strip("/") and parsed.path.strip("/") not in ["index.html", "index.php"])

    # 1. Above-the-fold Value Proposition Clarity
    hero_container = soup.find(["section", "header", "div"], attrs={
        "class": re.compile(r"hero|banner|intro|jumbotron|header-content", re.I)
    })
    
    h1 = soup.find("h1")
    has_subhead = False
    subhead_text = ""

    if hero_container:
        subhead = hero_container.find(["p", "h2", "div"], attrs={"class": re.compile(r"subtitle|lead|desc|subhead|tagline", re.I)})
        if not subhead:
            subhead = hero_container.find("p")
        if subhead and len(subhead.get_text(strip=True).split()) >= 6:
            has_subhead = True
            subhead_text = subhead.get_text(strip=True)
    elif h1:
        # Check next sibling
        next_sibling = h1.find_next_sibling(["p", "h2", "div"])
        if next_sibling and len(next_sibling.get_text(strip=True).split()) >= 6:
            has_subhead = True
            subhead_text = next_sibling.get_text(strip=True)

    metadata["has_hero_container"] = hero_container is not None
    metadata["has_h1"] = h1 is not None
    metadata["has_explanatory_subhead"] = has_subhead

    if not has_subhead:
        findings.append({
            "id": "F-ENG-HERO-UNCLEAR",
            "title": "Unclear above-the-fold value proposition",
            "severity": "high",
            "category": "engagement",
            "evidence": "Above-the-fold section lacks a clear explanatory subhead or value proposition statement adjacent to the main headline. Visitors arriving via AI citation cannot immediately confirm relevance.",
            "suggested_action": {
                "summary": "Add a prominent 1-2 sentence value proposition subhead directly below the primary H1.",
                "priority": "high",
                "details": "Clearly state the primary benefit and target audience within the visible viewport to retain incoming visitors.",
                "code_example": "<h1>Automate Your Cloud Security Audits</h1>\n<p class=\"hero-subhead\">Scan Kubernetes clusters and AWS infrastructure continuously with one-click compliance reports.</p>"
            }
        })

    # 2. Deep-Link Context Retention (Breadcrumbs & Parent Navigation)
    if is_deep_page:
        breadcrumb = soup.find(["nav", "ol", "ul", "div"], attrs={
            "aria-label": re.compile(r"breadcrumb", re.I)
        })
        if not breadcrumb:
            breadcrumb = soup.find(attrs={"class": re.compile(r"breadcrumb|crumbs|site-map-path", re.I)})

        metadata["has_breadcrumbs"] = breadcrumb is not None
        if not breadcrumb:
            findings.append({
                "id": "F-ENG-DEEP-NO-BREADCRUMBS",
                "title": "Deep-link page lacks contextual breadcrumb navigation",
                "severity": "high",
                "category": "engagement",
                "evidence": f"Visitor landed directly on deep page '{parsed.path}', but page lacks semantic breadcrumbs (<nav aria-label=\"breadcrumb\">). AI citation referrals lack orientation within site taxonomy.",
                "suggested_action": {
                    "summary": "Implement semantic HTML breadcrumbs and BreadcrumbList JSON-LD on all deep subpages.",
                    "priority": "high",
                    "details": "Breadcrumbs allow visitors landing on specific documentation, feature, or pricing pages to instantly grasp the parent product context.",
                    "code_example": "<nav aria-label=\"breadcrumb\">\n  <ol class=\"breadcrumbs\">\n    <li><a href=\"/\">Home</a></li>\n    <li><a href=\"/solutions\">Solutions</a></li>\n    <li aria-current=\"page\">Cloud Security</li>\n  </ol>\n</nav>"
                }
            })

    # 3. Friction & Obstructive Overlays / Modals
    modals = soup.find_all(attrs={"role": "dialog"})
    intrusive_popups = soup.find_all(attrs={"class": re.compile(r"popup-overlay|interstitial-modal|newsletter-modal|exit-intent", re.I)})
    total_overlays = len(modals) + len(intrusive_popups)
    metadata["intrusive_overlay_count"] = total_overlays

    if total_overlays > 0:
        findings.append({
            "id": "F-ENG-INTRUSIVE-OVERLAYS",
            "title": "Intrusive modal overlays or popup interstitials detected in DOM",
            "severity": "medium",
            "category": "engagement",
            "evidence": f"Found {total_overlays} modal or overlay element(s) in the DOM. Immediate popups cause severe bounce rates for visitors arriving from AI assistants.",
            "suggested_action": {
                "summary": "Replace instant blocking modals with non-intrusive banners or delay triggers.",
                "priority": "medium",
                "details": "Ensure referral visitors can read content uninterrupted for at least 15 seconds before surfacing newsletter or survey prompts."
            }
        })

    # 4. Call-to-Action (CTA) Audit
    cta_candidates = soup.find_all(["a", "button", "input"], attrs={
        "class": re.compile(r"btn|button|cta|action", re.I)
    })
    # also scan all buttons
    all_buttons = soup.find_all("button")
    unique_elements = set(cta_candidates + all_buttons)

    actionable_ctas = []
    for el in unique_elements:
        text = el.get_text(strip=True).lower()
        if not text and el.name == "input":
            text = (el.get("value") or "").lower()
        if any(term in text for term in ACTIONABLE_CTA_TERMS):
            actionable_ctas.append(text)

    metadata["detected_actionable_ctas"] = actionable_ctas[:5]
    if not actionable_ctas:
        findings.append({
            "id": "F-ENG-MISSING-CTA",
            "title": "Missing prominent or clear Call-to-Action (CTA) pathway",
            "severity": "medium",
            "category": "engagement",
            "evidence": "No high-contrast, clearly worded Call-to-Action buttons (e.g. 'Get Started', 'Try Free', 'Documentation') found on the page.",
            "suggested_action": {
                "summary": "Add a prominent primary CTA button above the fold and at key content milestones.",
                "priority": "medium",
                "details": "Visitors arriving with high intent from an AI recommendation need an unambiguous next step to convert.",
                "code_example": "<a href=\"/signup\" class=\"btn btn-primary\">Start Free Trial &rarr;</a>"
            }
        })

    return findings, metadata


def run_audit(target_url: str, html: str = None, session: requests.Session = None) -> dict:
    if not html:
        if not session:
            session = requests.Session()
            session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; BrandAIAuditAgent/1.0; +https://agentskills.io)"})
        resp = session.get(target_url, timeout=10)
        html = resp.text

    findings, meta = audit_page_engagement(html, target_url)
    return {
        "skill": "engagement-conversion-audit",
        "findings": findings,
        "metadata": meta
    }


def main():
    parser = argparse.ArgumentParser(description="Audit above-the-fold value prop, deep-link orientation, modal friction, and CTAs.")
    parser.add_argument("--url", required=True, help="Target website URL")
    parser.add_argument("--output", help="Optional path to output findings JSON")
    args = parser.parse_args()

    results = run_audit(args.url)
    output_json = json.dumps(results, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"Findings written to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
