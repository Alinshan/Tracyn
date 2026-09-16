# 🔐 File Integrity Monitoring Tool

A Python-based cybersecurity tool that monitors files and detects unauthorized changes using SHA-256 cryptographic hashing.

## 📌 Overview

File Integrity Monitoring (FIM) is a security technique used to detect unexpected or unauthorized changes to important files.

This project creates a trusted baseline of file hashes and compares the current state of monitored files against that baseline.

The tool can detect:

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
```

### Generated Files

The following files are automatically generated when the tool runs:

```text
baseline.json
baseline.sha256
alerts.log
```

These files are excluded from Git using `.gitignore`.

## 🚀 Step-by-Step Usage

Follow the steps below to use the File Integrity Monitoring Tool.

### Step 1 — Clone the repository

```bash
git clone https://github.com/nylagouri2003/file-integrity-monitor.git
```

### Step 2 — Enter the project directory

```bash
cd file-integrity-monitor
```

### Step 3 — Check the monitored files

```bash
ls monitored_files
```

You should see:

```text
config.txt
```

### Step 4 — Create the trusted baseline

```bash
python3 fim.py --baseline
```

This creates a trusted baseline containing the SHA-256 hashes of the monitored files.

### Step 5 — Run an integrity scan

```bash
python3 fim.py --scan
```

If no files have changed, the scan should report:

```text
Modified files : 0
Deleted files  : 0
New files      : 0
Total alerts   : 0
```

---

## 🧪 Testing the Tool

The following steps demonstrate how the tool detects different types of file changes.

### Test 1 — Detect a modified file

#### Step 6 — Modify the monitored file

```bash
echo "File has been modified." > monitored_files/config.txt
```

#### Step 7 — Run the scan

```bash
python3 fim.py --scan
```

The tool should detect a **FILE MODIFIED** alert.

---

### Test 2 — Detect a new file

#### Step 8 — Create a new file

```bash
echo "New file detected." > monitored_files/newfile.txt
```

#### Step 9 — Run the scan

```bash
python3 fim.py --scan
```

The tool should detect a **NEW FILE** alert.

---

### Test 3 — Detect a deleted file

#### Step 10 — Delete the new file

```bash
rm monitored_files/newfile.txt
```

#### Step 11 — Run the scan

```bash
python3 fim.py --scan
```

The tool will compare the current monitored directory with the trusted baseline.

---

### Step 12 — Restore the sample file

If you deleted `config.txt` during testing, restore it with:

```bash
echo "Sample configuration file for FIM testing." > monitored_files/config.txt
```

### Step 13 — Create a fresh baseline

```bash
python3 fim.py --baseline
```

### Step 14 — Perform a final scan

```bash
python3 fim.py --scan
```

A clean scan should show:

```text
Modified files : 0
Deleted files  : 0
New files      : 0
Total alerts   : 0
```
# ⚡ Real-Time File Integrity Monitoring

This document explains how to use the real-time monitoring feature of the File Integrity Monitoring Tool.

## 1. Start Real-Time Monitoring

Open a terminal and go to the project directory.

```bash
cd ~/file-integrity-monitor
```

Start the real-time monitor:

```bash
python3 realtime_monitor.py
```

You should see:

```text
==================================================
   REAL-TIME FILE INTEGRITY MONITOR
==================================================
Monitoring: monitored_files
Press Ctrl+C to stop.
```

Keep this terminal running.

## 2. Test File Modification

Open a second terminal.

Go to the project directory:

```bash
cd ~/file-integrity-monitor
```

Modify the monitored file:

```bash
echo "Real-time test" >> monitored_files/config.txt
```

The first terminal should show:

```text
[ALERT] FILE MODIFIED: monitored_files/config.txt
```

## 3. Test New File Detection

In the second terminal, create a new file:

```bash
echo "New file test" > monitored_files/testfile.txt
```

The first terminal should show:

```text
[ALERT] NEW FILE: monitored_files/testfile.txt
```

## 4. Test Deleted File Detection

Delete the test file:

```bash
rm monitored_files/testfile.txt
```

The first terminal should show:

```text
[ALERT] FILE DELETED: monitored_files/testfile.txt
```

## 5. Stop Real-Time Monitoring

Return to the first terminal and press:

```text
Ctrl + C
```

The monitor will stop safely.

## 🖥️ Interactive Menu

For an easier way to use the tool, run:

```bash
python3 menu.py  
```


## 🔎 How It Works

```text
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
```
```

The real-time monitor checks the `monitored_files` directory every few seconds.

It calculates SHA-256 hashes and compares the current state with the previous state.

It reports:

- **FILE MODIFIED** — an existing file changed
- **NEW FILE** — a new file appeared
- **FILE DELETED** — a previously monitored file disappeared

## 🔐 Security Concept

Each monitored file is given a SHA-256 hash, which acts as a digital fingerprint.

During a scan, the current hash is compared with the original hash stored in the trusted baseline.

```text
Original Hash = Current Hash
        ↓
    No change
```

```text
Original Hash ≠ Current Hash
        ↓
    File changed
        ↓
      ALERT
```

The project also stores a SHA-256 hash of the baseline file itself. This helps detect unauthorized changes to the trusted baseline.

## 📊 Example Output

```text
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
```

## 🎯 Learning Objectives

This project demonstrates practical knowledge of:

- Cryptographic hashing
- File Integrity Monitoring
- Security baselines
- File change detection
- Security alerting
- Security logging
- Python automation
- Linux command-line tools

## 🔮 Future Improvements

Possible future improvements include:

- Real-time file monitoring
- Email notifications
- Web-based security dashboard
- CSV/PDF security reports
- Multiple monitored directories
- Database-backed event logging
- Configurable monitoring rules
- Improved alert severity
- Automated security reports

## ⚠️ Disclaimer

This project is intended for educational and defensive cybersecurity purposes.

Only monitor files and systems that you own or have permission to monitor.

## 👩‍💻 Author

**Nyla S**

Cybersecurity Student

## 📜 Copyright & Usage

Copyright © 2026 Nyla S. All rights reserved.

This project is created and maintained by Nyla S.

You may view this project and follow the documented steps for personal, educational, and cybersecurity learning purposes.

You may not claim this project as your own, remove the author's name or copyright notice, or redistribute the source code as your own work without written permission from the author.

The author retains all copyright and ownership rights to this project.
