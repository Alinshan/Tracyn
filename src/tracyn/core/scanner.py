import fnmatch
import logging
from pathlib import Path
from typing import Dict, List

from .baseline import _build_file_map, get_active_baseline_map
from .detector import detect_changes
from ..database.database import get_session
from ..database.repositories import Repository
from ..security.risk_engine import RiskEngine
from ..security.attribution import get_current_attribution
from ..security.incident import IncidentManager

logger = logging.getLogger("tracyn")


def run_scan(config: Dict) -> List[Dict]:
    """
    Run a full integrity scan.
    Compares current filesystem state against active baseline.
    Returns list of event dicts.
    """
    mon_cfg = config.get("monitoring", {})
    paths = mon_cfg.get("paths", ["./demo_environment"])
    recursive = mon_cfg.get("recursive", True)
    exclude = mon_cfg.get("exclude_patterns", [])

    baseline_map = get_active_baseline_map()
    if baseline_map is None:
        logger.warning("No active baseline found. Run 'tracyn baseline create' first.")
        return []

    current_map = _build_file_map(paths, recursive, exclude)
    changes = detect_changes(baseline_map, current_map)

    if not changes:
        logger.info("Scan complete. No changes detected.")
        return []

    risk_engine = RiskEngine(config)
    attribution = get_current_attribution()
    user = attribution.get("user", "UNKNOWN")
    process = attribution.get("process", "UNKNOWN")

    session = get_session()
    repo = Repository(session)
    inc_mgr = IncidentManager(repo, config)

    results = []
    for change in changes:
        score, severity, reasons = risk_engine.evaluate(
            event_type=change["event_type"],
            path=change["path"],
            user=user,
            process=process,
            is_burst=len(changes) > 5
        )
        reason_text = "\n".join(f"• {r}" for r in reasons)

        # Get or create file record
        file_rec = repo.get_or_create_file(
            path=change["path"],
            sha256=change.get("new_hash") or change.get("old_hash"),
            criticality=risk_engine.get_file_criticality(change["path"])
        )

        event = repo.create_event(
            event_type=change["event_type"],
            path=change["path"],
            old_hash=change.get("old_hash"),
            new_hash=change.get("new_hash"),
            user=user,
            process=process,
            risk_score=score,
            severity=severity,
            reason=reason_text,
            file_id=file_rec.id
        )

        inc_mgr.process_event(event)

        logger.info(f"[{severity}] {change['event_type']}: {change['path']} (risk={score})")

        results.append({
            "event_id": event.event_id,
            "event_type": change["event_type"],
            "path": change["path"],
            "severity": severity,
            "risk_score": score,
            "reasons": reasons,
            "old_hash": change.get("old_hash"),
            "new_hash": change.get("new_hash")
        })

    session.close()
    logger.info(f"Scan complete. {len(results)} change(s) detected.")
    return results
