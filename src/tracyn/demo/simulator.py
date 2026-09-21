import os
import random
import shutil
import time
from datetime import datetime
from pathlib import Path

DEMO_DIR = Path("demo_environment")
SAFE_PATHS = {
    "normal_text": DEMO_DIR / "data" / "notes.txt",
    "sensitive_config": DEMO_DIR / "config" / "app.conf",
    "security_config": DEMO_DIR / "config" / "security.conf",
    "script": DEMO_DIR / "scripts" / "startup.sh",
    "suspicious_exe": DEMO_DIR / "data" / "update.exe",
}


def _ensure_demo_env():
    """Ensure demo environment exists with initial files."""
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    (DEMO_DIR / "config").mkdir(exist_ok=True)
    (DEMO_DIR / "scripts").mkdir(exist_ok=True)
    (DEMO_DIR / "data").mkdir(exist_ok=True)

    if not SAFE_PATHS["normal_text"].exists():
        SAFE_PATHS["normal_text"].write_text(
            "# Demo Notes File\n\nThis is a normal application notes file.\n"
            "Created for TRACYN demonstration purposes.\n"
        )
    if not SAFE_PATHS["sensitive_config"].exists():
        SAFE_PATHS["sensitive_config"].write_text(
            "# Application Configuration\n\n"
            "host=localhost\nport=8080\ndebug=false\n"
            "database_url=sqlite:///data/app.db\n"
        )
    if not SAFE_PATHS["security_config"].exists():
        SAFE_PATHS["security_config"].write_text(
            "# Security Configuration\n\n"
            "auth_enabled=true\nsession_timeout=3600\n"
            "max_login_attempts=5\n"
        )
    if not SAFE_PATHS["script"].exists():
        SAFE_PATHS["script"].write_text(
            "#!/bin/bash\n# Demo startup script\necho 'Application starting...'\n"
        )


def reset_demo():
    """Reset demo environment to clean state."""
    for key, path in SAFE_PATHS.items():
        if key == "suspicious_exe" and path.exists():
            path.unlink()

    SAFE_PATHS["normal_text"].write_text(
        "# Demo Notes File\n\nThis is a normal application notes file.\n"
        "Created for TRACYN demonstration purposes.\n"
    )
    SAFE_PATHS["sensitive_config"].write_text(
        "# Application Configuration\n\n"
        "host=localhost\nport=8080\ndebug=false\n"
        "database_url=sqlite:///data/app.db\n"
    )
    SAFE_PATHS["security_config"].write_text(
        "# Security Configuration\n\n"
        "auth_enabled=true\nsession_timeout=3600\n"
        "max_login_attempts=5\n"
    )
    SAFE_PATHS["script"].write_text(
        "#!/bin/bash\n# Demo startup script\necho 'Application starting...'\n"
    )
    return {"result": "Demo environment reset to clean state."}


def scenario_normal_change() -> dict:
    """Scenario 1 — Modify a normal text file. Expected: LOW/MEDIUM."""
    _ensure_demo_env()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    SAFE_PATHS["normal_text"].write_text(
        f"# Demo Notes File\n\nUpdated at {ts} for demonstration.\n"
        "This simulates a routine file modification.\n"
    )
    return {"scenario": "normal_change", "file": str(SAFE_PATHS["normal_text"]), "expected": "LOW/MEDIUM"}


def scenario_sensitive_config_change() -> dict:
    """Scenario 2 — Modify sensitive config. Expected: HIGH."""
    _ensure_demo_env()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    SAFE_PATHS["sensitive_config"].write_text(
        f"# Application Configuration — MODIFIED {ts}\n\n"
        "host=0.0.0.0\nport=8080\ndebug=true\n"
        "database_url=sqlite:///data/app.db\n"
        "# WARNING: Debug mode enabled\n"
    )
    return {"scenario": "sensitive_config_change", "file": str(SAFE_PATHS["sensitive_config"]), "expected": "HIGH"}


def scenario_new_executable() -> dict:
    """Scenario 3 — Drop a harmless dummy .exe. Expected: HIGH/CRITICAL."""
    _ensure_demo_env()
    SAFE_PATHS["suspicious_exe"].write_text(
        "DEMO FILE — NOT A REAL EXECUTABLE\n"
        "This file simulates a suspicious new executable in TRACYN demo mode.\n"
        "It contains no harmful code.\n"
    )
    return {"scenario": "new_executable", "file": str(SAFE_PATHS["suspicious_exe"]), "expected": "HIGH/CRITICAL"}


def scenario_critical_deletion() -> dict:
    """Scenario 4 — Delete a critical config file. Expected: HIGH/CRITICAL."""
    _ensure_demo_env()
    deleted_path = str(SAFE_PATHS["security_config"])
    if SAFE_PATHS["security_config"].exists():
        SAFE_PATHS["security_config"].unlink()
        return {"scenario": "critical_deletion", "file": deleted_path, "expected": "HIGH/CRITICAL"}
    return {"scenario": "critical_deletion", "error": "File already deleted. Run reset first."}


def scenario_burst_attack() -> dict:
    """Scenario 5 — Multiple rapid changes. Expected: Multiple events, incident created."""
    _ensure_demo_env()
    changed = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    SAFE_PATHS["normal_text"].write_text(f"Burst change 1 at {ts}\n")
    changed.append(str(SAFE_PATHS["normal_text"]))
    time.sleep(0.3)

    SAFE_PATHS["sensitive_config"].write_text(f"# Burst change 2 at {ts}\nhost=0.0.0.0\n")
    changed.append(str(SAFE_PATHS["sensitive_config"]))
    time.sleep(0.3)

    burst_file = DEMO_DIR / "data" / "burst_new.txt"
    burst_file.write_text(f"New file burst at {ts}\n")
    changed.append(str(burst_file))
    time.sleep(0.3)

    SAFE_PATHS["script"].write_text(f"#!/bin/bash\n# Modified at {ts}\necho 'Modified'\n")
    changed.append(str(SAFE_PATHS["script"]))

    return {
        "scenario": "burst_attack",
        "files_changed": changed,
        "expected": "Multiple HIGH/CRITICAL events, incident auto-created"
    }
