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



