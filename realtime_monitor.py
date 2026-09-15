import os
import time
import hashlib
from datetime import datetime

MONITORED_DIR = "monitored_files"
CHECK_INTERVAL = 2
LOG_FILE = "alerts.log"


def calculate_hash(filepath):
    with open(filepath, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()


def get_file_hashes():
    hashes = {}

    for root, _, files in os.walk(MONITORED_DIR):
        for filename in files:
            filepath = os.path.join(root, filename)

            try:
                hashes[filepath] = calculate_hash(filepath)
            except (FileNotFoundError, PermissionError):
                pass

    return hashes


def log_alert(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"

    print(log_message)

    with open(LOG_FILE, "a") as log:
        log.write(log_message + "\n")


print("=" * 50)
print("   REAL-TIME FILE INTEGRITY MONITOR")
print("=" * 50)
print(f"Monitoring: {MONITORED_DIR}")
print(f"Alert log: {LOG_FILE}")
print("Press Ctrl+C to stop.\n")

previous_hashes = get_file_hashes()

try:
    while True:
        time.sleep(CHECK_INTERVAL)

        current_hashes = get_file_hashes()

        # Detect modified files
        for filepath in current_hashes:
            if filepath in previous_hashes:
                if current_hashes[filepath] != previous_hashes[filepath]:
                    log_alert(f"ALERT: FILE MODIFIED: {filepath}")

        # Detect new files
        for filepath in current_hashes:
            if filepath not in previous_hashes:
                log_alert(f"ALERT: NEW FILE: {filepath}")

        # Detect deleted files
        for filepath in previous_hashes:
            if filepath not in current_hashes:
                log_alert(f"ALERT: FILE DELETED: {filepath}")

        previous_hashes = current_hashes

except KeyboardInterrupt:
    print("\nMonitoring stopped.")
