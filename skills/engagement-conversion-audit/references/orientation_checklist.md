# Deep-Link Orientation & Context Retention Checklist

## Why Deep-Link Context Retention Matters
When an AI engine cites a site, 85%+ of referral traffic bypasses the homepage entirely. Without deliberate orientation architecture:
- Visitors do not know what overarching product or company hosts the feature.
- Visitors cannot navigate to related documentation, pricing, or the company overview.
- Conversion rates drop by up to 70% compared to homepage entries.

## Architectural Requirements
1. **Semantic Breadcrumb Navigation**:
   - Must use `<nav aria-label="breadcrumb">` with an ordered list `<ol>` containing clickable hierarchy links.
   - Example: `Home > Solutions > Cloud Security > Automated Audits`.
2. **Persistent Global Brand Header**:
   - Visible brand logo and root link on all viewports.
3. **Targeted Reading Continuity**:
   - Deep-linked headings must anchor directly to the user's cited query without requiring endless scrolling.
4. **Friction-Free Entry**:
   - Do not display modal opt-ins, newsletter overlays, or push notification prompts within the first 10 seconds of a referral visit.
