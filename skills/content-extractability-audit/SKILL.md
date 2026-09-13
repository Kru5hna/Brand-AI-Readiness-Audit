---
name: content-extractability-audit
description: Audit website content quotability for AI search engines, RAG chunking friendliness, information density vs boilerplate ratio, freshness signals, and support for the /llms.txt standard.
license: MIT
---

# Content Extractability & Freshness Audit

## When to use
Use this skill to diagnose why AI assistants fail to cite clear quotes or facts from a website, why AI summarizers drop key points, or why a site appears stale or unmaintained to conversational search models.

## Inputs
- **`url`** *(string, required)*: The target website URL or domain.
- **`--html`** *(string, optional)*: Raw HTML string or file path for offline auditing.
- **`--output`** *(string, optional)*: Path to save findings JSON.

## Procedure
1. **Definitive Quotability Check**: Parse opening text (first 250 words). Evaluate presence of concise, declarative definition statements ("X is a...", "X provides...", "We build..."). Detect vague buzzword-only rhetoric.
2. **Information Density & Clutter Ratio**: Calculate substantive text length versus peripheral boilerplate (navigation links, footer disclaimers, cookie banners). Flag pages where clutter suppresses content extraction.
3. **Temporal Freshness & Copyright Audit**: Extract copyright notices, meta publication dates (`article:published_time`, `article:modified_time`), and detect outdated temporal markers (e.g. copyright <= 2024 during a 2026 audit).
4. **AI Context Standard (`llms.txt`) Check**: Check whether the root hosts an accessible, valid `/llms.txt` or `/llms-full.txt` file for LLM scrapers.

## Output
Returns a structured JSON payload containing:
- `findings`: Array of extractability, density, and freshness defects with `id`, `title`, `severity`, `evidence`, and `suggested_action`.
- `metadata`: Word counts, density percentages, detected dates, and `llms.txt` status.

Detailed guidance is documented in [llmstxt_spec.md](file:///k:/adobe/skills/content-extractability-audit/references/llmstxt_spec.md) and [quotability_guide.md](file:///k:/adobe/skills/content-extractability-audit/references/quotability_guide.md).
