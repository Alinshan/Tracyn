import csv
import io
import json
from datetime import datetime
from typing import Dict, List, Optional

from ..database.database import get_session
from ..database.repositories import Repository


def generate_report(fmt: str = "json", period_hours: int = 24) -> Dict:
    """Generate a security report. fmt: 'json' | 'csv' | 'html'"""
    session = get_session()
    repo = Repository(session)
    stats = repo.get_summary_stats()
    events = repo.get_all_events(limit=500)
    incidents = session.query(__import__("tracyn.database.models", fromlist=["IncidentRecord"]).IncidentRecord).order_by(
        __import__("tracyn.database.models", fromlist=["IncidentRecord"]).IncidentRecord.created_at.desc()
    ).all()

    report_id = f"RPT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    generated_at = datetime.utcnow().isoformat() + "Z"

    top_risk_events = sorted(events, key=lambda e: e.risk_score, reverse=True)[:10]

    open_incidents = sum(1 for i in incidents if i.status in ["NEW", "INVESTIGATING", "ACKNOWLEDGED"])
    resolved_incidents = sum(1 for i in incidents if i.status in ["RESOLVED", "FALSE_POSITIVE"])

    report_data = {
        "report_id": report_id,
        "generated_at": generated_at,
        "monitoring_period_hours": period_hours,
        "summary": stats,
        "open_incidents": open_incidents,
        "resolved_incidents": resolved_incidents,
        "top_risk_events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "path": e.path,
                "severity": e.severity,
                "risk_score": e.risk_score,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "reason": e.reason,
            }
            for e in top_risk_events
        ],
    }

    session.close()

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Report ID", "Generated At", "Total Events", "Modified", "New", "Deleted", "Open Incidents"])
        writer.writerow([
            report_id, generated_at,
            stats["total_events"], stats["modified_files"],
            stats["new_files"], stats["deleted_files"],
            open_incidents
        ])
        writer.writerow([])
        writer.writerow(["Event ID", "Type", "Path", "Severity", "Risk Score", "Timestamp"])
        for e in top_risk_events:
            writer.writerow([
                e.event_id, e.event_type, e.path,
                e.severity, e.risk_score,
                e.timestamp.isoformat() if e.timestamp else ""
            ])
        return {"format": "csv", "content": output.getvalue(), "report_id": report_id}

    elif fmt == "html":
        rows = "".join(
            f"<tr><td>{e.event_id}</td><td>{e.event_type}</td><td>{e.path}</td>"
            f"<td><span class='badge {e.severity.lower()}'>{e.severity}</span></td>"
            f"<td>{e.risk_score}</td><td>{e.timestamp}</td></tr>"
            for e in top_risk_events
        )
        html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>TRACYN Security Report</title>
<style>
body{{font-family:monospace;background:#0a0e1a;color:#e2e8f0;padding:2rem}}
h1{{color:#00ff88}}table{{width:100%;border-collapse:collapse;margin-top:1rem}}
th{{background:#1a2035;color:#94a3b8;padding:0.5rem 1rem;text-align:left}}
td{{padding:0.5rem 1rem;border-bottom:1px solid #1e293b}}
.badge{{padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:bold}}
.critical{{background:#7f1d1d;color:#fca5a5}}.high{{background:#78350f;color:#fcd34d}}
.medium{{background:#1e3a5f;color:#93c5fd}}.low{{background:#14532d;color:#86efac}}
</style></head>
<body>
<h1>TRACYN — Security Report</h1>
<p>Report ID: {report_id} | Generated: {generated_at}</p>
<table><tr><th>Files Monitored</th><th>Modified</th><th>New</th><th>Deleted</th><th>Open Incidents</th><th>Resolved</th></tr>
<tr><td>{stats["total_files"]}</td><td>{stats["modified_files"]}</td><td>{stats["new_files"]}</td>
<td>{stats["deleted_files"]}</td><td>{open_incidents}</td><td>{resolved_incidents}</td></tr></table>
<h2>Top Risk Events</h2>
<table><tr><th>Event ID</th><th>Type</th><th>Path</th><th>Severity</th><th>Risk</th><th>Timestamp</th></tr>
{rows}</table></body></html>"""
        return {"format": "html", "content": html, "report_id": report_id}

    else:
        return {"format": "json", "content": json.dumps(report_data, indent=2), "data": report_data, "report_id": report_id}
