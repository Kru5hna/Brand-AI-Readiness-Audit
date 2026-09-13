"""
Content Extractability & Freshness Audit Check
Audits AI quotability, RAG chunking friendliness, information density,
temporal freshness signals, and /llms.txt availability.
"""

import argparse
from datetime import datetime
import json
import re
import sys
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

DEFINITION_PATTERNS = [
    r"\b(?:is|are)\s+(?:an?|the)\s+[\w\s]{2,30}\s+(?:for|that|which|to)\b",
    r"\b(?:provides|delivers|builds|powers|enables|offers|automates)\s+[\w\s]{2,40}\b",
    r"\b(?:platform|framework|engine|solution|service|tool|software)\s+(?:for|to|that)\b"
]


def audit_quotability_and_density(soup: BeautifulSoup, target_url: str) -> tuple:
    findings = []
    metadata = {}

    # Isolate main content vs boilerplate
    nav_and_footers = soup.find_all(["nav", "header", "footer", "aside"])
    boilerplate_words = 0
    for tag in nav_and_footers:
        text = tag.get_text(separator=" ", strip=True)
        boilerplate_words += len(text.split())

    # Get clean clone for substantive content
    content_soup = BeautifulSoup(str(soup), "html.parser")
    for t in content_soup(["script", "style", "noscript", "svg", "nav", "footer", "header", "aside"]):
        t.decompose()

    main_tag = content_soup.find(["main", "article"])
    if main_tag:
        substantive_text = main_tag.get_text(separator=" ", strip=True)
    else:
        body = content_soup.find("body")
        substantive_text = body.get_text(separator=" ", strip=True) if body else ""

    sub_words = [w for w in substantive_text.split() if len(w) > 1]
    total_substantive = len(sub_words)
    metadata["substantive_word_count"] = total_substantive
    metadata["boilerplate_word_count"] = boilerplate_words

    # 1. Quotability Check on Opening Text (first 250 words)
    opening_text = " ".join(sub_words[:250])
    has_def = any(re.search(pat, opening_text, re.I) for pat in DEFINITION_PATTERNS)

    if total_substantive > 40 and not has_def:
        findings.append({
            "id": "F-CONT-LOW-QUOTABILITY",
            "title": "Low AI quotability — opening text lacks a clear declarative definition",
            "severity": "high",
            "category": "discoverability",
            "evidence": f"Opening text ({len(opening_text.split())} words) does not contain a concise definition of what the brand/product is or does. AI search engines struggle to extract direct answer snippets.",
            "suggested_action": {
                "summary": "Adopt the Inverted Pyramid structure with a clear 1-2 sentence declarative definition in the first 100 words.",
                "priority": "high",
                "details": "State '<Brand> is a <category> that <core function> for <target user>' in the hero lead paragraph to maximize RAG snippet extraction.",
                "code_example": "<p class=\"lead\">Acme is an automated cloud compliance platform that monitors infrastructure security in real time for DevOps teams.</p>"
            }
        })

    # 2. Information Density vs Boilerplate Ratio
    total_words = total_substantive + boilerplate_words
    if total_words > 200:
        density_ratio = total_substantive / total_words
        metadata["density_ratio"] = round(density_ratio, 2)
        if density_ratio < 0.30:
            findings.append({
                "id": "F-CONT-LOW-DENSITY",
                "title": "Low information density — page is dominated by navigation and boilerplate",
                "severity": "medium",
                "category": "discoverability",
                "evidence": f"Substantive content comprises only {int(density_ratio*100)}% of visible text ({total_substantive} content words vs {boilerplate_words} boilerplate words). LLM scrapers may discard the page as low-value.",
                "suggested_action": {
                    "summary": "Delineate substantive content using semantic <main> and <article> tags and consolidate navigation.",
                    "priority": "medium",
                    "details": "AI text extraction parsers (such as Readability and Trafilatura) drop pages where navigational boilerplate overwhelms factual text."
                }
            })

    return findings, metadata


def audit_freshness(soup: BeautifulSoup, html: str, current_year: int = 2026) -> list:
    findings = []
    # Search for copyright year in footer or body
    copyright_matches = re.findall(r"(?:©|&copy;|copyright)\s*(?:(?:19|20)\d{2}\s*[-–—]\s*)?((?:19|20)\d{2})", html, re.I)
    if copyright_matches:
        years = [int(y) for y in copyright_matches if y.isdigit()]
        if years:
            max_year = max(years)
            if max_year <= current_year - 2:
                findings.append({
                    "id": "F-CONT-STALE-COPYRIGHT",
                    "title": "Outdated copyright date indicates unmaintained or stale content",
                    "severity": "medium",
                    "category": "discoverability",
                    "evidence": f"Detected copyright year '{max_year}' in page footer (current audit year is {current_year}). AI assistants penalize stale recency signals.",
                    "suggested_action": {
                        "summary": f"Update footer copyright year to {current_year} or implement dynamic year injection.",
                        "priority": "medium",
                        "code_example": f"<p>&copy; {current_year} BrandName, Inc. All rights reserved.</p>"
                    }
                })

    # Check for meta date tags
    meta_mod = soup.find("meta", attrs={"property": re.compile(r"article:modified_time|og:updated_time", re.I)})
    if not meta_mod:
        meta_pub = soup.find("meta", attrs={"property": re.compile(r"article:published_time", re.I)})
        if meta_pub:
            findings.append({
                "id": "F-CONT-MISSING-MODIFIED-TIME",
                "title": "Article published date lacks modified_time update stamp",
                "severity": "low",
                "category": "discoverability",
                "evidence": f"Found published date '{meta_pub.get('content')}' but no article:modified_time metadata.",
                "suggested_action": {
                    "summary": "Emit article:modified_time metadata to indicate fresh content revisions.",
                    "priority": "low"
                }
            })

    return findings


def audit_llms_txt(base_url: str, session: requests.Session) -> list:
    findings = []
    llms_url = urljoin(base_url, "/llms.txt")
    try:
        resp = session.get(llms_url, timeout=6)
        if resp.status_code != 200:
            findings.append({
                "id": "F-CONT-LLMSTXT-MISSING",
                "title": "Missing /llms.txt standard file for AI assistant navigation",
                "severity": "medium",
                "category": "discoverability",
                "evidence": f"GET {llms_url} returned HTTP {resp.status_code}. The site has not adopted the emerging /llms.txt standard for AI crawlers.",
                "suggested_action": {
                    "summary": "Deploy a curated /llms.txt markdown index at the site root.",
                    "priority": "medium",
                    "details": "The /llms.txt specification enables AI assistants like ChatGPT and Claude to ingest clean markdown links without parsing heavy HTML.",
                    "code_example": "# Brand Documentation\n> One-line brand summary\n\n## Core Docs\n- [API Guide](/docs/api.md): Endpoint references\n- [Product Overview](/products.md): Feature breakdown"
                }
            })
    except requests.RequestException:
        pass
    return findings


def run_audit(target_url: str, html: str = None, session: requests.Session = None) -> dict:
    if not session:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; BrandAIAuditAgent/1.0; +https://agentskills.io)"})

    parsed = urlparse(target_url)
    if not parsed.scheme:
        target_url = f"https://{target_url}"
        parsed = urlparse(target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    if not html:
        resp = session.get(target_url, timeout=10)
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")
    all_findings = []

    q_findings, meta = audit_quotability_and_density(soup, target_url)
    all_findings.extend(q_findings)

    f_findings = audit_freshness(soup, html)
    all_findings.extend(f_findings)

    llms_findings = audit_llms_txt(base_url, session)
    all_findings.extend(llms_findings)

    return {
        "skill": "content-extractability-audit",
        "findings": all_findings,
        "metadata": meta
    }


def main():
    parser = argparse.ArgumentParser(description="Audit AI quotability, information density, freshness, and /llms.txt.")
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
