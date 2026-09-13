"""
Structured Data & Entity Audit Check
Audits Schema.org JSON-LD, entity disambiguation (sameAs), non-text trapped facts,
and semantic heading hierarchies.
"""

import argparse
import json
import re
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests

AUTHORITATIVE_SAMEAS_DOMAINS = [
    "wikidata.org",
    "wikipedia.org",
    "linkedin.com",
    "crunchbase.com",
    "github.com",
    "twitter.com",
    "x.com"
]


def extract_jsonld_nodes(soup: BeautifulSoup) -> tuple:
    nodes = []
    syntax_errors = []
    scripts = soup.find_all("script", attrs={"type": re.compile(r"application/ld\+json", re.I)})
    for s in scripts:
        raw_text = s.string or s.get_text()
        if not raw_text or not raw_text.strip():
            continue
        try:
            data = json.loads(raw_text.strip())
            if isinstance(data, list):
                nodes.extend(data)
            elif isinstance(data, dict):
                if "@graph" in data and isinstance(data["@graph"], list):
                    nodes.extend(data["@graph"])
                else:
                    nodes.append(data)
        except Exception as ex:
            syntax_errors.append(str(ex))
    return nodes, syntax_errors


def audit_structured_data_and_entities(html: str, target_url: str) -> tuple:
    findings = []
    metadata = {}
    soup = BeautifulSoup(html, "html.parser")
    nodes, syntax_errors = extract_jsonld_nodes(soup)

    metadata["jsonld_block_count"] = len(nodes)
    if syntax_errors:
        findings.append({
            "id": "F-DATA-JSONLD-SYNTAX-ERR",
            "title": "Malformed JSON-LD structured data syntax",
            "severity": "high",
            "category": "discoverability",
            "evidence": f"Encountered {len(syntax_errors)} JSON parsing error(s) in <script type=\"application/ld+json\"> blocks: {syntax_errors[0]}.",
            "suggested_action": {
                "summary": "Fix syntax errors in JSON-LD markup to ensure parsers can extract structured facts.",
                "priority": "high",
                "details": "Validate JSON-LD snippets through Schema.org validator or Google Rich Results Test."
            }
        })

    # Collect all @type declarations
    types_found = set()
    all_same_as = []
    org_nodes = []
    product_nodes = []

    for n in nodes:
        t = n.get("@type")
        if isinstance(t, list):
            types_found.update(t)
            if any(item in ["Organization", "Corporation"] for item in t):
                org_nodes.append(n)
            if any(item in ["Product", "SoftwareApplication", "Service"] for item in t):
                product_nodes.append(n)
        elif isinstance(t, str):
            types_found.add(t)
            if t in ["Organization", "Corporation"]:
                org_nodes.append(n)
            if t in ["Product", "SoftwareApplication", "Service"]:
                product_nodes.append(n)

        # check sameAs
        sa = n.get("sameAs")
        if isinstance(sa, list):
            all_same_as.extend(sa)
        elif isinstance(sa, str):
            all_same_as.append(sa)

    metadata["schema_types_found"] = list(types_found)

    parsed = urlparse(target_url)
    is_homepage = parsed.path in ["", "/", "/index.html", "/index.php"]

            return findings, metadata
