from models import LABELS, severity_for_mentions

def test_labels_are_the_five_expected():
    assert set(LABELS) == {
        "BUG_REPORT", "FEATURE_REQUEST", "COMPLAINT", "POSITIVE", "SPAM"
    }

def test_severity_boundaries():
    assert severity_for_mentions(10) == "critical"
    assert severity_for_mentions(11) == "critical"
    assert severity_for_mentions(9) == "medium"
    assert severity_for_mentions(3) == "medium"
    assert severity_for_mentions(2) == "low"
    assert severity_for_mentions(0) == "low"
