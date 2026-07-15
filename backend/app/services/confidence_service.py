from datetime import datetime, timezone


def _skill_overlap(user_languages: list[str], repo_language: str) -> str:
    user_skills = {s.lower() for s in user_languages}
    repo_lang = (repo_language or "").lower()

    if repo_lang in user_skills:
        return "high"
    elif not repo_lang:
        return "partial"
    else:
        return "low"


def _complexity(issue_body: str, comments_count: int) -> str:
    body = (issue_body or "").lower()

    high_signals = ["architecture", "breaking change", "performance", "refactor entire", "redesign"]
    low_signals = ["typo", "documentation", "docs", "readme", "small fix", "simple", "screenshot"]

    if any(sig in body for sig in high_signals) or comments_count > 15:
        return "high"
    if any(sig in body for sig in low_signals):
        return "low"
    if comments_count <= 5:
        return "low"
    return "medium"


def _repo_health(pushed_at: str, open_issues: int) -> str:
    if not pushed_at:
        return "stale"

    pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    days_since_push = (datetime.now(timezone.utc) - pushed_date).days

    if days_since_push <= 30 and open_issues < 500:
        return "active"
    elif days_since_push <= 180:
        return "moderate"
    else:
        return "stale"


def calculate_baseline_confidence(issue_data: dict) -> dict:
    """
    Computes confidence from purely deterministic, verifiable signals.
    Clarity is intentionally NOT included here — it requires actually
    understanding the issue text, which is a reasoning task handled
    later by the LLM (which can only downgrade this baseline, never
    upgrade it, to bound hallucination risk).
    """
    skill = _skill_overlap(issue_data["user_languages"], issue_data["repo_language"])
    complexity = _complexity(issue_data["issue_body"], issue_data["comments_count"])
    health = _repo_health(issue_data["repo_pushed_at"], issue_data["repo_open_issues"])

    baseline = _baseline_score(skill, complexity, health)

    return {
        "skill_overlap": skill,
        "complexity": complexity,
        "repo_health": health,
        "baseline_confidence": baseline,
    }


def _baseline_score(skill: str, complexity: str, health: str) -> str:
    if skill == "low":
        return "Low"
    if skill == "high" and complexity == "low" and health in ("active", "moderate"):
        return "High"
    if health == "stale" or complexity == "high":
        return "Low"
    return "Medium"