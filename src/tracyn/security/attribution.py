import os
import getpass
import platform


def get_current_attribution() -> dict:
    try:
        current_user = getpass.getuser()
    except Exception:
        current_user = "UNKNOWN"

    # On Windows or Linux, we don't fabricate process info unless verifiable
    return {
        "user": current_user if current_user else "UNKNOWN",
        "process": f"python (PID: {os.getpid()})" if os.getpid() else "UNKNOWN",
        "pid": os.getpid() if os.getpid() else "UNKNOWN",
        "confidence": "MEDIUM" if current_user != "UNKNOWN" else "LOW"
    }
