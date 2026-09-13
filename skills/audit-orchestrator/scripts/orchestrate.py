"""
Audit Orchestrator - Master Entrypoint
Coordinates multi-skill website evaluation, aggregates findings across discovered pages,
synthesizes proactive recommendations, and emits a standard JSON audit report.
"""

import argparse
from datetime import datetime, timezone
import json
import os
import re
import sys
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

# Import sibling skill modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

if SKILLS_DIR not in sys.path:
    sys.path.insert(0, SKILLS_DIR)

from importlib import import_module

crawler_skill = import_module("crawler-access-audit.scripts.check_crawl_render")
data_skill = import_module("structured-data-entity-audit.scripts.check_structured_data")
extract_skill = import_module("content-extractability-audit.scripts.check_extractability")
engage_skill = import_module("engagement-conversion-audit.scripts.check_engagement")
reporter = import_module("audit-orchestrator.scripts.reporter")

SAMPLE_PAGE_PATTERNS = [
    r"/(?:products?|solutions?|features?|pricing|about|docs?|blog)/?"
]


def discover_representative_pages(base_url: str, root_html: str, max_pages: int = 5) -> list:
    """
    Discovers candidate subpages (e.g. pricing, product, docs) from internal navigation.
    """
    discovered = [base_url]
    parsed_base = urlparse(base_url)
    soup = BeautifulSoup(root_html, "html.parser")

    candidates = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full_url = urljoin(base_url, href)
        parsed_target = urlparse(full_url)
        # stay on same domain
        if parsed_target.netloc.lower() == parsed_base.netloc.lower():
            path = parsed_target.path
            if path and path != parsed_base.path:
                for pat in SAMPLE_PAGE_PATTERNS:
                    if re.search(pat, path, re.I):
                        candidates.add(f"{parsed_target.scheme}://{parsed_target.netloc}{path}")
                        break

    for c in sorted(candidates):
        if len(discovered) >= max_pages:
            break
        if c not in discovered:
            discovered.append(c)

    return discovered


def generate_proactive_recommendations(findings: list, base_url: str) -> list:
    """
    Produces beyond-problem forward-looking enhancements to maximize AI search readiness.
    """
    recs = [
        {
            "title": "Adopt the /llms.txt AI Context Standard",
            "impact": "High",
            "recommendation": "Deploy /llms.txt and /llms-full.txt at the website root containing curated markdown links and concise summaries of documentation, products, and APIs. This eliminates HTML parsing overhead for ChatGPT, Claude, and Perplexity crawlers."
        },
        {
            "title": "Establish Knowledge Graph Entity Authority via Wikidata",
            "impact": "High",
            "recommendation": "Create or claim an official Wikidata entity item for the organization and link it in the homepage Organization JSON-LD 'sameAs' array. Grounding in Wikidata prevents LLM namesake confusion."
        },
        {
            "title": "Inverted-Pyramid Conversational Answer Optimization",
            "impact": "Medium",
            "recommendation": "Ensure all core service and feature pages begin with a declarative 40-word definition sentence followed by a 3-bullet key fact summary. LLM retrieval systems prioritize pages that provide crisp, self-contained answers in the first chunk."
        },
        {
            "title": "Deploy Schema.org FAQPage on High-Intent Commercial Pages",
            "impact": "Medium",
            "recommendation": "Add structured FAQPage JSON-LD schemas answering common pricing, integration, and security questions. AI assistants directly parse FAQ markup to synthesize answers to comparative queries."
        }
    ]
    return recs


def run_orchestrated_audit(target_url: str, max_pages: int = 5, timeout: int = 8) -> dict:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; BrandAIAuditAgent/1.0; +https://agentskills.io)"
    })

    parsed = urlparse(target_url)
    if not parsed.scheme:
        target_url = f"https://{target_url}"
        parsed = urlparse(target_url)

    site_hostname = parsed.netloc

    # Step 1: Execute Crawler Access Audit on Origin
    crawl_result = crawler_skill.run_audit(target_url, session=session)
    raw_findings = list(crawl_result.get("findings", []))

    # Fetch root HTML
    root_html = ""
    try:
        resp = session.get(target_url, timeout=timeout)
        root_html = resp.text
    except Exception as ex:
        raw_findings.append({
            "id": "F-ORCH-FETCH-ERROR",
            "title": "Target root URL could not be fetched",
            "severity": "critical",
            "category": "discoverability",
            "evidence": f"Failed to retrieve {target_url}: {str(ex)}",
            "suggested_action": {
                "summary": "Check server uptime, SSL configuration, and domain routing.",
                "priority": "critical"
            }
        })

    # Step 2: Discover Pages
    pages_to_audit = [target_url]
    if root_html:
        pages_to_audit = discover_representative_pages(target_url, root_html, max_pages=max_pages)

    # Step 3: Execute Content, Structured Data, and Engagement Audits across sampled pages
    seen_finding_ids = set(f["id"] for f in raw_findings)

    for page_url in pages_to_audit:
        try:
            page_html = root_html if page_url == target_url else session.get(page_url, timeout=timeout).text
        except Exception:
            continue

        # Run structured data audit
        sd_res = data_skill.run_audit(page_url, html=page_html, session=session)
        for f in sd_res.get("findings", []):
            fid = f["id"]
            if fid not in seen_finding_ids:
                seen_finding_ids.add(fid)
                raw_findings.append(f)

        # Run content extractability audit
        ce_res = extract_skill.run_audit(page_url, html=page_html, session=session)
        for f in ce_res.get("findings", []):
            fid = f["id"]
            if fid not in seen_finding_ids:
                seen_finding_ids.add(fid)
                raw_findings.append(f)

        # Run engagement audit
        eng_res = engage_skill.run_audit(page_url, html=page_html, session=session)
        for f in eng_res.get("findings", []):
            fid = f["id"]
            if fid not in seen_finding_ids:
                seen_finding_ids.add(fid)
                raw_findings.append(f)

    # Step 4: Proactive Recommendations
    proactive_recs = generate_proactive_recommendations(raw_findings, target_url)

    # Step 5: Format & Validate Standard Schema Report
    report = reporter.build_audit_report(
        site=site_hostname,
        findings=raw_findings,
        proactive_recommendations=proactive_recs
    )

    validation_errors = reporter.validate_report_schema(report)
    if validation_errors:
        sys.stderr.write(f"Schema validation warnings: {validation_errors}\n")

    return report


def main():
    parser = argparse.ArgumentParser(description="Master Audit Orchestrator for Brand AI-Readiness.")
    parser.add_argument("--url", required=True, help="Target website URL or domain")
    parser.add_argument("--max-pages", type=int, default=5, help="Max representative pages to crawl")
    parser.add_argument("--timeout", type=int, default=8, help="Request timeout in seconds")
    parser.add_argument("--output", help="Output file path for report")
    parser.add_argument("--format", choices=["json", "markdown", "both"], default="json", help="Output format")
    args = parser.parse_args()

    report = run_orchestrated_audit(args.url, max_pages=args.max_pages, timeout=args.timeout)

    json_str = json.dumps(report, indent=2)
    md_str = reporter.render_markdown_report(report)

    if args.format in ["json", "both"]:
        if args.output:
            out_path = args.output if args.output.endswith(".json") else f"{args.output}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"JSON report written to: {out_path}")
        else:
            print(json_str)

    if args.format in ["markdown", "both"]:
        if args.output:
            md_path = args.output if args.output.endswith(".md") else f"{args.output}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_str)
            print(f"Markdown report written to: {md_path}")
        elif args.format == "markdown":
            print(md_str)


if __name__ == "__main__":
    main()
