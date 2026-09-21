import os
import yaml
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG = {
    "project": {
        "name": "TRACYN",
        "tagline": "Trace. Detect. Analyze. Defend.",
        "environment": "development"
    },
    "monitoring": {
        "paths": ["./demo_environment", "./monitored_files"],
        "recursive": True,
        "exclude_patterns": ["*.tmp", "*.log", "*.db", "*.sha256", "__pycache__", ".git"]
    },
    "hashing": {
        "algorithm": "sha256",
        "chunk_size": 1048576
    },
    "risk": {
        "thresholds": {"low": 24, "medium": 49, "high": 74},
        "criticality": {
            "*.txt": "NORMAL",
            "*.conf": "IMPORTANT",
            "*.json": "IMPORTANT",
            "*.yaml": "IMPORTANT",
            "*.sh": "SENSITIVE",
            "*.exe": "CRITICAL"
        }
    },
    "database": {
        "url": "sqlite:///data/tracyn.db"
    },
    "logging": {
        "level": "INFO",
        "file": "logs/tracyn.log"
    },
    "dashboard": {
        "host": "127.0.0.1",
        "port": 8000
    }
}


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
            # Deep merge default with user_config
            merged = DEFAULT_CONFIG.copy()
            for key, val in user_config.items():
                if isinstance(val, dict) and key in merged and isinstance(merged[key], dict):
                    merged[key] = {**merged[key], **val}
                else:
                    merged[key] = val
            return merged
    except Exception as e:
        print(f"Warning: Failed to load config from {config_path}: {e}")
        return DEFAULT_CONFIG.copy()
