# Audit Orchestrator: Composition & Execution Flow

This reference describes how `audit-orchestrator` coordinates the specialized skills in the marketplace.

## Orchestration Pipeline

```mermaid
graph TD
    A[Input: Target URL/Domain] --> B[Phase 1: Page Discovery & Sampling]
    B --> C1[Skill: crawler-access-audit]
    B --> C2[Skill: structured-data-entity-audit]
    B --> C3[Skill: content-extractability-audit]
    B --> C4[Skill: engagement-conversion-audit]
    
    C1 --> D[Phase 3: Aggregator & Deduplicator]
    C2 --> D
    C3 --> D
    C4 --> D
    
    D --> E[Phase 4: Severity & Priority Synthesizer]
    E --> F[Phase 5: Proactive Recommendations Generator]
    F --> G[Phase 6: Schema Validation & Output]
    G --> H[Final Report: JSON & Markdown]
```

## Composition Rules

1. **Sub-Skill Execution Contract**:
   - Each specialized skill is completely self-contained. It can be invoked as an independent CLI tool or via Python module import.
   - Each skill returns findings adhering to the sub-finding interface:
     - `id`: unique identifier (e.g. `F-CRAWL-001`, `F-DATA-002`, `F-CONT-001`, `F-ENG-001`)
     - `title`: human-readable description of defect
     - `severity`: `"critical"`, `"high"`, `"medium"`, or `"low"`
     - `category`: `"discoverability"` or `"engagement"`
     - `evidence`: factual proof observed during crawl
     - `suggested_action`: `{ "summary": "...", "priority": "...", "details": "...", "code_example": "..." }`

2. **Deduplication & Severity Sorting**:
   - Findings are grouped by ID or target page.
   - Summaries count `critical`, `high`, and `medium` findings.
   - Findings are sorted by severity descending (`critical` > `high` > `medium` > `low`).

3. **Resilience & Guardrails**:
   - Timeouts enforced per request (default: 8.0s).
   - Entire audit execution completes in < 5 minutes.
   - All network calls are strictly read-only (HTTP GET/HEAD).
   - User-Agent identifying as `Mozilla/5.0 (compatible; BrandAIAuditAgent/1.0; +https://agentskills.io)`.
   - Never attempts authentication, form submissions, or modifying operations.
