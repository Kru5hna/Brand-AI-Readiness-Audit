---
name: crawler-access-audit
description: Audit website crawlability, AI crawler access permissions in robots.txt, HTTP headers, meta robots directives, and Client-Side Rendering (CSR) hydration gaps that prevent AI assistants from indexing or citing page content.
license: MIT
---

# Crawler Access & Render Audit

## When to use
Use this skill to diagnose why a website is completely invisible or ignored by AI retrieval bots (such as OpenAI GPTBot, ClaudeBot, PerplexityBot, and Google-Extended). It pinpoints crawl blocks, WAF challenges, noindex tags, and client-side JavaScript rendering walls where raw HTML lacks text substance.

## Inputs
- **`url`** *(string, required)*: The target website URL or domain.
- **`--timeout`** *(integer, optional, default: 8)*: HTTP request timeout in seconds.
- **`--output`** *(string, optional)*: Path to save the findings JSON.

## Procedure
1. **Robots.txt Analysis**: Fetch `robots.txt` from the origin. Parse User-Agent sections for AI crawlers (`GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, `CCBot`, `Google-Extended`, `Bytespider`). Verify whether `Disallow: /` or wildcard disallows block AI assistants.
2. **Critical Assets Check**: Check whether assets required for layout and styling (`/_next/`, `/static/`, `/assets/`) are erroneously blocked in `robots.txt`.
3. **HTTP Header & Bot Shield Inspection**: Perform an HTTP GET with an AI crawler user-agent header. Detect Cloudflare/WAF 403/429/503 bot challenges, CAPTCHAs, or `X-Robots-Tag: noindex`.
4. **Meta Robots Inspection**: Parse HTML `<meta name="robots">` tags for `noindex`, `nosnippet`, or `noarchive`.
5. **CSR vs SSR Render Gap Evaluation**: Inspect raw HTML payload for client-side hydration walls (`<div id="root">`, `<div id="app">`) with low substantive text count (< 150 words) dominated by JavaScript bundles.
6. **Sitemap Verification**: Test `/sitemap.xml` presence, format, and declaration within `robots.txt`.

## Output
Returns a structured JSON payload containing:
- `findings`: Array of detected crawl and render defects with `id`, `title`, `severity`, `evidence`, and `suggested_action`.
- `metadata`: Raw observations (robots rules, response status, render stats).

Reference details are found in [crawler_agents.json](file:///k:/adobe/skills/crawler-access-audit/references/crawler_agents.json) and [render_heuristics.md](file:///k:/adobe/skills/crawler-access-audit/references/render_heuristics.md).
