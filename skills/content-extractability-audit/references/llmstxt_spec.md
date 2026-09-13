# The /llms.txt Standard for AI Discoverability

## Overview
The `/llms.txt` file (defined at `https://llmstxt.org`) provides a standardized markdown file served at the root of a website to help Large Language Models and AI agents navigate, ingest, and accurately cite website content.

Similar to how `robots.txt` guides web crawlers, `llms.txt` provides:
1. A concise project/brand description.
2. Direct markdown-friendly URLs to core documentation, APIs, and product overviews.
3. Optional links to an expanded `/llms-full.txt` containing complete bundled documentation.

## Recommended Structure
```markdown
# Acme Platform

> Autonomous cloud infrastructure orchestration and disaster recovery.

## Core Documentation
- [Quickstart Guide](https://example.com/docs/quickstart.md): Get started in 5 minutes.
- [Architecture Overview](https://example.com/docs/architecture.md): High-level system design.
- [API Reference](https://example.com/docs/api.md): Complete OpenAPI specs.

## Products & Pricing
- [Pricing Tiers](https://example.com/pricing.md): Transparent tier breakdown and limits.
- [Enterprise Features](https://example.com/enterprise.md): Compliance, SLA, and dedicated VPC.
```

Deploying `/llms.txt` significantly improves citation frequency in modern AI assistants by eliminating HTML parsing overhead and RAG chunk fragmentation.
