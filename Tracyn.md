# TRACYN

## Intelligent Cyber Defence, File Integrity & Threat Detection Platform

> **Tagline:** Trace. Detect. Analyze. Defend.

---

# 1. PROJECT OVERVIEW

Build **TRACYN**, a professional defensive cybersecurity platform that continuously monitors critical files and directories, detects suspicious system changes, analyzes their security risk, records evidence, and provides a centralized interface for investigation and incident management.

TRACYN should evolve an existing Python-based File Integrity Monitoring (FIM) project into a complete **Cyber Defence and Threat Detection Platform** suitable for a cybersecurity hackathon demonstration.

The existing project already provides basic functionality such as:

* SHA-256 file hashing
* Trusted baseline creation
* File integrity scanning
* Detection of modified files
* Detection of deleted files
* Detection of newly created files
* Real-time monitoring
* Severity alerts
* Timestamped security logs
* Report generation
* Command-line operation

Do **not** throw away working functionality.

Extend and reorganize the existing implementation into the TRACYN architecture while preserving existing useful features.

---

# 2. PRODUCT IDENTITY

## Official Name

**TRACYN**

## Full Product Name

**TRACYN — Intelligent Cyber Defence, File Integrity & Threat Detection Platform**

## Tagline

**Trace. Detect. Analyze. Defend.**

## Product Description

TRACYN is a defensive cybersecurity platform that continuously monitors system files against trusted integrity baselines, identifies unauthorized or unexpected changes, evaluates contextual risk, preserves security evidence, and assists security teams in investigating potential incidents.

---

# 3. PRIMARY OBJECTIVE

The goal is to transform a simple File Integrity Monitoring tool into a polished cybersecurity platform capable of demonstrating the following security workflow:

```text
                 ┌─────────────────────┐
                 │   Files / Folders   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Trusted Baseline    │
                 │ SHA-256 Hashes      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Integrity Monitor   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Change Detection    │
                 └──────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          MODIFIED        NEW           DELETED
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Context Analysis    │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Risk Analysis       │
                 │ 0–100 Risk Score    │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Alert Generation    │
                 └──────────┬──────────┘
                            ▼
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
     Dashboard          Incident             Reports
                        Management
```

---

# 4. IMPORTANT DEVELOPMENT INSTRUCTIONS

You are an AI coding assistant working inside an existing repository.

Before writing code:

1. Inspect the entire repository.
2. Identify the existing implementation.
3. Identify reusable modules.
4. Identify existing CLI commands.
5. Identify existing hashing and monitoring logic.
6. Identify existing tests.
7. Preserve working functionality.
8. Refactor only where necessary.
9. Do not replace functioning components without reason.
10. Do not fabricate functionality that has not actually been implemented.
11. Every UI feature must connect to real backend functionality.
12. Every displayed security event must originate from real or controlled demo data.
13. Keep the project runnable locally.
14. Keep the architecture modular and maintainable.
15. Add tests for new functionality.
16. Update documentation after implementation.

The finished project must work as an integrated application rather than a collection of disconnected mock screens.

---

# 5. SECURITY SCOPE

TRACYN is a **defensive cybersecurity platform**.

All security demonstrations must remain controlled and authorized.

The project must NOT implement:

* Malware
* Ransomware
* Credential theft
* Keylogging
* Persistence mechanisms
* Privilege escalation
* Exploitation of real systems
* Unauthorized network scanning
* Destructive payloads
* Data exfiltration
* Real-world attack automation

Instead, create a controlled **Demo Mode** that simulates security-relevant file changes inside an isolated project directory.

---

# 6. CORE FEATURES

## 6.1 File Integrity Monitoring

TRACYN must continuously monitor configured files and directories.

The system must detect:

* File creation
* File modification
* File deletion
* File renaming where technically supported
* Hash changes
* Unexpected file type changes
* Changes to configured sensitive files

Each event must contain:

```text
Event ID
Timestamp
Event Type
File Path
Previous Hash
Current Hash
File Size
User
Process
Risk Score
Severity
Status
Reason
```

---

# 7. SHA-256 INTEGRITY ENGINE

Use Python's standard `hashlib` library.

The primary integrity algorithm must be:

```text
SHA-256
```

Do not read extremely large files entirely into memory.

Use chunked hashing.

Conceptual implementation:

```python
import hashlib

def calculate_sha256(path):
    sha256 = hashlib.sha256()

    with open(path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()
```

The final implementation may improve this design while maintaining the same security principle.

---

# 8. BASELINE MANAGEMENT

TRACYN must support trusted baseline creation.

A baseline records the expected state of monitored files.

Example:

```json
{
  "path": "demo_environment/config/application.conf",
  "sha256": "....",
  "size": 2048,
  "created_at": "2026-09-21T10:00:00Z"
}
```

Baseline functionality must include:

* Create baseline
* View baseline
* Compare against baseline
* Update baseline
* Delete baseline
* Verify baseline
* Baseline version/history

The interface must clearly distinguish:

**Trusted Baseline**

from

**Current System State**

---

# 9. CHANGE DETECTION ENGINE

The detection engine compares the current state against the trusted baseline.

Possible results:

```text
NO_CHANGE
MODIFIED
NEW_FILE
DELETED_FILE
RENAMED
HASH_MISMATCH
```

Example:

```text
Baseline:
config.json
SHA-256:
abc123...

Current:
config.json
SHA-256:
98ef21...

Result:
MODIFIED
```

---

# 10. REAL-TIME MONITORING

Use an appropriate filesystem monitoring library such as:

```text
watchdog
```

The monitor should detect filesystem changes without repeatedly performing unnecessary full-directory scans.

When an event occurs:

```text
Filesystem Event
       ↓
Normalize Event
       ↓
Calculate Hash
       ↓
Compare Baseline
       ↓
Classify Event
       ↓
Risk Analysis
       ↓
Create Security Event
       ↓
Store in Database
       ↓
Update Dashboard
```

---

# 11. RISK ENGINE

TRACYN must include an explainable risk scoring engine.

Do NOT make the risk engine a meaningless random number generator.

The score must be calculated from understandable security factors.

Risk score:

```text
0–100
```

Recommended severity levels:

```text
0–24    LOW
25–49   MEDIUM
50–74   HIGH
75–100  CRITICAL
```

The thresholds must be configurable.

---

# 12. RISK FACTORS

The risk engine may consider:

### File Criticality

Example:

```text
Normal file       +5
Configuration     +20
Executable        +25
Security config   +30
System-critical   +35
```

### Event Type

Example:

```text
Normal modification    +10
New executable         +30
Deleted critical file  +35
Hash mismatch          +20
Multiple rapid changes +20
```

### Location

Sensitive directories may increase risk.

Example:

```text
Normal directory       +0
Application directory  +10
Security directory     +20
System directory       +30
```

### Attribution

If reliable user/process information is available:

```text
Known expected process     +0
Unknown process            +10
Unexpected process         +20
```

If attribution cannot be obtained safely or reliably:

```text
User: UNKNOWN
Process: UNKNOWN
```

Never fabricate attribution.

---

# 13. RISK EXPLANATION

Every HIGH or CRITICAL event should explain why it received its score.

Example:

```text
Risk Score: 87
Severity: CRITICAL

Reasons:
• Modified executable file
• File located in sensitive directory
• Unexpected process attribution
• Multiple changes detected within 10 seconds
```

The explanation must be understandable to a human security analyst.

---

# 14. FILE CRITICALITY

Allow administrators to define file criticality.

Example levels:

```text
NORMAL
IMPORTANT
SENSITIVE
CRITICAL
```

Example:

```yaml
criticality:
  "*.txt": NORMAL
  "*.conf": IMPORTANT
  "*.json": IMPORTANT
  "*.exe": SENSITIVE
  "demo_environment/security/*": CRITICAL
```

The implementation may use a more suitable configuration format if required.

---

# 15. INCIDENT MANAGEMENT

TRACYN must group related security events into incidents.

Example:

```text
INC-00042

Title:
Multiple suspicious file modifications

Severity:
HIGH

Events:
17

Affected Files:
8

First Seen:
10:32:14

Last Seen:
10:32:27

Status:
INVESTIGATING
```

Supported incident statuses:

```text
NEW
ACKNOWLEDGED
INVESTIGATING
RESOLVED
FALSE_POSITIVE
```

Users should be able to:

* Open incident
* View associated events
* Add investigation notes
* Change status
* Assign analyst
* Mark false positive
* Resolve incident
* Export incident report

---

# 16. DATABASE

Use SQLite for the default local implementation.

Recommended ORM:

```text
SQLAlchemy
```

Suggested entities:

### files

```text
id
path
filename
extension
size
sha256
criticality
first_seen
last_seen
```

### baselines

```text
id
version
created_at
created_by
description
status
```

### baseline_files

```text
id
baseline_id
file_id
sha256
size
```

### events

```text
id
timestamp
event_type
file_id
path
old_hash
new_hash
user
process
risk_score
severity
reason
status
```

### incidents

```text
id
incident_number
title
description
severity
status
created_at
updated_at
resolved_at
```

### incident_events

```text
incident_id
event_id
```

### configuration

```text
key
value
updated_at
```

Use migrations or a safe initialization mechanism where appropriate.

---

# 17. DASHBOARD

Create a professional security operations dashboard.

Recommended technology:

```text
FastAPI
Jinja2
HTML
CSS
JavaScript
```

A modern frontend framework may be used if the existing project already uses one, but avoid unnecessary complexity.

---

# 18. DASHBOARD DESIGN

The dashboard should feel like a real SOC/security monitoring platform.

Main navigation:

```text
TRACYN
│
├── Dashboard
├── Live Monitor
├── Files
├── Events
├── Incidents
├── Baselines
├── Reports
├── Demo Mode
└── Settings
```

---

# 19. DASHBOARD OVERVIEW

Display:

```text
Files Monitored
Files Modified
New Files
Deleted Files
Open Incidents
Critical Alerts
High Alerts
Current Risk Level
```

Example:

```text
┌─────────────────────────────────────────────────┐
│ TRACYN                          SYSTEM ONLINE    │
├─────────────────────────────────────────────────┤
│                                                 │
│  1,248          17          3          2        │
│  Files        Modified     New       Deleted    │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│        SECURITY ACTIVITY                       │
│                                                 │
│  ● CRITICAL    suspicious.exe modified         │
│  ● HIGH        config.yaml changed             │
│  ● MEDIUM      new file detected               │
│                                                 │
└─────────────────────────────────────────────────┘
```

Use charts where they genuinely improve understanding.

Possible charts:

* Events over time
* Severity distribution
* Event type distribution
* Risk score distribution
* Top modified files
* Incident status

---

# 20. LIVE MONITOR

The Live Monitor should display incoming security events in near real time.

Example:

```text
10:42:31  MODIFIED    config.yaml       HIGH
10:42:33  NEW FILE    unknown.exe       CRITICAL
10:42:35  MODIFIED    settings.json     MEDIUM
10:42:39  DELETED     startup.conf      HIGH
```

New events should appear without requiring a full page refresh where practical.

WebSockets or Server-Sent Events may be used.

---

# 21. EVENT DETAILS

Clicking an event should open a detailed investigation view.

Example:

```text
EVENT EVT-00182

Event Type:
MODIFIED

File:
demo_environment/config/app.conf

Previous SHA-256:
abc123...

Current SHA-256:
def456...

Hash Changed:
YES

User:
demo-user

Process:
demo-editor

Risk Score:
78

Severity:
HIGH

Reasons:
• Sensitive configuration file
• Hash mismatch
• Unexpected modification time

Status:
NEW
```

Provide clear visual differentiation between:

```text
Previous State
Current State
```

---

# 22. FILES VIEW

The Files page should show:

```text
Path
Type
Size
SHA-256
Criticality
Baseline Status
Last Modified
Risk
```

Possible statuses:

```text
TRUSTED
MODIFIED
NEW
MISSING
UNKNOWN
```

Allow filtering by:

* Status
* Criticality
* File type
* Risk
* Directory

---

# 23. INCIDENT VIEW

Provide an analyst-friendly incident investigation interface.

Example:

```text
INC-00017

CRITICAL

Multiple suspicious changes detected

Timeline
──────────────

10:42:01  config.yaml modified
10:42:03  script.sh modified
10:42:04  new executable detected
10:42:05  credentials.conf modified

Affected Files: 4
Risk Score: 91
Status: INVESTIGATING
```

Include:

* Timeline
* Related files
* Related events
* Hashes
* Attribution
* Risk factors
* Analyst notes
* Status controls

---

# 24. REPORTING

TRACYN should generate security reports.

Supported formats:

```text
JSON
CSV
HTML
```

PDF may be added optionally.

Reports should include:

```text
Report ID
Generated At
Monitoring Period
Files Monitored
Total Events
Modified Files
New Files
Deleted Files
Critical Events
High Events
Open Incidents
Resolved Incidents
Top Risk Events
```

Reports should be useful for:

* Hackathon demonstrations
* Security reviews
* Incident investigation
* Evidence preservation
* System audits

---

# 25. SECURITY LOGGING

Use structured logging.

Log:

* Application startup
* Shutdown
* Baseline creation
* Baseline modification
* File changes
* Risk calculations
* Incidents
* Configuration changes
* Errors

Prefer JSON-compatible structured logs where practical.

Example:

```json
{
  "timestamp": "2026-09-21T10:42:31Z",
  "event": "FILE_MODIFIED",
  "path": "demo_environment/config/app.conf",
  "risk": 78,
  "severity": "HIGH"
}
```

---

# 26. DEMO MODE

Create a controlled demonstration environment.

Default demo directory:

```text
demo_environment/
```

TRACYN must NOT automatically monitor sensitive operating-system locations.

Do not default to:

```text
/etc
/var
/root
/home
```

unless explicitly configured by the user.

---

# 27. DEMO SCENARIOS

Create safe simulated scenarios.

## Scenario 1 — Normal Modification

Modify a normal text/configuration file.

Expected:

```text
LOW / MEDIUM
MODIFIED
```

## Scenario 2 — Sensitive Configuration Modification

Modify a sensitive configuration file.

Expected:

```text
HIGH
MODIFIED
```

## Scenario 3 — Suspicious New Executable

Create a harmless dummy executable or executable-like demo file.

Expected:

```text
HIGH / CRITICAL
NEW FILE
```

## Scenario 4 — Critical File Deletion

Delete a controlled demo file.

Expected:

```text
HIGH / CRITICAL
DELETED
```

## Scenario 5 — Burst of Changes

Generate several controlled changes within a short period.

Expected:

```text
Multiple related events
Incident created
Elevated risk
```

The demo must never execute malicious payloads.

---

# 28. DEMO CONTROLS

Dashboard should include:

```text
▶ Start Demo
⏸ Pause Demo
↻ Reset Demo
```

Scenario buttons:

```text
Normal Change
Sensitive Change
New File
Delete File
Burst Attack Simulation
```

Label this clearly:

```text
CONTROLLED DEMONSTRATION ENVIRONMENT
```

---

# 29. CLI

Maintain or implement a clean command-line interface.

Example:

```bash
tracyn init
tracyn baseline create
tracyn baseline show
tracyn scan
tracyn monitor
tracyn events
tracyn incidents
tracyn report
tracyn demo
tracyn dashboard
```

Possible usage:

```bash
python -m tracyn scan
```

The exact CLI architecture may depend on the existing project.

---

# 30. CONFIGURATION

Use a configuration file.

Example:

```yaml
project:
  name: TRACYN
  environment: development

monitoring:
  paths:
    - ./demo_environment

  recursive: true

hashing:
  algorithm: sha256
  chunk_size: 1048576

risk:
  thresholds:
    low: 24
    medium: 49
    high: 74

database:
  url: sqlite:///data/tracyn.db

logging:
  level: INFO
  file: logs/tracyn.log
```

Never hard-code sensitive configuration.

---

# 31. API

Create backend API endpoints.

Suggested endpoints:

```text
GET  /api/health

GET  /api/dashboard/summary

GET  /api/events

GET  /api/events/{id}

GET  /api/files

GET  /api/files/{id}

GET  /api/incidents

GET  /api/incidents/{id}

POST /api/incidents/{id}/status

GET  /api/baselines

POST /api/baselines

POST /api/baselines/{id}/verify

GET  /api/reports

POST /api/reports

POST /api/demo/{scenario}
```

Use proper validation and error handling.

---

# 32. PROJECT STRUCTURE

Use a clean modular architecture.

Recommended structure:

```text
tracyn/
│
├── README.md
├── PROJECT_SPEC.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
│
├── config/
│   └── config.yaml
│
├── data/
│   └── .gitkeep
│
├── logs/
│   └── .gitkeep
│
├── demo_environment/
│   ├── config/
│   ├── scripts/
│   └── data/
│
├── src/
│   └── tracyn/
│       ├── __init__.py
│       ├── __main__.py
│       │
│       ├── cli/
│       │   ├── __init__.py
│       │   └── commands.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── hasher.py
│       │   ├── baseline.py
│       │   ├── scanner.py
│       │   ├── monitor.py
│       │   └── detector.py
│       │
│       ├── security/
│       │   ├── __init__.py
│       │   ├── risk_engine.py
│       │   ├── severity.py
│       │   ├── attribution.py
│       │   └── incident.py
│       │
│       ├── database/
│       │   ├── __init__.py
│       │   ├── database.py
│       │   ├── models.py
│       │   └── repositories.py
│       │
│       ├── reports/
│       │   ├── __init__.py
│       │   └── generator.py
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes.py
│       │   └── schemas.py
│       │
│       ├── dashboard/
│       │   ├── templates/
│       │   └── static/
│       │
│       ├── demo/
│       │   ├── __init__.py
│       │   └── simulator.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── config.py
│           └── logging.py
│
└── tests/
    ├── test_hasher.py
    ├── test_baseline.py
    ├── test_scanner.py
    ├── test_risk_engine.py
    ├── test_database.py
    ├── test_api.py
    └── test_demo.py
```

Adapt this structure to the existing repository rather than blindly recreating it.

---

# 33. TECHNOLOGY STACK

Recommended:

### Backend

```text
Python 3.11+
FastAPI
Uvicorn
Pydantic
SQLAlchemy
```

### Monitoring

```text
watchdog
```

### Hashing

```text
hashlib
```

Python standard library should be preferred.

### Configuration

```text
PyYAML
```

### Frontend

```text
HTML
CSS
JavaScript
Jinja2
```

### Testing

```text
pytest
```

Additional libraries may be introduced only when they provide meaningful functionality.

---

# 34. USER EXPERIENCE

TRACYN should feel like a real cybersecurity product.

Avoid:

* Generic unstyled HTML
* Placeholder dashboards
* Fake statistics
* Random security alerts
* Buttons that do nothing
* Fake AI output
* Hard-coded event counts
* Decorative charts disconnected from backend data

Prefer:

* Dark security-console aesthetic
* Clear severity indicators
* Responsive dashboard
* Real-time event feed
* Search
* Filtering
* Sorting
* Event timelines
* Risk explanations
* Incident workflows
* Clear empty states
* Loading states
* Error states

---

# 35. RESPONSIVE DESIGN

The dashboard should work on:

```text
Desktop
Laptop
Tablet
```

The primary hackathon demonstration target is desktop.

Ensure the dashboard does not break at smaller resolutions.

---

# 36. AI / INTELLIGENCE COMPONENT

If an AI-assisted component is implemented, it must provide meaningful security analysis.

Do not simply label a deterministic rule engine as "AI".

A safe initial implementation can be an explainable rule-based risk engine.

Optional future functionality:

```text
Anomaly detection
Behavior profiling
Change clustering
Natural-language incident summaries
Risk explanation generation
```

Any optional AI functionality must be clearly separated from deterministic security logic.

The core integrity detection must remain reliable without an external AI service.

---

# 37. ATTRIBUTION

Where technically available, attempt to determine:

```text
User
Process
Process ID
```

However:

**Never fabricate attribution.**

If information cannot reliably be determined:

```text
User: UNKNOWN
Process: UNKNOWN
PID: UNKNOWN
```

The system should clearly communicate attribution confidence.

---

# 38. PATH SECURITY

Validate monitored paths.

Prevent unsafe path handling such as:

* Unexpected path traversal
* Writing outside configured demo directories
* Arbitrary file deletion
* Unsafe user-provided paths

Demo Mode must remain confined to:

```text
demo_environment/
```

unless explicitly configured otherwise.

---

# 39. ERROR HANDLING

The application must handle:

* Missing files
* Permission errors
* Invalid configuration
* Corrupted database
* Hashing failures
* Monitoring failures
* Invalid API requests
* Invalid baseline data

Do not silently ignore important errors.

Return useful messages.

---

# 40. TESTING REQUIREMENTS

Implement automated tests.

Minimum tests:

### Hashing

Verify:

```text
Same file → same hash
Changed file → different hash
```

### Baseline

Verify:

```text
Baseline creation
Baseline retrieval
Baseline comparison
```

### Detection

Verify:

```text
Modified file
New file
Deleted file
Unchanged file
```

### Risk Engine

Verify:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Verify deterministic scores.

### Database

Verify:

```text
Event storage
Incident storage
Relationships
```

### API

Verify important endpoints.

### Demo

Verify demo scenarios operate only inside the controlled demo directory.

---

# 41. ACCEPTANCE TEST

The final implementation must support the following complete workflow.

## Step 1

Start TRACYN.

```bash
tracyn dashboard
```

## Step 2

Open the dashboard.

Expected:

```text
TRACYN
SYSTEM ONLINE
```

## Step 3

Create a baseline.

Expected:

```text
Baseline created successfully
```

## Step 4

Start monitoring.

Expected:

```text
Monitoring ACTIVE
```

## Step 5

Modify a monitored demo file.

Expected:

```text
MODIFIED event
```

## Step 6

TRACYN calculates the new SHA-256 hash.

Expected:

```text
Previous Hash
Current Hash
```

## Step 7

Risk engine evaluates the event.

Expected:

```text
Risk Score
Severity
Reasons
```

## Step 8

Dashboard updates.

Expected:

```text
New event visible
```

## Step 9

Generate several controlled changes.

Expected:

```text
Multiple events
```

## Step 10

Incident is created/grouped.

Expected:

```text
INC-XXXXX
```

## Step 11

Open the incident.

Expected:

```text
Timeline
Affected Files
Risk
Evidence
```

## Step 12

Generate report.

Expected:

```text
JSON / CSV / HTML
```

If all of these work, the core TRACYN implementation is considered functional.

---

# 42. HACKATHON DEMONSTRATION FLOW

The recommended live presentation should follow this sequence.

### Opening

Show the TRACYN dashboard.

Say:

> "TRACYN continuously watches critical files and detects changes that could indicate a security incident."

### Baseline

Create the trusted baseline.

Explain:

> "First, TRACYN establishes what a trusted system state looks like."

### Normal Change

Modify a normal demo file.

Show:

```text
LOW
```

Explain:

> "Not every change is automatically considered an attack."

### Suspicious Change

Modify a sensitive file.

Show:

```text
HIGH
```

Explain the risk factors.

### New File

Create a suspicious-looking harmless demo executable.

Show:

```text
CRITICAL
```

### Burst

Trigger multiple controlled changes.

Show:

```text
Incident Created
```

### Investigation

Open the incident.

Show:

* Timeline
* File paths
* Previous hashes
* Current hashes
* Risk score
* Severity
* Attribution
* Evidence

### Report

Generate a security report.

Finish with:

> **"TRACYN doesn't just tell you that something changed. It tells you what changed, why it matters, how risky it is, and gives you the evidence to investigate it."**

---

# 43. README REQUIREMENTS

Update `README.md` to contain:

1. TRACYN branding
2. Project overview
3. Problem statement
4. Features
5. Architecture
6. Installation
7. Configuration
8. CLI usage
9. Dashboard usage
10. Demo Mode
11. Screenshots if available
12. Testing
13. Security scope
14. Project structure
15. Future improvements
16. Hackathon relevance

Do not claim features that are not implemented.

---

# 44. INSTALLATION

The project should support a simple setup.

Example:

```bash
git clone <repository>
cd tracyn

python -m venv .venv

source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Initialize:

```bash
tracyn init
```

Start dashboard:

```bash
tracyn dashboard
```

Document the actual commands implemented by the final project.

---

# 45. ENVIRONMENT

Support:

```text
Linux
Windows
```

Linux is the primary cybersecurity demonstration environment.

Do not assume Linux-only functionality where a cross-platform implementation is practical.

For platform-specific process attribution, implement graceful fallback.

---

# 46. PERFORMANCE

The system should:

* Avoid unnecessary repeated hashing
* Use chunked hashing
* Avoid blocking the dashboard
* Process filesystem events efficiently
* Use database indexes where appropriate
* Handle large numbers of events reasonably
* Avoid memory leaks in long-running monitoring

---

# 47. DATA RETENTION

Implement reasonable event retention configuration.

Example:

```yaml
retention:
  events_days: 30
  incidents_days: 90
```

Do not automatically delete evidence without explicit configuration.

---

# 48. PRIVACY

TRACYN should operate locally by default.

Do not transmit monitored file contents to external services.

Only metadata such as:

```text
Hash
Path
Size
Timestamp
Event
Risk
```

should be used by the monitoring platform unless the user explicitly configures otherwise.

Never upload sensitive file contents to an external AI service by default.

---

# 49. FUTURE EXTENSIONS

The architecture should allow future integration of:

```text
SIEM
EDR
Threat Intelligence
YARA
Sigma
Syslog
Email Alerts
Slack
Microsoft Teams
Webhook Notifications
Machine Learning
Anomaly Detection
Cloud Monitoring
Container Monitoring
```

These are future extensions and should not be implemented as fake functionality.

---

# 50. QUALITY REQUIREMENTS

The final code must be:

* Modular
* Readable
* Tested
* Documented
* Secure by default
* Maintainable
* Cross-platform where practical
* Free from unnecessary complexity

Use:

```text
Type hints
Docstrings
Meaningful variable names
Structured logging
Exception handling
Configuration management
Unit tests
```

Avoid:

```text
Massive single files
Duplicated logic
Hard-coded paths
Hard-coded secrets
Fake data
Unused dependencies
Dead code
```

---

# 51. FINAL PRODUCT DEFINITION

At completion, TRACYN should be described as:

> **TRACYN is a defensive cybersecurity platform that continuously monitors critical files against trusted SHA-256 baselines, detects modifications, creations, deletions and other integrity events, evaluates contextual security risk, records investigation evidence, groups related events into incidents, and provides a centralized security monitoring dashboard.**

The core value proposition is:

```text
TRUSTED STATE
      ↓
CONTINUOUS MONITORING
      ↓
CHANGE DETECTION
      ↓
RISK ANALYSIS
      ↓
SECURITY ALERT
      ↓
INCIDENT INVESTIGATION
      ↓
EVIDENCE & REPORT
```

---

# 52. FINAL IMPLEMENTATION RULE

Do not stop after creating the architecture or UI.

The final repository must contain a **working end-to-end implementation**.

A feature is considered complete only when:

```text
Backend
   ↓
Database
   ↓
Detection Engine
   ↓
Risk Engine
   ↓
API
   ↓
Dashboard
```

are actually connected.

Do not create placeholder buttons for unfinished functionality.

If a feature cannot reasonably be implemented, document it as a future feature instead of pretending it works.

---

# TRACYN

## Trace. Detect. Analyze. Defend.

**Build a real defensive cybersecurity platform, not just a file-monitoring demo.**
