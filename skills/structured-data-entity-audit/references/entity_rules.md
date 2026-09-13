# Entity Disambiguation & Knowledge Graph Grounding Rules

## Why Entity Ambiguity Causes AI Hallucination & Invisibility
Modern conversational AI assistants (such as ChatGPT, Claude, and Gemini) resolve brands through internal knowledge graphs and web grounding. When multiple organizations share a similar or common name, or when a brand's web presence does not link to definitive registry nodes:
1. The assistant may confuse the brand with an unrelated namesake.
2. The assistant lacks confidence in the fact consistency and defaults to omitting the brand from comparative answers.
3. Citations may link to an ambiguous disambiguation page rather than the brand's primary product.

## Rules for Entity Authority
1. **Unambiguous Primary Naming**:
   - The brand name in `<title>`, `<h1>`, and schema `Organization.name` must match exactly.
2. **Knowledge Graph `sameAs` Links**:
   - `sameAs` must reference high-authority external identifiers:
     - Wikidata (`wikidata.org/wiki/...`)
     - Wikipedia (`wikipedia.org/wiki/...`)
     - LinkedIn (`linkedin.com/company/...`)
     - Crunchbase (`crunchbase.com/organization/...`)
     - GitHub (`github.com/...`) for developer tools
3. **Non-Text Lock Elimination**:
   - Brand logos, charts, pricing grids, and architectural diagrams must provide machine-readable textual representation in `alt` attributes or adjacent structured tables.
