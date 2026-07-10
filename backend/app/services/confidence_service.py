from datetime import datetime, timezone


def _skill_overlap(user_languages: list[str], user_frameworks: list[str], repo_language: str, issue_text: str) -> str:
    user_skills = {s.lower() for s in user_languages + user_frameworks}
    repo_lang = (repo_language or "").lower()
    issue_text_lower = issue_text.lower()

    lang_match = repo_lang in user_skills
    framework_mentioned = any(fw.lower() in issue_text_lower for fw in user_frameworks)

    if lang_match and framework_mentioned:
        return "high"
    elif lang_match or framework_mentioned:
        return "partial"
    else:
        return "low"


def _complexity(issue_body: str, comments_count: int) -> str:
    body = (issue_body or "").lower()
    word_count = len(body.split())

    high_signals = ["architecture", "breaking change", "performance", "refactor entire", "redesign"]
    low_signals = ["typo", "documentation", "docs", "readme", "small fix", "simple"]

    if any(sig in body for sig in high_signals) or comments_count > 15:
        return "high"
    if any(sig in body for sig in low_signals) and word_count < 150:
        return "low"
    if word_count < 100 and comments_count <= 5:
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


def _clarity(issue_body: str) -> str:
    body = issue_body or ""
    word_count = len(body.split())
    has_structure = "```" in body or "- " in body or "1." in body

    if word_count >= 40 and has_structure:
        return "clear"
    elif word_count >= 40:
        return "clear"
    else:
        return "vague"


def calculate_confidence(issue_data: dict) -> dict:
    skill = _skill_overlap(
        issue_data["user_languages"],
        issue_data["user_frameworks"],
        issue_data["repo_language"],
        issue_data["issue_title"] + " " + issue_data["issue_body"],
    )
    complexity = _complexity(issue_data["issue_body"], issue_data["comments_count"])
    health = _repo_health(issue_data["repo_pushed_at"], issue_data["repo_open_issues"])
    clarity = _clarity(issue_data["issue_body"])

    final = _final_score(skill, complexity, health, clarity)

    return {
        "skill_overlap": skill,
        "complexity": complexity,
        "repo_health": health,
        "clarity": clarity,
        "final_confidence": final,
    }


def _final_score(skill: str, complexity: str, health: str, clarity: str) -> str:
    if skill == "low":
        return "Low"
    if skill == "high" and complexity == "low" and health in ("active", "moderate") and clarity == "clear":
        return "High"
    if health == "stale" or complexity == "high":
        return "Low"
    return "Medium"