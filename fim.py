import hashlib
import json
import os
import argparse
from datetime import datetime

folder_path = "monitored_files"
baseline_file = "baseline.json"


def calculate_hash(file_path):
    with open(file_path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()

def calculate_baseline_hash():
    return calculate_hash(baseline_file)


def log_alert(risk, alert_type, file_path):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("alerts.log", "a") as log_file:
        log_file.write(
            f"{current_time} | {risk} | {alert_type} | {file_path}\n"
        )


def create_baseline():
    baseline = {}


    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path):
            baseline[file_path] = calculate_hash(file_path)

    with open(baseline_file, "w") as file:
         json.dump(baseline, file, indent=4)

    baseline_hash = calculate_baseline_hash()

    with open("baseline.sha256", "w") as file:
        file.write(baseline_hash)

    print("Baseline created successfully!")
    print("Files monitored:", len(baseline))
    print("Baseline protection hash created.")


def check_integrity():

    with open(baseline_file, "r") as file:
        baseline = json.load(file)


    # Verify baseline integrity
    current_baseline_hash = calculate_baseline_hash()

    with open("baseline.sha256", "r") as file:
        original_baseline_hash = file.read().strip()

    if current_baseline_hash != original_baseline_hash:
        print("\n🚨 CRITICAL ALERT")
        print("The baseline file has been modified!")
        print("Integrity scan stopped.")
        return
    current_files = {}
    alerts = 0
    modified = 0
    deleted = 0
    new_files = 0


    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path):
            current_files[file_path] = calculate_hash(file_path)

    print("\n==============================================")
    print("        CYBERSECURITY FILE INTEGRITY MONITOR")
    print("==============================================")

    # Check modified and deleted files
    for file_path, original_hash in baseline.items():

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if file_path not in current_files:

            print(f"\n[{current_time}] 🚨 HIGH RISK")
            print("ALERT: FILE DELETED")
            print("File:", file_path)

            log_alert("HIGH", "FILE DELETED", file_path)

            alerts += 1
            deleted += 1

        elif current_files[file_path] != original_hash:

            print(f"\n[{current_time}] 🚨 HIGH RISK")
            print("ALERT: FILE MODIFIED")
            print("File:", file_path)
            print("Original Hash:", original_hash)
            print("Current Hash :", current_files[file_path])
            log_alert("HIGH", "FILE MODIFIED", file_path)
            alerts += 1
            modified += 1


    # Check new files
    for file_path in current_files:

        if file_path not in baseline:

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"\n[{current_time}] ⚠️ MEDIUM RISK")
            print("ALERT: NEW FILE DETECTED")
            print("File:", file_path)
            log_alert("MEDIUM", "NEW FILE", file_path)
            alerts += 1
            new_files += 1

    print("\n==============================================")
    print("                 SCAN SUMMARY")
    print("==============================================")
    print("Files checked  :", len(current_files))
    print("Modified files :", modified)
    print("Deleted files  :", deleted)
    print("New files      :", new_files)
    print("Total alerts   :", alerts)
    print("==============================================")




parser = argparse.ArgumentParser(
    description="Cybersecurity File Integrity Monitoring Tool",
    epilog="""
Examples:
  python3 fim.py --baseline
  python3 fim.py --scan
"""
)

parser.add_argument(
    "--baseline",
    action="store_true",
    help="Create a new file integrity baseline"
)

parser.add_argument(
    "--scan",
    action="store_true",
    help="Scan files for integrity changes"
)

args = parser.parse_args()

if args.baseline:
    create_baseline()

elif args.scan:
    check_integrity()

else:
    parser.print_help()



