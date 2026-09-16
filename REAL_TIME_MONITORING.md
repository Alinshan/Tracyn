# ⚡ Real-Time File Integrity Monitoring

This document explains how to use the real-time monitoring feature of the File Integrity Monitoring Tool.

## 1. Start Real-Time Monitoring

Open a terminal and go to the project directory.

```bash
cd ~/file-integrity-monitor
```

Start the real-time monitor.

```bash
python3 realtime_monitor.py
```

You should see:

```text
==================================================
   REAL-TIME FILE INTEGRITY MONITOR
==================================================
Monitoring: monitored_files
Alert log: alerts.log
Press Ctrl+C to stop.
```

Keep this terminal running.

## 2. Test File Modification

Open a second terminal and go to the project directory.

```bash
cd ~/file-integrity-monitor
```

Modify the monitored file.

```bash
echo "Real-time test" >> monitored_files/config.txt
```

The first terminal should show an alert similar to:

```text
[2026-09-15 19:00:00] ALERT: FILE MODIFIED: monitored_files/config.txt
```

## 3. Test New File Detection

Create a new test file.

```bash
echo "New file test" > monitored_files/testfile.txt
```

The first terminal should show:

```text
[2026-09-15 19:01:00] ALERT: NEW FILE: monitored_files/testfile.txt
```

## 4. Test Deleted File Detection

Delete the test file.

```bash
rm monitored_files/testfile.txt
```

The first terminal should show:

```text
[2026-09-15 19:02:00] ALERT: FILE DELETED: monitored_files/testfile.txt
```

## 5. View the Alert Log

The real-time monitor automatically saves detected alerts to `alerts.log`.

To view the recorded alerts:

```bash
cat alerts.log
```

Example:

```text
[2026-09-15 19:00:00] ALERT: FILE MODIFIED: monitored_files/config.txt
[2026-09-15 19:01:00] ALERT: NEW FILE: monitored_files/testfile.txt
[2026-09-15 19:02:00] ALERT: FILE DELETED: monitored_files/testfile.txt
```

## 6. Stop Real-Time Monitoring

Return to the first terminal and press:

```text
Ctrl + C
```

The monitor will stop safely.

## 7. Restore the Test File

The modification test changes `config.txt`. Restore it using Git:

```bash
git restore monitored_files/config.txt
```

Then check the project:

```bash
git status
```

A clean project should show:

```text
nothing to commit, working tree clean
```

## How It Works

The real-time monitor checks the `monitored_files` directory every few seconds.

It calculates SHA-256 hashes and compares the current state with the previous state.

It reports:

- **FILE MODIFIED** — an existing file changed
- **NEW FILE** — a new file appeared
- **FILE DELETED** — a previously monitored file disappeared

Every detected alert is displayed in the terminal and saved with a timestamp in `alerts.log`.


## 🚨 Alert Severity Levels

The real-time monitor uses three severity levels:

- LOW — A new file was detected.
- MEDIUM — An existing file was modified.
- HIGH — An existing file was deleted.

Examples:

[LOW] NEW FILE: monitored_files/testfile.txt

[MEDIUM] FILE MODIFIED: monitored_files/config.txt

[HIGH] FILE DELETED: monitored_files/testfile.txt

These severity levels help users quickly understand the importance of each detected file integrity event.



## ⚠️ Important

Use this tool only on files and systems that you own or have permission to monitor.

## © Copyright

Copyright © 2026 Nyla S. All rights reserved.

This project is created and maintained by Nyla S. The author retains all copyright and ownership rights to this project.
