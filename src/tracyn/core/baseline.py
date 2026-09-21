import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .hasher import calculate_sha256, calculate_sha256_string
from ..database.database import get_session
from ..database.repositories import Repository


def _build_file_map(paths: list, recursive: bool = True, exclude_patterns: list = None) -> Dict[str, str]:
    """Walk monitored paths and collect {filepath: sha256} mapping."""
    import fnmatch
    exclude = exclude_patterns or []
    file_map = {}

    for base_path in paths:
        base = Path(base_path)
        if not base.exists():
            continue

        if base.is_file():
            file_map[str(base)] = calculate_sha256(str(base))
            continue

        walker = base.rglob("*") if recursive else base.glob("*")
        for fp in walker:
            if not fp.is_file():
                continue
            rel = str(fp)
            skip = any(fnmatch.fnmatch(fp.name, pat) or pat in rel for pat in exclude)
            if skip:
                continue
            try:
                file_map[str(fp)] = calculate_sha256(str(fp))
            except (PermissionError, FileNotFoundError):
                pass

    return file_map


def create_baseline(config: Dict) -> Dict:
    """Create a new trusted baseline from monitored paths."""
    mon_cfg = config.get("monitoring", {})
    paths = mon_cfg.get("paths", ["./demo_environment"])
    recursive = mon_cfg.get("recursive", True)
    exclude = mon_cfg.get("exclude_patterns", [])

    file_map = _build_file_map(paths, recursive, exclude)

    # Tamper-protection: hash the JSON representation
    serialised = json.dumps({k: v for k, v in sorted(file_map.items())}, indent=2)
    tamper_hash = calculate_sha256_string(serialised)

    session = get_session()
    repo = Repository(session)
    baseline = repo.create_baseline(
        file_map=file_map,
        version=f"v{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        description=f"Baseline created at {datetime.utcnow().isoformat()}Z",
        tamper_hash=tamper_hash
    )
    baseline_data = {
        "baseline_id": baseline.id,
        "version": baseline.version,
        "files_count": len(file_map),
        "tamper_hash": tamper_hash,
        "created_at": baseline.created_at.isoformat()
    }
    session.close()

    return baseline_data


def get_active_baseline_map() -> Optional[Dict[str, str]]:
    """Return {filepath: sha256} dict of the active baseline."""
    session = get_session()
    repo = Repository(session)
    baseline = repo.get_active_baseline()
    if not baseline:
        session.close()
        return None

    result = {}
    for bf in baseline.baseline_files:
        if bf.file:
            result[bf.file.path] = bf.sha256

    session.close()
    return result
