# Implementation Specification & Architecture: Brand AI-Readiness Audit Skill Marketplace

This document details the technical implementation, architectural design, schema compliance, and verification results for the **Brand AI-Readiness Audit Skill Marketplace** developed for the **Adobe University Hackathon 2026 (Round 3)**.

---

## 1. System Overview & Objectives

General AI assistants (ChatGPT Search, Claude Search, Perplexity AI, Google Gemini) increasingly act as the primary discovery engine for brands, products, and services. When an AI assistant answers user queries, it relies on real-time web retrieval, crawling, and quote extraction. If a website fails to provide machine-readable, corroborated, and cleanly indexed information, the brand becomes effectively invisible or misrepresented. Furthermore, when users click through AI citations to visit the site, poor contextual orientation and intrusive friction cause immediate bounce.

The objective of this marketplace is to provide an autonomous, modular suite of agent skills that can:
1. **Audit any target website URL/domain** safely (< 5 minutes runtime, read-only, non-destructive, rate-safe).
2. **Detect concrete failure modes** across both **AI Discoverability** (off-site) and **On-Site Engagement** (on-site).
3. **Provide evidence-backed findings** with exact severity levels (`critical`, `high`, `medium`).
4. **Emit mechanism-sound, prioritized suggested actions**, including proactive recommendations (such as `llms.txt`, entity grounding, and inverted-pyramid content structures).
5. **Comply strictly with the `agentskills.io` standard** and the contest's required report schema.

---

## 2. Marketplace Manifest & Directory Layout

### 2.1 Manifest (`marketplace.json`)
The root contains `marketplace.json` defining the marketplace metadata, the list of skills, and designating `audit-orchestrator` as the sole entrypoint:

```json
{
  "name": "brand-ai-readiness-audit",
  "version": "1.0.0",
  "description": "Agent Skill Marketplace for auditing website AI-discoverability and on-site engagement readiness",
  "skills": [
    {
      "id": "audit-orchestrator",
      "path": "skills/audit-orchestrator",
      "entrypoint": true
    },
    {
      "id": "crawler-access-audit",
      "path": "skills/crawler-access-audit"
    },
    {
      "id": "structured-data-entity-audit",
      "path": "skills/structured-data-entity-audit"
    },
    {
      "id": "content-extractability-audit",
      "path": "skills/content-extractability-audit"
    },
    {
      "id": "engagement-conversion-audit",
      "path": "skills/engagement-conversion-audit"
    }
  ]
}
```

---

## 3. Detailed Skill Decomposition (Separation of Concerns)

Each skill represents a discrete, focused domain of concern, containing:
- `SKILL.md`: Standard YAML frontmatter, `When to use`, `Inputs`, `Procedure`, and `Output`.
- `scripts/`: Deterministic, self-contained Python CLI execution scripts.
- `references/`: Detailed checklists, schemas, and rule definitions (progressive disclosure).

### 3.1 `skills/audit-orchestrator` (Entrypoint)
- **Primary Concern**: Marketplace composition, page discovery, multi-skill orchestration, deduplication, severity scoring, and standardized reporting.
- **Workflow**:
  1. Accepts target URL/domain via CLI flag `--url`.
  2. Resolves domain, inspects sitemap/nav links to sample representative pages (homepage + deep pages like `/products`, `/docs`, `/pricing`, `/about`).
  3. Executes domain audits via the specialized audit engines.
  4. Merges findings, validates schema integrity, and writes the final JSON report.
- **Outputs**: Conforms 100% to the contest JSON schema.

### 3.2 `skills/crawler-access-audit`
- **Primary Concern**: Machine accessibility, bot authorization, and rendering barriers.
- **Checks Encoded**:
  - `F-CRAWL-AI-BOTS-BLOCKED`: Checks if `robots.txt` disallows AI User-Agents (`GPTBot`, `ClaudeBot`, `PerplexityBot`, `CCBot`, `Google-Extended`, `Bytespider`, `cohere-ai`, `Amazonbot`).
  - `F-CRAWL-UNIVERSAL-DISALLOW`: Checks if `User-agent: * Disallow: /` blocks all crawlers.
  - `F-CRAWL-ASSETS-BLOCKED`: Checks if critical asset paths (CSS, JS, API data feeds) are disallowed.
  - `F-CRAWL-META-NOINDEX` / `F-CRAWL-META-NOSNIPPET`: Inspects `<meta name="robots">` and `X-Robots-Tag` headers for `noindex`, `nosnippet`, or `noarchive`.
  - `F-CRAWL-CSR-HYDRATION-WALL`: Evaluates Client-Side Rendering vs Static SSR content parity. Detects empty `<div id="root"></div>` or `<div id="__next">` shells with high script density and near-zero raw text.
  - `F-CRAWL-SITEMAP-MISSING`: Verifies presence and valid XML structure of `sitemap.xml` and declaration in `robots.txt`.

### 3.3 `skills/structured-data-entity-audit`
- **Primary Concern**: Machine comprehension, schema graph markup, entity identity, and non-text facts.
- **Checks Encoded**:
  - `F-DATA-MISSING-ORG-SCHEMA`: Missing `Organization` or `WebSite` JSON-LD schema on key pages.
  - `F-DATA-MISSING-PRODUCT-SCHEMA`: Missing `Product`, `SoftwareApplication`, or `Service` JSON-LD on product/offering pages.
  - `F-DATA-ENTITY-SAMEAS-ABSENT`: Absence of `sameAs` entity links grounding the brand in authoritative knowledge graph hubs (Wikidata, Wikipedia, LinkedIn, Crunchbase).
  - `F-DATA-NONTEXT-ALT-MISSING`: Key informative images, charts, and diagrams missing descriptive `alt` text.
  - `F-DATA-CANVAS-LOCKED-CONTENT`: Tables or specifications rendered purely as images or canvas elements without accessible HTML table counterparts.
  - `F-DATA-HEADING-NO-H1` / `F-DATA-HEADING-MULTIPLE-H1`: Broken heading hierarchy (missing or multiple `<h1>`, skipped levels).

### 3.4 `skills/content-extractability-audit`
- **Primary Concern**: RAG quotability, information density, freshness, and AI protocol standards.
- **Checks Encoded**:
  - `F-CONT-LOW-QUOTABILITY`: Absence of crisp, declarative definition sentences ("X is a...", "We offer...") in the opening 250 words.
  - `F-CONT-LOW-DENSITY`: High boilerplate/fluff-to-substance ratio that causes RAG chunk extractors and summarizers to discard page content.
  - `F-CONT-STALE-COPYRIGHT`: Outdated copyright years (e.g. `<= 2024` on a 2026 audit), outdated revision dates, or unmaintained status indicators.
  - `F-CONT-LLMSTXT-MISSING`: Proactive detection for missing `/llms.txt` and `/llms-full.txt` files (the emerging markdown context standard for LLMs).

### 3.5 `skills/engagement-conversion-audit`
- **Primary Concern**: On-site visitor orientation, deep-link context retention, interaction friction, and conversion pathways.
- **Checks Encoded**:
  - `F-ENG-HERO-UNCLEAR`: Lack of unambiguous above-the-fold value proposition (hero headline and explanatory subhead).
  - `F-ENG-DEEP-NO-BREADCRUMBS`: Deep landing pages lacking breadcrumb navigation (`nav[aria-label="breadcrumb"]`) or parent brand grounding for users arriving from AI citation links.
  - `F-ENG-INTRUSIVE-OVERLAYS`: Obtrusive full-screen modal overlays, popups, or gating prompts that obscure content upon arrival.
  - `F-ENG-MISSING-CTA`: Lack of clear, visible primary and secondary calls to action guiding the user to next steps.

---

## 4. Required Audit Report Schema

The output conforms strictly to the contest specification:

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

---

## 5. Implementation Diff Tracker & Verification Log

| Step # | File / Component | Purpose | Status | Validation Result |
|---|---|---|:---:|---|
| **Step 1** | `marketplace.json` | Top-level marketplace manifest with 5 skills | ✅ Completed | Well-formed JSON with single entrypoint |
| **Step 2** | `skills/audit-orchestrator/*` | Entrypoint skill spec, orchestrator script, reporter, schema | ✅ Completed | `skills-ref validate` passed; standalone test passed |
| **Step 3** | `skills/crawler-access-audit/*` | Crawl & render audit skill, script, AI bots reference, heuristics | ✅ Completed | `skills-ref validate` passed; standalone test passed |
| **Step 4** | `skills/structured-data-entity-audit/*` | Structured data & entity audit skill, script, schema templates | ✅ Completed | `skills-ref validate` passed; standalone test passed |
| **Step 5** | `skills/content-extractability-audit/*` | Content extractability & freshness skill, script, llms.txt guide | ✅ Completed | `skills-ref validate` passed; standalone test passed |
| **Step 6** | `skills/engagement-conversion-audit/*` | Engagement & conversion audit skill, script, UX heuristics | ✅ Completed | `skills-ref validate` passed; standalone test passed |
| **Step 7** | `tests/test_marketplace.py` | Automated end-to-end integration test with mock servers | ✅ Completed | 6/6 unit & integration tests passing in 0.8s |
| **Step 8** | `npx skills-ref validate` | Specification compliance of all 5 skill directories | ✅ Completed | 5/5 skills reported `Valid skill` |
| **Step 9** | `brand-ai-readiness-audit.zip` | Package submission zip archive | ✅ Completed | Generated zip archive (< 50MB) |
