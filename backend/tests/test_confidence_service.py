from app.services.confidence_service import (
    _skill_overlap,
    _complexity,
    _repo_health,
    calculate_baseline_confidence,
)


def test_skill_overlap_high_when_language_matches():
    assert _skill_overlap(["Python"], "Python") == "high"


def test_skill_overlap_low_when_language_differs():
    assert _skill_overlap(["Python"], "Rust") == "low"


def test_skill_overlap_partial_when_repo_language_unknown():
    assert _skill_overlap(["Python"], None) == "partial"


def test_complexity_low_for_typo_fix():
    assert _complexity("Fix a typo in the README", comments_count=1) == "low"


def test_complexity_high_for_architecture_change():
    assert _complexity("This requires a full architecture redesign", comments_count=2) == "high"


def test_complexity_high_when_many_comments():
    assert _complexity("Some ambiguous issue", comments_count=20) == "high"


def test_repo_health_stale_when_no_pushed_at():
    assert _repo_health(None, open_issues=10) == "stale"


def test_calculate_baseline_confidence_high_case():
    issue_data = {
        "user_languages": ["Python"],
        "repo_language": "Python",
        "issue_body": "Add a missing docstring",
        "comments_count": 1,
        "repo_pushed_at": "2026-07-01T00:00:00Z",
        "repo_open_issues": 5,
    }
    result = calculate_baseline_confidence(issue_data)
    assert result["baseline_confidence"] == "High"


def test_calculate_baseline_confidence_low_when_skill_mismatch():
    issue_data = {
        "user_languages": ["Rust"],
        "repo_language": "Python",
        "issue_body": "Fix something",
        "comments_count": 1,
        "repo_pushed_at": "2026-07-01T00:00:00Z",
        "repo_open_issues": 5,
    }
    result = calculate_baseline_confidence(issue_data)
    assert result["baseline_confidence"] == "Low"