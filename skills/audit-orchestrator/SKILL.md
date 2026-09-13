---
name: audit-orchestrator
description: Coordinate and execute comprehensive AI-discoverability and on-site engagement audits for any target website. Discovers pages, composes sub-skills (crawler access, structured data, content extractability, engagement), aggregates findings, and produces a standardized audit report with prioritized fixes.
license: MIT
---

# Audit Orchestrator (Brand AI-Readiness & Engagement Audit)

## When to use
Use this skill when auditing any public website to evaluate its readiness for AI assistants (ChatGPT, Claude, Perplexity, Gemini) and diagnose why visitors landing from AI citations fail to engage or convert. This skill acts as the master entrypoint for the `brand-ai-readiness-audit` marketplace.

## Inputs
- **`url`** *(string, required)*: The target website URL or domain (e.g. `https://example.com` or `example.com`).
- **`--max-pages`** *(integer, optional, default: 5)*: Maximum representative pages to crawl and sample.
- **`--output`** *(string, optional, default: stdout)*: File path to save the final audit JSON report.
- **`--format`** *(string, optional, values: `json`, `markdown`, `both`, default: `json`)*: Output format.

## Procedure
1. **Target Normalization**: Validate the input URL, ensure scheme (`https://`), and resolve the primary hostname.
2. **Page Discovery**: Fetch the root page, inspect `robots.txt` and `sitemap.xml`, and select representative deep links (such as `/products`, `/docs`, `/pricing`, `/about`, `/blog`).
3. **Dispatch Sub-Skills**:
   - Invoke `crawler-access-audit` to evaluate machine accessibility, AI crawler blocking (`GPTBot`, `ClaudeBot`, etc.), HTTP headers, and CSR vs SSR render gaps.
   - Invoke `structured-data-entity-audit` to inspect Schema.org JSON-LD / Microdata, entity grounding (`sameAs`), heading hierarchies, and non-text trapped content.
   - Invoke `content-extractability-audit` to evaluate answer quotability, information density, freshness signals, and `/llms.txt`.
   - Invoke `engagement-conversion-audit` to assess deep-link landing context, breadcrumbs, above-the-fold value proposition, and modal friction.
4. **Aggregate & Deduplicate**: Collect findings across all sub-skills, normalize identifiers, and calculate severity metrics (`critical`, `high`, `medium`, `low`).
5. **Generate Suggested Actions & Proactive Fixes**: Assign actionable remediations with code snippets and mechanism-sound priorities.
6. **Schema Validation & Emission**: Ensure the resulting report conforms strictly to the contest report schema (`site`, `audited_at`, `summary`, `findings`), and emit the report.

## Output
Emits a validated JSON report adhering to the required schema:

```json
{
  "site": "example.com",
  "audited_at": "2026-09-20T14:32:00Z",
  "summary": {
    "total_findings": 6,
    "critical": 1,
    "high": 2,
    "medium": 3
  },
  "findings": [
    {
      "id": "F-001",
      "title": "No JSON-LD structured data on product pages",
      "severity": "high",
      "evidence": "Crawled 12 product pages; 0/12 contain schema.org markup.",
      "suggested_action": {
        "summary": "Add Product/Offer JSON-LD to every product page.",
        "priority": "high"
      }
    }
  ]
}
```

Detailed schema and guidelines are available in [report_schema.json](file:///k:/adobe/skills/audit-orchestrator/references/report_schema.json) and [composition_flow.md](file:///k:/adobe/skills/audit-orchestrator/references/composition_flow.md).
