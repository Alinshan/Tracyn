def calculate_severity(score: int, thresholds: dict = None) -> str:
    if thresholds is None:
        thresholds = {"low": 24, "medium": 49, "high": 74}

    if score <= thresholds.get("low", 24):
        return "LOW"
    elif score <= thresholds.get("medium", 49):
        return "MEDIUM"
    elif score <= thresholds.get("high", 74):
        return "HIGH"
    else:
        return "CRITICAL"
