---
name: structured-data-entity-audit
description: Audit website structured data (JSON-LD / Microdata), schema.org completeness, entity disambiguation via sameAs knowledge graph links, semantic HTML heading hierarchy, and facts trapped in non-text images.
license: MIT
---

# Structured Data & Entity Audit

## When to use
Use this skill when diagnosing why AI assistants fail to extract structured facts about a brand (e.g. products, pricing, features, founders) or confuse the brand with other entities. It audits Schema.org markup, authoritative entity links, heading structure, and facts trapped in non-text images.

## Inputs
- **`url`** *(string, required)*: The target website URL to audit.
- **`--html`** *(string, optional)*: Raw HTML string or file path for offline auditing.
- **`--output`** *(string, optional)*: Path to save the findings JSON.

## Procedure
1. **Schema.org JSON-LD Extraction**: Extract all `<script type="application/ld+json">` elements and microdata (`itemscope`, `itemtype`). Parse and validate JSON syntax.
2. **Entity & Organization Validation**: Verify whether `Organization` or `WebSite` schemas are declared. Check for required properties: `name`, `url`, `description`, `logo`.
3. **Entity Disambiguation & `sameAs` Check**: Check whether schema includes authoritative `sameAs` links to Wikidata, Wikipedia, LinkedIn, or Crunchbase.
4. **Product / Offering Schema Check**: On product, pricing, or service pages, check for `Product`, `SoftwareApplication`, or `Offer` schemas with pricing and availability.
5. **Non-Text Lock Detection**: Scan all `<img>` elements. Detect missing `alt` attributes, empty `alt=""`, or non-descriptive filler ("image", "banner"). Inspect for data tables trapped in images or canvas.
6. **Semantic Heading Hierarchy Check**: Audit `<h1>` through `<h6>` tags. Flag missing `<h1>`, multiple competing `<h1>` tags, or skipped heading levels.

## Output
Returns a structured JSON payload containing:
- `findings`: Array of structured data and entity defects with `id`, `title`, `severity`, `evidence`, and `suggested_action`.
- `metadata`: Count of schema blocks, detected types, image statistics, and heading tree.

Templates and rules are detailed in [schema_templates.md](file:///k:/adobe/skills/structured-data-entity-audit/references/schema_templates.md) and [entity_rules.md](file:///k:/adobe/skills/structured-data-entity-audit/references/entity_rules.md).
