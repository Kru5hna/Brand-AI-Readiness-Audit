---
name: engagement-conversion-audit
description: Audit website on-site engagement readiness, above-the-fold value proposition clarity, deep-link context retention (breadcrumbs/orientation), intrusive friction overlays, and conversion CTA pathways for visitors arriving via AI citations.
license: MIT
---

# Engagement & Conversion Audit

## When to use
Use this skill to diagnose why visitors referred by AI assistants bounce immediately without reading or converting. It audits deep-landing orientation, contextual breadcrumbs, above-the-fold clarity, obstructive popup friction, and call-to-action discoverability.

## Inputs
- **`url`** *(string, required)*: The target website URL to audit.
- **`--html`** *(string, optional)*: Raw HTML string or file path for offline auditing.
- **`--output`** *(string, optional)*: Path to save findings JSON.

## Procedure
1. **Above-the-Fold Clarity Check**: Scan the hero or header region. Verify presence of a prominent title (`<h1>`) paired with a clear descriptive subhead or value proposition statement.
2. **Deep-Link Context & Breadcrumbs Audit**: For subpages and deep links, inspect for contextual grounding elements: breadcrumb trails (`<nav aria-label="breadcrumb">`, `.breadcrumbs`), parent hierarchy links, and persistent global branding.
3. **Friction & Interruption Detection**: Detect intrusive modal dialogs (`role="dialog"`, modal classes, full-screen overlay backdrops) that trigger on arrival.
4. **Call-to-Action (CTA) Audit**: Scan for primary and secondary action elements (`<a>` or `<button>` styled as CTAs). Check action verb clarity and verify that arriving visitors have a clear next step.

## Output
Returns a structured JSON payload containing:
- `findings`: Array of engagement and conversion defects with `id`, `title`, `severity`, `evidence`, and `suggested_action`.
- `metadata`: Detected CTAs, breadcrumb status, hero element presence, and modal indicators.

Evaluation heuristics and checklists are documented in [engagement_rubric.md](file:///k:/adobe/skills/engagement-conversion-audit/references/engagement_rubric.md) and [orientation_checklist.md](file:///k:/adobe/skills/engagement-conversion-audit/references/orientation_checklist.md).
