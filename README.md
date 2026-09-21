# Tracyn — File Integrity Monitor

A Python tool that detects unauthorized changes to files using SHA-256 cryptographic hashing. It tracks file modifications, deletions, and new file additions — and generates timestamped security alerts and reports.

---

## What This Project Does

Integrity Monitor works by taking a snapshot (baseline) of your files' SHA-256 hashes. Every time you run a scan or enable real-time monitoring, it compares the current file state against that baseline and raises alerts for any differences.

It can detect:
- **Modified files** — content has changed since the baseline
- **Deleted files** — a previously monitored file is gone
- **New files** — a file appeared that wasn't in the baseline

All detected events are logged to `alerts.log` with a timestamp and severity level, and can be exported as a `security_report.txt`.

---

## Features

| Feature | Description |
|---|---|
| SHA-256 hashing | Cryptographically strong hash per file |
| Baseline protection | The baseline file itself is hashed to detect tampering |
| Integrity scanning | On-demand comparison against the baseline |
| Real-time monitoring | Continuous polling every 2 seconds for live detection |
| Severity levels | LOW / MEDIUM / HIGH per event type |
| Alert logging | All events saved to `alerts.log` with timestamps |
| Security report | Summary report exported to `security_report.txt` |
| Interactive menu | CLI menu to run all functions without memorising commands |

---

## How It Works

```
monitored_files/
       |
       v
 SHA-256 hashing
       |
       v
 baseline.json  <--  baseline.sha256 (tamper check)
       |
       v
 Integrity scan / Real-time monitor
       |
  +---------+---------+
  |         |         |
  v         v         v
MODIFIED  DELETED   NEW FILE
  |         |         |
  +---------+---------+
            |
            v
       alerts.log
            |
            v
    security_report.txt
```

---

## Project Structure

```
Integrity-Monitor/
├── fim.py                  # Baseline creation and integrity scanning
├── realtime_monitor.py     # Continuous real-time file monitoring
├── generate_report.py      # Security report generator
├── menu.py                 # Interactive CLI menu
├── README.md
├── REAL_TIME_MONITORING.md # Real-time monitoring walkthrough
├── LICENSE
├── .gitignore
└── monitored_files/
    └── config.txt          # Example monitored file
```

---

## Requirements

- Python 3 (no external packages required)
- Linux / Kali Linux recommended

---

## Installation

```bash
git clone https://github.com/Alinshan/Tracyn.git
cd Tracyn
python3 --version
```

---

## Usage

### Interactive Menu (recommended)

```bash
python3 menu.py
```

```
========================================
      FILE INTEGRITY MONITOR
========================================
1. Create baseline
2. Scan files
3. Start real-time monitoring
4. Generate security report
5. Exit
========================================
```

### Create a Baseline

```bash
python3 fim.py --baseline
```

Hashes every file in `monitored_files/`, saves results to `baseline.json`, and creates `baseline.sha256` to protect the baseline from tampering.

### Run an Integrity Scan

```bash
python3 fim.py --scan
```

Compares current file hashes against the baseline. Reports modified, deleted, and new files with severity levels and a scan summary.

### Start Real-Time Monitoring

```bash
python3 realtime_monitor.py
```

Polls `monitored_files/` every 2 seconds and prints a live alert whenever a change is detected. Press `Ctrl+C` to stop.

### Generate a Security Report

```bash
python3 generate_report.py
```

Reads `alerts.log` and writes a formatted summary to `security_report.txt`, including counts by severity and all recorded events.

---

## Alert Severity Levels

| Severity | Trigger |
|---|---|
| `LOW` | A new file appeared in the monitored directory |
| `MEDIUM` | An existing monitored file was modified |
| `HIGH` | An existing monitored file was deleted |

Example alerts in `alerts.log`:

```
2026-09-21 18:00:00 | HIGH   | FILE DELETED  | monitored_files/config.txt
2026-09-21 18:01:00 | MEDIUM | FILE MODIFIED | monitored_files/config.txt
2026-09-21 18:02:00 | LOW    | NEW FILE      | monitored_files/testfile.txt
```

---

## Testing

Add a file (LOW alert):

```bash
echo "test" > monitored_files/testfile.txt
python3 fim.py --scan
```

Modify a file (MEDIUM alert):

```bash
echo "changed" >> monitored_files/config.txt
python3 fim.py --scan
```

Delete a file (HIGH alert):

```bash
rm monitored_files/testfile.txt
python3 fim.py --scan
```

> Only test on files and systems you own or have permission to monitor.

---

## Security Notes

- `baseline.sha256` stores a hash of `baseline.json`. If the baseline file is tampered with, the scan is aborted with a critical alert before any comparison is made.
- `security_report.txt` and `alerts.log` are excluded from Git via `.gitignore`.
- This tool is intended for educational and authorized security monitoring only.

---

## Author

**Alinshan**

- GitHub: https://github.com/Alinshan

---

## License

MIT License — Copyright © 2026 Alinshan. All rights reserved.
