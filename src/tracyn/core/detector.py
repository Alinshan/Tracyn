from typing import Dict, List, Tuple

from .hasher import calculate_sha256


def detect_changes(
    baseline: Dict[str, str],
    current: Dict[str, str]
) -> List[Dict]:
    """
    Compare baseline against current state.

    Returns a list of change dicts with keys:
      event_type, path, old_hash, new_hash
    """
    changes = []
    all_paths = set(baseline.keys()) | set(current.keys())

    for path in all_paths:
        old_hash = baseline.get(path)
        new_hash = current.get(path)

        if old_hash and not new_hash:
            changes.append({
                "event_type": "DELETED_FILE",
                "path": path,
                "old_hash": old_hash,
                "new_hash": None
            })
        elif not old_hash and new_hash:
            changes.append({
                "event_type": "NEW_FILE",
                "path": path,
                "old_hash": None,
                "new_hash": new_hash
            })
        elif old_hash and new_hash and old_hash != new_hash:
            changes.append({
                "event_type": "MODIFIED",
                "path": path,
                "old_hash": old_hash,
                "new_hash": new_hash
            })

    return changes
