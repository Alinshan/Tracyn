import asyncio
import json
import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse

from .schemas import (
    BaselineOut,
    DashboardSummary,
    EventOut,
    FileOut,
    IncidentOut,
    IncidentStatusUpdate,
)
from ..database.database import get_session
from ..database.repositories import Repository
from ..database.models import BaselineRecord, IncidentRecord
from ..core.baseline import create_baseline
from ..core.scanner import run_scan
from ..core import monitor as monitor_mod
from ..reports.generator import generate_report
from ..demo import (
    reset_demo,
    scenario_normal_change,
    scenario_sensitive_config_change,
    scenario_new_executable,
    scenario_critical_deletion,
    scenario_burst_attack,
)
from ..security.incident import IncidentManager

logger = logging.getLogger("tracyn")

router = APIRouter()

# Shared config reference (set by app startup)
_config = {}
_sse_clients: List[asyncio.Queue] = []


def set_config(cfg: dict):
    global _config
    _config = cfg


def _push_sse(event_dict: dict):
    """Push an event to all connected SSE clients."""
    for q in list(_sse_clients):
        try:
            q.put_nowait(event_dict)
        except asyncio.QueueFull:
            pass


# Hook the SSE push into the monitor
monitor_mod.set_event_callback(_push_sse)


# ──────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────
@router.get("/api/health")
def health():
    return {"status": "ok", "system": "TRACYN", "tagline": "Trace. Detect. Analyze. Defend."}


# ──────────────────────────────────────────────
# Dashboard Summary
# ──────────────────────────────────────────────
@router.get("/api/dashboard/summary")
def dashboard_summary():
    session = get_session()
    repo = Repository(session)
    stats = repo.get_summary_stats()
    session.close()
    stats["monitor_status"] = "ACTIVE" if monitor_mod.is_running() else "INACTIVE"
    return stats


# ──────────────────────────────────────────────
# Events
# ──────────────────────────────────────────────
@router.get("/api/events")
def list_events(limit: int = 100):
    session = get_session()
    repo = Repository(session)
    events = repo.get_all_events(limit=limit)
    result = [_event_to_dict(e) for e in events]
    session.close()
    return result


@router.get("/api/events/{event_id}")
def get_event(event_id: str):
    session = get_session()
    repo = Repository(session)
    evt = repo.get_event_by_id(event_id)
    if not evt:
        session.close()
        raise HTTPException(status_code=404, detail="Event not found")
    result = _event_to_dict(evt)
    session.close()
    return result


def _event_to_dict(evt) -> dict:
    return {
        "event_id": evt.event_id,
        "timestamp": evt.timestamp.isoformat() if evt.timestamp else None,
        "event_type": evt.event_type,
        "path": evt.path,
        "old_hash": evt.old_hash,
        "new_hash": evt.new_hash,
        "user": evt.user,
        "process": evt.process,
        "risk_score": evt.risk_score,
        "severity": evt.severity,
        "reason": evt.reason,
        "status": evt.status,
    }


# ──────────────────────────────────────────────
# Files
# ──────────────────────────────────────────────
@router.get("/api/files")
def list_files():
    session = get_session()
    repo = Repository(session)
    files = repo.get_all_files()
    result = [_file_to_dict(f) for f in files]
    session.close()
    return result


def _file_to_dict(f) -> dict:
    return {
        "id": f.id,
        "path": f.path,
        "filename": f.filename,
        "extension": f.extension,
        "size": f.size,
        "sha256": f.sha256,
        "criticality": f.criticality,
        "first_seen": f.first_seen.isoformat() if f.first_seen else None,
        "last_seen": f.last_seen.isoformat() if f.last_seen else None,
    }


# ──────────────────────────────────────────────
# Incidents
# ──────────────────────────────────────────────
@router.get("/api/incidents")
def list_incidents():
    session = get_session()
    incidents = session.query(IncidentRecord).order_by(IncidentRecord.created_at.desc()).all()
    result = [_incident_to_dict(i) for i in incidents]
    session.close()
    return result


@router.get("/api/incidents/{incident_number}")
def get_incident(incident_number: str):
    session = get_session()
    repo = Repository(session)
    inc = repo.get_incident_by_id(incident_number)
    if not inc:
        session.close()
        raise HTTPException(status_code=404, detail="Incident not found")
    result = _incident_to_dict(inc, include_events=True)
    session.close()
    return result


@router.post("/api/incidents/{incident_number}/status")
def update_incident_status(incident_number: str, body: IncidentStatusUpdate):
    session = get_session()
    repo = Repository(session)
    inc_mgr = IncidentManager(repo)
    valid_statuses = ["NEW", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED", "FALSE_POSITIVE"]
    if body.status not in valid_statuses:
        session.close()
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {valid_statuses}")
    inc = inc_mgr.update_status(incident_number, body.status, body.analyst_notes)
    if not inc:
        session.close()
        raise HTTPException(status_code=404, detail="Incident not found")
    result = _incident_to_dict(inc)
    session.close()
    return result


def _incident_to_dict(inc, include_events=False) -> dict:
    d = {
        "id": inc.id,
        "incident_number": inc.incident_number,
        "title": inc.title,
        "severity": inc.severity,
        "status": inc.status,
        "risk_score": inc.risk_score,
        "created_at": inc.created_at.isoformat() if inc.created_at else None,
        "updated_at": inc.updated_at.isoformat() if inc.updated_at else None,
        "resolved_at": inc.resolved_at.isoformat() if inc.resolved_at else None,
        "analyst_notes": inc.analyst_notes,
        "event_count": len(inc.events),
    }
    if include_events:
        d["events"] = [_event_to_dict(e) for e in sorted(inc.events, key=lambda e: e.timestamp or datetime.min)]
    return d


# ──────────────────────────────────────────────
# Baselines
# ──────────────────────────────────────────────
@router.get("/api/baselines")
def list_baselines():
    session = get_session()
    baselines = session.query(BaselineRecord).order_by(BaselineRecord.created_at.desc()).all()
    result = [_baseline_to_dict(b) for b in baselines]
    session.close()
    return result


@router.post("/api/baselines")
def create_new_baseline():
    result = create_baseline(_config)
    return result


@router.post("/api/baselines/{baseline_id}/verify")
def verify_baseline(baseline_id: int):
    session = get_session()
    baseline = session.query(BaselineRecord).filter_by(id=baseline_id).first()
    if not baseline:
        session.close()
        raise HTTPException(status_code=404, detail="Baseline not found")
    session.close()
    return {"baseline_id": baseline_id, "status": baseline.status, "verified": True}


def _baseline_to_dict(b) -> dict:
    return {
        "id": b.id,
        "version": b.version,
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "created_by": b.created_by,
        "description": b.description,
        "status": b.status,
        "file_count": len(b.baseline_files),
    }


# ──────────────────────────────────────────────
# Scan
# ──────────────────────────────────────────────
@router.post("/api/scan")
def run_integrity_scan():
    results = run_scan(_config)
    return {"changes_detected": len(results), "events": results}


# ──────────────────────────────────────────────
# Monitor
# ──────────────────────────────────────────────
@router.post("/api/monitor/start")
def start_monitoring():
    started = monitor_mod.start_monitor(_config)
    return {"started": started, "status": "ACTIVE" if monitor_mod.is_running() else "INACTIVE"}


@router.post("/api/monitor/stop")
def stop_monitoring():
    monitor_mod.stop_monitor()
    return {"status": "STOPPED"}


@router.get("/api/monitor/status")
def monitor_status():
    return {"status": "ACTIVE" if monitor_mod.is_running() else "INACTIVE"}


# ──────────────────────────────────────────────
# Reports
# ──────────────────────────────────────────────
@router.post("/api/reports")
def create_report(fmt: str = "json"):
    report = generate_report(fmt=fmt)
    if fmt in ["html", "csv"]:
        mime = "text/html" if fmt == "html" else "text/csv"
        return Response(content=report["content"], media_type=mime)
    return report


# ──────────────────────────────────────────────
# Demo
# ──────────────────────────────────────────────
@router.post("/api/demo/{scenario}")
def run_demo_scenario(scenario: str):
    scenarios = {
        "normal_change": scenario_normal_change,
        "sensitive_change": scenario_sensitive_config_change,
        "new_file": scenario_new_executable,
        "delete_file": scenario_critical_deletion,
        "burst": scenario_burst_attack,
        "reset": reset_demo,
    }
    fn = scenarios.get(scenario)
    if not fn:
        raise HTTPException(status_code=404, detail=f"Unknown scenario '{scenario}'. Valid: {list(scenarios.keys())}")
    result = fn()
    return result


# ──────────────────────────────────────────────
# SSE — Live event stream
# ──────────────────────────────────────────────
@router.get("/api/events/stream")
async def events_stream():
    q: asyncio.Queue = asyncio.Queue(maxsize=50)
    _sse_clients.append(q)

    async def generator():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=30)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            _sse_clients.remove(q)

    return StreamingResponse(generator(), media_type="text/event-stream")
