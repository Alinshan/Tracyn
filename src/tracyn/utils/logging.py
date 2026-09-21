import json
import logging
import os
from datetime import datetime
from pathlib import Path


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcfromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_obj.update(record.extra)
        return json.dumps(log_obj)


def setup_logger(log_file: str = "logs/tracyn.log", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("tracyn")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    # Console Handler
    c_handler = logging.StreamHandler()
    c_format = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File Handler (JSON structured logs)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        f_handler = logging.FileHandler(log_file, encoding="utf-8")
        f_handler.setFormatter(JsonFormatter())
        logger.addHandler(f_handler)

    return logger
