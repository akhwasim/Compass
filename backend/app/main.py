from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.services.github_service import get_authenticated_user
from app.services.github_service import get_authenticated_user, search_issues

from app.services.github_service import search_issues


app = FastAPI(title="Compass")


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