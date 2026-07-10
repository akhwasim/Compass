from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.services.github_service import get_authenticated_user, search_issues, get_repo_metadata
from app.services.confidence_service import calculate_confidence

app = FastAPI(title="Open Source Contribution Matcher")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/debug/github-user")
async def debug_github_user():
    user = await get_authenticated_user()
    return {"login": user.get("login"), "name": user.get("name")}


@app.get("/debug/search-issues")
async def debug_search_issues(language: str = "python"):
    issues = await search_issues(language=language)
    return {
        "count": len(issues),
        "issues": [
            {"title": i["title"], "url": i["html_url"], "repo": i["repository_url"]}
            for i in issues
        ],
    }


@app.get("/debug/confidence-test")
async def debug_confidence_test(language: str = "python"):
    issues = await search_issues(language=language, max_results=5)
    results = []

    for issue in issues:
        repo_full_name = issue["repository_url"].replace("https://api.github.com/repos/", "")
        repo_meta = await get_repo_metadata(repo_full_name)

        issue_data = {
            "issue_title": issue["title"],
            "issue_body": issue.get("body") or "",
            "comments_count": issue.get("comments", 0),
            "repo_language": repo_meta["language"],
            "repo_pushed_at": repo_meta["pushed_at"],
            "repo_open_issues": repo_meta["open_issues_count"],
            "user_languages": [language],
            "user_frameworks": [],
        }

        confidence = calculate_confidence(issue_data)

        results.append({
            "title": issue["title"],
            "repo": repo_full_name,
            "url": issue["html_url"],
            "confidence": confidence,
        })

    return {"count": len(results), "results": results}