import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from .hasher import calculate_sha256
from .baseline import get_active_baseline_map
from ..database.database import get_session
from ..database.repositories import Repository
from ..security.risk_engine import RiskEngine
from ..security.attribution import get_current_attribution
from ..security.incident import IncidentManager

logger = logging.getLogger("tracyn")

_observer: Optional[Observer] = None
_monitor_thread: Optional[threading.Thread] = None
_is_running = False
_event_callback: Optional[Callable] = None  # Optional callback for SSE/WS push


def set_event_callback(callback: Callable):
    global _event_callback
    _event_callback = callback


class TRACYNEventHandler(FileSystemEventHandler):
    def __init__(self, config: Dict, exclude_patterns: list = None):
        super().__init__()
        self.config = config
        self.exclude_patterns = exclude_patterns or []
        self.risk_engine = RiskEngine(config)
        self._recent_paths: Dict[str, float] = {}  # path -> last event time

    def _should_exclude(self, path: str) -> bool:
        import fnmatch
        name = Path(path).name
        return any(
            fnmatch.fnmatch(name, pat) or pat in path
            for pat in self.exclude_patterns
        )

    def _is_burst(self, path: str) -> bool:
        now = time.time()
        recent_count = sum(1 for t in self._recent_paths.values() if now - t < 10)
        self._recent_paths[path] = now
        # Prune old entries
        self._recent_paths = {p: t for p, t in self._recent_paths.items() if now - t < 30}
        return recent_count >= 4

    def _process(self, event_type: str, path: str, src_path: str = None):
        if self._should_exclude(path):
            return

        attribution = get_current_attribution()
        is_burst = self._is_burst(path)

        old_hash = None
        new_hash = None

        baseline_map = get_active_baseline_map()
        if baseline_map:
            old_hash = baseline_map.get(path)

        if event_type != "DELETED_FILE":
            try:
                new_hash = calculate_sha256(path)
            except (FileNotFoundError, PermissionError):
                pass

        score, severity, reasons = self.risk_engine.evaluate(
            event_type=event_type,
            path=path,
            user=attribution.get("user", "UNKNOWN"),
            process=attribution.get("process", "UNKNOWN"),
            is_burst=is_burst
        )
        reason_text = "\n".join(f"• {r}" for r in reasons)

        try:
            session = get_session()
            repo = Repository(session)
            file_rec = repo.get_or_create_file(
                path=path,
                sha256=new_hash or old_hash,
                criticality=self.risk_engine.get_file_criticality(path)
            )
            event = repo.create_event(
                event_type=event_type,
                path=path,
                old_hash=old_hash,
                new_hash=new_hash,
                user=attribution.get("user", "UNKNOWN"),
                process=attribution.get("process", "UNKNOWN"),
                risk_score=score,
                severity=severity,
                reason=reason_text,
                file_id=file_rec.id
            )
            inc_mgr = IncidentManager(repo, self.config)
            inc_mgr.process_event(event)
            session.close()

            logger.info(f"[{severity}] {event_type}: {path} (risk={score})")

            event_dict = {
                "event_id": event.event_id,
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "path": path,
                "severity": severity,
                "risk_score": score,
                "reasons": reasons,
            }

            if _event_callback:
                _event_callback(event_dict)

        except Exception as e:
            logger.error(f"Error processing event for {path}: {e}")

    def on_modified(self, event):
        if not event.is_directory:
            self._process("MODIFIED", event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._process("NEW_FILE", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._process("DELETED_FILE", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._process("DELETED_FILE", event.src_path)
            self._process("NEW_FILE", event.dest_path)


def start_monitor(config: Dict) -> bool:
    global _observer, _is_running

    if _is_running:
        return False

    mon_cfg = config.get("monitoring", {})
    paths = mon_cfg.get("paths", ["./demo_environment"])
    recursive = mon_cfg.get("recursive", True)
    exclude = mon_cfg.get("exclude_patterns", [])

    handler = TRACYNEventHandler(config, exclude_patterns=exclude)
    _observer = Observer()

    for path in paths:
        p = Path(path)
        if p.exists():
            _observer.schedule(handler, str(p), recursive=recursive)
            logger.info(f"Monitoring: {p}")

    _observer.start()
    _is_running = True
    logger.info("Real-time monitor ACTIVE")
    return True


def stop_monitor():
    global _observer, _is_running
    if _observer and _is_running:
        _observer.stop()
        _observer.join()
        _is_running = False
        logger.info("Real-time monitor STOPPED")


def is_running() -> bool:
    return _is_running
