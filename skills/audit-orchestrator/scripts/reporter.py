"""
Audit Report Generator and Validator
Ensures 100% conformance with the hackathon audit report schema.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List

SEVERITY_WEIGHTS = {
    "critical": 25,
    "high": 15,
    "medium": 8,
    "low": 3,
    "info": 0
}

SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4
}


def build_audit_report(
    site: str,
    findings: List[Dict[str, Any]],
    proactive_recommendations: List[Dict[str, Any]] = None,
    audited_at: str = None
) -> Dict[str, Any]:
    """
    Constructs and validates the standard audit report structure.
    Guarantees the required fields:
    - site (string)
    - audited_at (ISO 8601 string)
    - summary: { total_findings, critical, high, medium, ... }
    - findings: [ { id, title, severity, evidence, suggested_action: { summary, priority } } ]
    """
    if audited_at is None:
        audited_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Sort findings by severity order
    sorted_findings = sorted(
        findings,
        key=lambda f: SEVERITY_ORDER.get(str(f.get("severity", "medium")).lower(), 99)
    )

    # Calculate summary counts
    critical_count = sum(1 for f in sorted_findings if str(f.get("severity", "")).lower() == "critical")
    high_count = sum(1 for f in sorted_findings if str(f.get("severity", "")).lower() == "high")
    medium_count = sum(1 for f in sorted_findings if str(f.get("severity", "")).lower() == "medium")
    low_count = sum(1 for f in sorted_findings if str(f.get("severity", "")).lower() == "low")
    total_findings = len(sorted_findings)

    # Compute discoverability & engagement category scores (100 baseline, deducted by severity)
    disc_penalty = sum(
        SEVERITY_WEIGHTS.get(str(f.get("severity", "")).lower(), 5)
        for f in sorted_findings
        if f.get("category", "discoverability") == "discoverability"
    )
    eng_penalty = sum(
        SEVERITY_WEIGHTS.get(str(f.get("severity", "")).lower(), 5)
        for f in sorted_findings
        if f.get("category", "") == "engagement"
    )

    discoverability_score = max(0, 100 - disc_penalty)
    engagement_score = max(0, 100 - eng_penalty)

    # Clean and standardize findings
    cleaned_findings = []
    for idx, f in enumerate(sorted_findings, start=1):
        finding_id = f.get("id") or f"F-{idx:03d}"
        title = f.get("title", "Detected AI Readiness Defect")
        severity = str(f.get("severity", "medium")).lower()
        if severity not in SEVERITY_ORDER:
            severity = "medium"

        evidence = str(f.get("evidence", "Observable defect detected during crawl."))

        suggested_action = f.get("suggested_action", {})
        if not isinstance(suggested_action, dict):
            suggested_action = {"summary": str(suggested_action), "priority": severity}
        
        if "summary" not in suggested_action:
            suggested_action["summary"] = f"Remediate {title.lower()}."
        if "priority" not in suggested_action:
            suggested_action["priority"] = severity

        finding_entry = {
            "id": finding_id,
            "title": title,
            "severity": severity,
            "category": f.get("category", "discoverability"),
            "evidence": evidence,
            "suggested_action": suggested_action
        }
        cleaned_findings.append(finding_entry)

    report = {
        "site": site,
        "audited_at": audited_at,
        "summary": {
            "total_findings": total_findings,
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "discoverability_score": discoverability_score,
            "engagement_score": engagement_score
        },
        "findings": cleaned_findings
    }

    if proactive_recommendations:
        report["proactive_recommendations"] = proactive_recommendations

    return report


def validate_report_schema(report: Dict[str, Any]) -> List[str]:
    """
    Validates report dictionary against the contest minimum required schema.
    Returns a list of error strings (empty if valid).
    """
    errors = []
    required_top = ["site", "audited_at", "summary", "findings"]
    for field in required_top:
        if field not in report:
            errors.append(f"Missing required top-level field: '{field}'")

    if "summary" in report:
        summary = report["summary"]
        if not isinstance(summary, dict):
            errors.append("'summary' must be an object")
        else:
            for s_field in ["total_findings", "critical", "high", "medium"]:
                if s_field not in summary:
                    errors.append(f"Missing required summary field: '{s_field}'")
                elif not isinstance(summary[s_field], int):
                    errors.append(f"Summary field '{s_field}' must be an integer")

    if "findings" in report:
        findings = report["findings"]
        if not isinstance(findings, list):
            errors.append("'findings' must be a list")
        else:
            for i, f in enumerate(findings):
                if not isinstance(f, dict):
                    errors.append(f"Finding #{i} is not an object")
                    continue
                for req in ["id", "title", "severity", "evidence", "suggested_action"]:
                    if req not in f:
                        errors.append(f"Finding #{i} missing required field: '{req}'")
                if "suggested_action" in f:
                    action = f["suggested_action"]
                    if not isinstance(action, dict):
                        errors.append(f"Finding #{i} 'suggested_action' must be an object")
                    else:
                        if "summary" not in action:
                            errors.append(f"Finding #{i} suggested_action missing 'summary'")
                        if "priority" not in action:
                            errors.append(f"Finding #{i} suggested_action missing 'priority'")

    return errors


def render_markdown_report(report: Dict[str, Any]) -> str:
    """
    Renders human-readable markdown summary for dashboards and CLI display.
    """
    lines = [
        f"# AI Readiness & Engagement Audit Report: {report.get('site')}",
        f"**Audited At:** {report.get('audited_at')}",
        "",
        "## Summary",
        f"- **Total Findings:** {report['summary']['total_findings']}",
        f"- **Critical:** {report['summary']['critical']}",
        f"- **High:** {report['summary']['high']}",
        f"- **Medium:** {report['summary']['medium']}",
        f"- **Discoverability Score:** {report['summary'].get('discoverability_score', 'N/A')}/100",
        f"- **Engagement Score:** {report['summary'].get('engagement_score', 'N/A')}/100",
        "",
        "## Detailed Findings",
        ""
    ]

    for f in report.get("findings", []):
        lines.append(f"### [{f.get('id')}] {f.get('title')} ({f.get('severity', '').upper()})")
        lines.append(f"- **Category:** {f.get('category')}")
        lines.append(f"- **Evidence:** {f.get('evidence')}")
        action = f.get("suggested_action", {})
        lines.append(f"- **Suggested Action (Priority: {action.get('priority')}):** {action.get('summary')}")
        if action.get("details"):
            lines.append(f"  - *Details:* {action.get('details')}")
        if action.get("code_example"):
            lines.append(f"  - *Example:*")
            lines.append("```")
            lines.append(action.get("code_example").strip())
            lines.append("```")
        lines.append("")

    if "proactive_recommendations" in report:
        lines.append("## Proactive Beyond-Problem Recommendations")
        lines.append("")
        for p in report["proactive_recommendations"]:
            lines.append(f"- **{p.get('title')}** [Impact: {p.get('impact')}]: {p.get('recommendation')}")
        lines.append("")

    return "\n".join(lines)
