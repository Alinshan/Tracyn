# 🔐 File Integrity Monitoring Tool

A Python-based cybersecurity tool that monitors files and detects unauthorized changes using SHA-256 cryptographic hashing.

## 📌 Overview

File Integrity Monitoring (FIM) helps security professionals detect unexpected changes to important files.

This project creates a trusted baseline of file hashes and compares the current state of monitored files against that baseline.

### The tool can detect:

- Modified files
- Deleted files
- New files
- Unauthorized changes to the trusted baseline

## ✨ Features

- SHA-256 file hashing
- Automatic baseline creation
- File modification detection
- File deletion detection
- New file detection
- Baseline integrity protection
- Risk levels
- Timestamped security alerts
- Alert logging
- Scan summary
- Command-line interface

## 🛠️ Technologies Used

- Python 3
- SHA-256
- JSON
- Linux
- Command Line Interface

No external Python packages are required.

## 📂 Project Structure

```text
file-integrity-monitor/
│
├── fim.py
├── README.md
├── .gitignore
│
└── monitored_files/
    └── config.txt
Generated Files
These files are created when the tool runs:
baseline.json
baseline.sha256
alerts.log
They are excluded from Git using .gitignore.
🚀 Usage
Create a trusted baseline
python3 fim.py --baseline
Scan for file changes
python3 fim.py --scan
Display help
python3 fim.py --help
🧪 Testing
Test file modification
Modify the monitored file:
echo "File has been modified." > monitored_files/config.txt
Then run:
python3 fim.py --scan
The tool should detect the file modification.
Test new-file detection
Create a new file:
echo "New file detected." > monitored_files/newfile.txt
Then run:
python3 fim.py --scan
The tool should detect the new file.
Test deleted-file detection
Delete a file that was included in the baseline:
rm monitored_files/config.txt
Then run:
python3 fim.py --scan
The tool should detect the deleted file.
🔎 How It Works
              Monitored Files
                     │
                     ▼
               SHA-256 Hash
                     │
                     ▼
              Trusted Baseline
                     │
                     ▼
               Integrity Scan
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Modified    Deleted      New
          │          │          │
          └──────────┼──────────┘
                     ▼
               Security Alert
                     │
                     ▼
                  Alert Log
🔐 Security Concept
Each monitored file is given a SHA-256 hash, which acts as a digital fingerprint.
During a scan, the current hash is compared with the original hash.
Original Hash = Current Hash
        ↓
    No change
Original Hash ≠ Current Hash
        ↓
    File changed
        ↓
      ALERT
The project also stores a SHA-256 hash of the baseline file itself. This helps detect unauthorized changes to the trusted baseline.
📊 Example Output
==============================================
        CYBERSECURITY FILE INTEGRITY MONITOR
==============================================

[2026-09-14 22:30:15] HIGH RISK
ALERT: FILE MODIFIED
File: monitored_files/config.txt

Original Hash: 8a7c...
Current Hash : 4f82...

==============================================
                 SCAN SUMMARY
==============================================
Files checked  : 1
Modified files : 1
Deleted files  : 0
New files      : 0
Total alerts   : 1
==============================================
🎯 Learning Objectives
This project demonstrates practical knowledge of:
- Cryptographic hashing
- File integrity monitoring
- Security baselines
- Change detection
- Security alerting
- Security logging
- Python automation
- Linux command-line tools
🔮 Future Improvements
- Real-time file monitoring
- Email notifications
- Web-based security dashboard
- CSV/PDF security reports
- Multiple monitored directories
- Database-backed event logging
- Configurable monitoring rules
- Improved alert severity
⚠️ Disclaimer
This project is intended for educational and defensive cybersecurity purposes. Only monitor files and systems that you own or have permission to monitor.
👩‍💻 Author
Nyla S
Cybersecurity Student
