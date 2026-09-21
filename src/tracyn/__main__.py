"""
tracyn.__main__ — Allows `python -m tracyn` as an alternative launcher.
"""
import sys
import uvicorn
from .utils.config import load_config

if __name__ == "__main__":
    cfg = load_config()
    server_cfg = cfg.get("server", {})
    uvicorn.run(
        "tracyn.app:app",
        host=server_cfg.get("host", "0.0.0.0"),
        port=server_cfg.get("port", 8000),
        reload=server_cfg.get("reload", False),
        log_level="info",
    )
