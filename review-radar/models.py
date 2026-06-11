LABELS = ["BUG_REPORT", "FEATURE_REQUEST", "COMPLAINT", "POSITIVE", "SPAM"]

# similarity thresholds for app resolution
MATCH_THRESHOLD = 0.85
AMBIGUOUS_THRESHOLD = 0.40

def severity_for_mentions(count: int) -> str:
    if count >= 10:
        return "critical"
    if count >= 3:
        return "medium"
    return "low"
