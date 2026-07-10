import os
import httpx

GITHUB_API_BASE = "https://api.github.com"


def _get_headers() -> dict:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set in environment")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


async def get_authenticated_user() -> dict:
    """Sanity check: confirms the token works by fetching the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GITHUB_API_BASE}/user", headers=_get_headers())
        response.raise_for_status()
        return response.json()


async def search_issues(
    language: str,
    label: str = "good first issue",
    max_results: int = 20,
) -> list[dict]:
    """
    Search GitHub for open issues matching a language and label.
    Uses the Search API, sorted by most recently updated (favors active repos).
    """
    query_parts = [
        f'label:"{label}"',
        f"language:{language}",
        "state:open",
        "is:issue",
    ]
    query = " ".join(query_parts)

    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": min(max_results, 100),
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/search/issues",
            headers=_get_headers(),
            params=params,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])


async def get_repo_metadata(repo_full_name: str) -> dict:
    """
    Fetches repo metadata needed for confidence scoring.
    repo_full_name format: "owner/repo"
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/repos/{repo_full_name}",
            headers=_get_headers(),
        )
        response.raise_for_status()
        data = response.json()
        return {
            "language": data.get("language"),
            "pushed_at": data.get("pushed_at"),
            "open_issues_count": data.get("open_issues_count"),
            "stargazers_count": data.get("stargazers_count"),
        }