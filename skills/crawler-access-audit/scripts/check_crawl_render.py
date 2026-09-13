"""
Crawler Access & Render Audit Check
Audits robots.txt AI crawler policies, HTTP bot headers, meta robots directives,
and Client-Side Rendering (CSR) hydration walls.
"""

import argparse
import json
import re
import sys
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

AI_AGENTS = [
    "GPTBot",
    "OAI-SearchBot",
    "ClaudeBot",
    "PerplexityBot",
    "Google-Extended",
    "CCBot",
    "Bytespider",
    "cohere-ai",
    "Amazonbot",
    "Applebot-Extended"
]

CRITICAL_PATHS = ["/_next/", "/static/", "/assets/", "/api/"]


def audit_robots_txt(base_url: str, session: requests.Session) -> list:
    findings = []
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        resp = session.get(robots_url, timeout=8)
        if resp.status_code == 404:
            findings.append({
                "id": "F-CRAWL-ROBOTS-404",
                "title": "Missing robots.txt file",
                "severity": "medium",
                "category": "discoverability",
                "evidence": f"GET {robots_url} returned HTTP 404 Not Found.",
                "suggested_action": {
                    "summary": "Create a standardized robots.txt file declaring open access for search and AI retrieval agents.",
                    "priority": "medium",
                    "details": "Include explicit directives allowing GPTBot, ClaudeBot, and PerplexityBot, plus declare the sitemap location.",
                    "code_example": "User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\nSitemap: " + urljoin(base_url, "/sitemap.xml")
                }
            })
            return findings

        if resp.status_code != 200:
            return findings

        content = resp.text
        lines = [line.strip() for line in content.splitlines()]

        # Parse robots blocks
        current_agents = []
        agent_disallows = {}
        sitemap_found = False

        for line in lines:
            line_clean = line.split("#")[0].strip()
            if not line_clean:
                continue

            lower_line = line_clean.lower()
            if lower_line.startswith("user-agent:"):
                agent_name = line_clean.split(":", 1)[1].strip()
                current_agents.append(agent_name)
            elif lower_line.startswith("disallow:"):
                path = line_clean.split(":", 1)[1].strip()
                for ag in current_agents:
                    agent_disallows.setdefault(ag, []).append(path)
            elif lower_line.startswith("sitemap:"):
                sitemap_found = True
            elif lower_line.startswith("allow:"):
                pass
            else:
                current_agents = []

        # Check universal block
        universal_blocks = agent_disallows.get("*", [])
        if "/" in universal_blocks:
            findings.append({
                "id": "F-CRAWL-UNIVERSAL-DISALLOW",
                "title": "Universal robots.txt disallow blocks all crawlers",
                "severity": "critical",
                "category": "discoverability",
                "evidence": "robots.txt contains 'User-agent: * Disallow: /', blocking all automated crawlers including AI assistants.",
                "suggested_action": {
                    "summary": "Remove root disallow from robots.txt to permit indexing by public search and AI retrieval crawlers.",
                    "priority": "critical",
                    "details": "Change 'Disallow: /' to 'Allow: /' for public directories.",
                    "code_example": "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /private/"
                }
            })

        # Check AI specific crawler blocks
        blocked_ai = []
        for ai_agent in AI_AGENTS:
            disallows = agent_disallows.get(ai_agent, [])
            if "/" in disallows:
                blocked_ai.append(ai_agent)

        if blocked_ai:
            findings.append({
                "id": "F-CRAWL-AI-BOTS-BLOCKED",
                "title": "AI search & retrieval crawlers explicitly blocked in robots.txt",
                "severity": "high",
                "category": "discoverability",
                "evidence": f"robots.txt explicitly blocks: {', '.join(blocked_ai)} with Disallow: /.",
                "suggested_action": {
                    "summary": f"Allow verified AI citation bots ({', '.join(blocked_ai[:3])}) in robots.txt.",
                    "priority": "high",
                    "details": "Explicitly declare Allow: / for AI retrieval bots to ensure the site is referenced in conversational answers.",
                    "code_example": "".join(f"User-agent: {bot}\nAllow: /\n" for bot in blocked_ai[:3])
                }
            })

        # Check critical asset blocking
        blocked_assets = []
        all_disallows = set(p for dis in agent_disallows.values() for p in dis)
        for cp in CRITICAL_PATHS:
            if any(cp.startswith(d) or d.startswith(cp) for d in all_disallows if d and d != "/"):
                blocked_assets.append(cp)

        if blocked_assets:
            findings.append({
                "id": "F-CRAWL-ASSETS-BLOCKED",
                "title": "Critical JS/CSS asset paths blocked in robots.txt",
                "severity": "high",
                "category": "discoverability",
                "evidence": f"robots.txt disallows critical asset paths: {', '.join(blocked_assets)}.",
                "suggested_action": {
                    "summary": "Permit crawler access to CSS, JS, and font assets in robots.txt.",
                    "priority": "high",
                    "details": "Crawlers need CSS and client assets to correctly determine layout and mobile readability.",
                    "code_example": "User-agent: *\nAllow: /_next/\nAllow: /static/\nAllow: /assets/"
                }
            })

        if not sitemap_found:
            findings.append({
                "id": "F-CRAWL-SITEMAP-MISSING-ROBOTS",
                "title": "Sitemap reference missing from robots.txt",
                "severity": "medium",
                "category": "discoverability",
                "evidence": "robots.txt does not declare any 'Sitemap:' directive.",
                "suggested_action": {
                    "summary": "Append the absolute sitemap URL to the bottom of robots.txt.",
                    "priority": "medium",
                    "details": "Enables immediate discovery of page inventory by new crawlers.",
                    "code_example": f"Sitemap: {urljoin(base_url, '/sitemap.xml')}"
                }
            })

    except requests.RequestException as ex:
        findings.append({
            "id": "F-CRAWL-ROBOTS-NETWORK-ERR",
            "title": "Unable to fetch robots.txt due to network error",
            "severity": "medium",
            "category": "discoverability",
            "evidence": f"Error fetching {robots_url}: {str(ex)}",
            "suggested_action": {
                "summary": "Ensure robots.txt is publicly accessible over standard HTTPS.",
                "priority": "medium"
            }
        })

    return findings


def audit_page_render_and_headers(url: str, session: requests.Session) -> tuple:
    findings = []
    metadata = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; GPTBot/1.0; +https://openai.com/gptbot)"
    }

    try:
        resp = session.get(url, headers=headers, timeout=10)
        metadata["http_status"] = resp.status_code
        metadata["content_type"] = resp.headers.get("Content-Type", "")

        # Check HTTP status
        if resp.status_code in [403, 429, 503]:
            findings.append({
                "id": "F-CRAWL-WAF-CHALLENGE",
                "title": "AI crawler User-Agent blocked or challenged by WAF",
                "severity": "critical",
                "category": "discoverability",
                "evidence": f"GET {url} with GPTBot User-Agent returned HTTP {resp.status_code}. Likely blocked by Cloudflare/WAF bot management.",
                "suggested_action": {
                    "summary": "Create a WAF exception rule allowing verified AI search crawlers.",
                    "priority": "critical",
                    "details": "Configure CDN/WAF (Cloudflare, AWS WAF, Akamai) to permit verified AI bots based on their published reverse-DNS or IP ranges."
                }
            })
            return findings, metadata

        # Check X-Robots-Tag header
        x_robots = resp.headers.get("X-Robots-Tag", "").lower()
        if "noindex" in x_robots or "nosnippet" in x_robots:
            findings.append({
                "id": "F-CRAWL-HEADER-NOINDEX",
                "title": "X-Robots-Tag HTTP header disallows indexing or snippets",
                "severity": "critical",
                "category": "discoverability",
                "evidence": f"Server emitted 'X-Robots-Tag: {x_robots}', preventing citation generation.",
                "suggested_action": {
                    "summary": "Remove noindex / nosnippet directives from X-Robots-Tag on public pages.",
                    "priority": "critical",
                    "details": "Allow indexing and snippet extraction in response headers."
                }
            })

        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        # Check Meta Robots tag
        meta_robots = soup.find("meta", attrs={"name": re.compile(r"^(robots|googlebot|bingbot)$", re.I)})
        if meta_robots and meta_robots.get("content"):
            content = meta_robots.get("content", "").lower()
            if "noindex" in content:
                findings.append({
                    "id": "F-CRAWL-META-NOINDEX",
                    "title": "Meta robots tag instructs crawlers not to index",
                    "severity": "critical",
                    "category": "discoverability",
                    "evidence": f"Found meta tag: <meta name=\"robots\" content=\"{content}\">.",
                    "suggested_action": {
                        "summary": "Change meta robots content to 'index, follow'.",
                        "priority": "critical",
                        "code_example": '<meta name="robots" content="index, follow">'
                    }
                })
            elif "nosnippet" in content:
                findings.append({
                    "id": "F-CRAWL-META-NOSNIPPET",
                    "title": "Meta robots nosnippet prevents quote extraction",
                    "severity": "high",
                    "category": "discoverability",
                    "evidence": f"Found meta tag: <meta name=\"robots\" content=\"{content}\">. Prevents AI engines from citing text snippets.",
                    "suggested_action": {
                        "summary": "Remove 'nosnippet' from meta robots directive.",
                        "priority": "high"
                    }
                })

        # Check CSR vs SSR Render Parity
        scripts = soup.find_all("script")
        script_weight = sum(len(s.get_text()) for s in scripts) + sum(len(s.get("src", "")) for s in scripts)
        
        # Strip scripts and styles to measure static body text
        for tag in soup(["script", "style", "svg", "noscript"]):
            tag.decompose()

        body = soup.find("body")
        body_text = body.get_text(separator=" ", strip=True) if body else ""
        words = [w for w in body_text.split() if len(w) > 1]
        word_count = len(words)
        metadata["static_word_count"] = word_count

        # Check for typical SPA hydration shells: <div id="root"> or <div id="app"> with minimal text
        raw_soup = BeautifulSoup(html, "html.parser")
        spa_mount = raw_soup.find(["div", "main"], attrs={"id": re.compile(r"^(root|app|__next)$", re.I)})
        has_spa_mount = spa_mount is not None

        if word_count < 120 and (has_spa_mount or len(scripts) >= 2):
            findings.append({
                "id": "F-CRAWL-CSR-HYDRATION-WALL",
                "title": "Client-Side Rendering (CSR) Hydration Wall detected",
                "severity": "high",
                "category": "discoverability",
                "evidence": f"Initial raw HTML contains only {word_count} visible words and mounts a client SPA container ({spa_mount.name if spa_mount else 'container'}), but relies on {len(scripts)} scripts. AI crawlers fetching static HTML will see an empty page shell.",
                "suggested_action": {
                    "summary": "Implement Server-Side Rendering (SSR) or Static Site Generation (SSG) for core landing pages.",
                    "priority": "high",
                    "details": "AI retrieval crawlers (e.g. ChatGPT Search, PerplexityBot) execute lightweight HTTP GET requests without JavaScript engines. Pre-render product descriptions, headers, and core facts into static HTML.",
                    "code_example": "// In Next.js / Astro / Vite-SSR:\n// Export static page or use SSR instead of 'use client' exclusively:\nexport async function getStaticProps() { ... }"
                }
            })

    except requests.RequestException as ex:
        findings.append({
            "id": "F-CRAWL-FETCH-FAIL",
            "title": "Failed to retrieve target page",
            "severity": "critical",
            "category": "discoverability",
            "evidence": f"HTTP GET {url} failed: {str(ex)}",
            "suggested_action": {
                "summary": "Verify website DNS, SSL certificate, and server availability.",
                "priority": "critical"
            }
        })

    return findings, metadata


def audit_sitemap_endpoint(base_url: str, session: requests.Session) -> list:
    findings = []
    sitemap_url = urljoin(base_url, "/sitemap.xml")
    try:
        resp = session.get(sitemap_url, timeout=8)
        if resp.status_code != 200:
            findings.append({
                "id": "F-CRAWL-SITEMAP-MISSING",
                "title": "Sitemap endpoint /sitemap.xml returned non-200 status",
                "severity": "medium",
                "category": "discoverability",
                "evidence": f"GET {sitemap_url} returned HTTP {resp.status_code}.",
                "suggested_action": {
                    "summary": "Deploy an XML sitemap at /sitemap.xml listing all canonical URLs.",
                    "priority": "medium",
                    "details": "Ensure sitemap includes <loc>, <lastmod>, and priority directives."
                }
            })
        elif "xml" not in resp.headers.get("Content-Type", "").lower() and "<urlset" not in resp.text:
            findings.append({
                "id": "F-CRAWL-SITEMAP-INVALID",
                "title": "Sitemap /sitemap.xml is not valid XML",
                "severity": "medium",
                "category": "discoverability",
                "evidence": f"GET {sitemap_url} returned Content-Type '{resp.headers.get('Content-Type')}' without standard <urlset> tags.",
                "suggested_action": {
                    "summary": "Ensure /sitemap.xml emits standard sitemap XML schema.",
                    "priority": "medium"
                }
            })
    except requests.RequestException:
        pass
    return findings


def run_audit(target_url: str, session: requests.Session = None) -> dict:
    if not session:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; BrandAIAuditAgent/1.0; +https://agentskills.io)"})

    parsed = urlparse(target_url)
    if not parsed.scheme:
        target_url = f"https://{target_url}"
        parsed = urlparse(target_url)

    base_url = f"{parsed.scheme}://{parsed.netloc}"

    all_findings = []
    # 1. robots.txt
    all_findings.extend(audit_robots_txt(base_url, session))
    # 2. page render and headers
    page_findings, meta = audit_page_render_and_headers(target_url, session)
    all_findings.extend(page_findings)
    # 3. sitemap
    all_findings.extend(audit_sitemap_endpoint(base_url, session))

    return {
        "skill": "crawler-access-audit",
        "findings": all_findings,
        "metadata": meta
    }


def main():
    parser = argparse.ArgumentParser(description="Audit website crawlability, bot restrictions, and CSR render gaps.")
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
