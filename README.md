# TRACYN — Advanced Defensive Cybersecurity Platform

**Trace. Detect. Analyze. Defend.**

TRACYN is an enterprise-grade File Integrity Monitoring (FIM) and Defensive Cybersecurity Platform. Designed for modern Security Operations Centers (SOC), it replaces legacy script-based monitoring with real-time event streaming, a dynamic Risk Engine, a centralized SQLite database, and a stunning dark-themed SOC web dashboard.

---

## 🚀 Key Capabilities

- **Real-Time Monitoring Engine:** Uses OS-level file system hooks (`watchdog`) to instantly detect tampering, rather than slow, resource-heavy polling.
- **Cryptographic Baselines:** Captures highly-optimized SHA-256 chunks of monitored directories. The baseline files themselves are protected with anti-tamper hashes.
- **Advanced Risk Engine:** Auto-classifies incidents based on severity, MITRE ATT&CK heuristics, and risk scoring (LOW, MEDIUM, HIGH, CRITICAL).
- **SOC Web Dashboard:** A live, dark-mode web application featuring real-time Server-Sent Events (SSE) feeds, incident timelines, and security metric tracking.
- **REST API:** A fully integrated `FastAPI` backend for programmatic integration and automation.
- **Unified CLI Tool:** Manage your entire security posture from a single command-line interface.

---

## 🛠 Architecture

TRACYN is built with a modular, scalable architecture:

```text
TRACYN/
├── api/          # FastAPI Routes, Schemas, and SSE Event Streaming
├── cli/          # Click-based Command Line Interface
├── core/         # Baselines, Hashing, Watchdog Real-time Monitors, Scanners
├── dashboard/    # HTML, Vanilla CSS, JS (SOC Dashboard)
├── database/     # SQLAlchemy ORM, SQLite DB, Repositories
├── demo/         # Safe Attack Simulator (Burst, Stealth, Ransomware)
├── reports/      # PDF/TXT Security Report Generators
└── security/     # Risk Engine, Attribution, Severity Classifications
```

---

## 💻 Requirements

- **Python 3.12+**
- Tested on Windows, macOS, and Linux

---

## 📥 Installation

1. Clone the repository:
```bash
git clone https://github.com/Alinshan/Tracyn.git
cd Tracyn
```

2. Install dependencies (creates the global `tracyn` command):
```bash
pip install -e .
```
*(If your Python scripts directory isn't on your PATH, you can use the provided `tracyn.bat` or `tracyn.ps1` wrappers on Windows, or just run `python -m tracyn`)*

---

## 🛡️ Usage & Quick Start

TRACYN is controlled via a centralized command-line interface.

### 1. Launch the SOC Dashboard & API
Starts the FastAPI server and the real-time event stream.
```bash
tracyn serve
```
> **Access the Dashboard:** [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 2. Create a Trusted Baseline
Before monitoring, TRACYN needs a snapshot of the known-good state.
```bash
tracyn baseline create
```

### 3. Start Real-Time Monitoring
Activates the `watchdog` sensor. Any modifications to the monitored directory will instantly trigger the Risk Engine and appear on your dashboard.
```bash
tracyn monitor start
```

### 4. Run an On-Demand Scan
Forces a manual verification of the current filesystem against the active trusted baseline.
```bash
tracyn scan run
```

### 5. Generate a Security Report
Compiles all incidents into an actionable security report.
```bash
tracyn report generate
```

---

## 🎯 Safe Attack Simulation (Demo Mode)

TRACYN includes a safe sandbox to test your defenses and trigger the Risk Engine.

```bash
# Reset the sandbox to a clean state
tracyn demo run reset

# Simulate a brute-force modification attack
tracyn demo run burst
```
*(Watch your dashboard light up in real-time as the simulator modifies files!)*

---

## 🔒 Security Notes

- **Anti-Tampering:** TRACYN secures its own baselines. If a malicious actor modifies the baseline database, TRACYN will immediately abort the scan and raise a `CRITICAL` alert.
- **Environment Context:** TRACYN is built for authorized monitoring only. Always ensure you have explicit permission to monitor the target host.

---

## 📝 Author

**Alinshan**
- GitHub: [https://github.com/Alinshan](https://github.com/Alinshan)

---

## 📄 License

MIT License — Copyright © 2026 Alinshan. All rights reserved.
