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



