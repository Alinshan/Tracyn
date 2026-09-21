import fnmatch
from typing import Dict, List, Tuple
from .severity import calculate_severity


class RiskEngine:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.criticality_rules = self.config.get("risk", {}).get("criticality", {
            "*.txt": "NORMAL",
            "*.conf": "IMPORTANT",
            "*.json": "IMPORTANT",
            "*.yaml": "IMPORTANT",
            "*.sh": "SENSITIVE",
            "*.py": "SENSITIVE",
            "*.exe": "CRITICAL",
            "demo_environment/config/*": "CRITICAL"
        })
        self.thresholds = self.config.get("risk", {}).get("thresholds", {"low": 24, "medium": 49, "high": 74})

    def get_file_criticality(self, path: str) -> str:
        norm_path = path.replace("\\", "/")
        filename = norm_path.split("/")[-1]

        # Check explicit path matching first
        for pattern, crit in self.criticality_rules.items():
            if "/" in pattern:
                if fnmatch.fnmatch(norm_path, pattern) or pattern in norm_path:
                    return crit
            elif fnmatch.fnmatch(filename, pattern):
                return crit

        return "NORMAL"

    def evaluate(
        self,
        event_type: str,
        path: str,
        user: str = "UNKNOWN",
        process: str = "UNKNOWN",
        is_burst: bool = False
    ) -> Tuple[int, str, List[str]]:
        score = 0
        reasons = []
        norm_path = path.replace("\\", "/")
        filename = norm_path.split("/")[-1]
        ext = filename.split(".")[-1].lower() if "." in filename else ""

        crit = self.get_file_criticality(norm_path)

        # 1. File Criticality Score
        if crit == "CRITICAL":
            score += 35
            reasons.append("System-critical or security configuration file")
        elif crit == "SENSITIVE":
            score += 25
            reasons.append("Sensitive file type or executable script")
        elif crit == "IMPORTANT":
            score += 20
            reasons.append("Important application configuration file")
        else:
            score += 5
            reasons.append("Standard data or text file")

        # 2. Event Type Score
        if event_type == "DELETED_FILE":
            if crit in ["CRITICAL", "SENSITIVE"]:
                score += 35
                reasons.append("Deleted critical security file")
            else:
                score += 15
                reasons.append("Deleted monitored file")
        elif event_type == "NEW_FILE":
            if ext in ["exe", "bat", "sh", "py", "ps1"] or crit in ["CRITICAL", "SENSITIVE"]:
                score += 30
                reasons.append("New executable or script created in monitored directory")
            else:
                score += 10
                reasons.append("New file added to monitored directory")
        elif event_type in ["MODIFIED", "HASH_MISMATCH"]:
            if crit in ["CRITICAL", "SENSITIVE"]:
                score += 25
                reasons.append("Unauthorized modification to sensitive file")
            else:
                score += 10
                reasons.append("Monitored file content modified")

        # 3. Location Sensitive Factor
        if "security" in norm_path or "config" in norm_path:
            score += 20
            reasons.append("File located in sensitive security/config directory")
        elif "scripts" in norm_path or "bin" in norm_path:
            score += 10
            reasons.append("File located in application scripts directory")

        # 4. Attribution
        if user == "UNKNOWN" or process == "UNKNOWN":
            score += 10
            reasons.append("Modification process or user attribution unverified")

        # 5. Rapid Burst Factor
        if is_burst:
            score += 20
            reasons.append("Multiple rapid file changes detected within short timeframe")

        # Cap score at 100
        score = min(100, score)
        severity = calculate_severity(score, self.thresholds)

        return score, severity, reasons
