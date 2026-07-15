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
    Interest-based filtering is intentionally NOT done here — GitHub topic
    filtering proved too sparse when combined with a language filter.
    Interest is instead judged by the LLM at the ranking step.
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


async def get_issue_details(owner: str, repo: str, issue_number: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}",
            headers=_get_headers(),
        )
        response.raise_for_status()
        data = response.json()
        return {
            "title": data.get("title", ""),
            "body": data.get("body") or "",
        }


async def get_readme(owner: str, repo: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme",
            headers={**_get_headers(), "Accept": "application/vnd.github.raw+json"},
        )
        if response.status_code != 200:
            return ""
        return response.text


async def get_folder_structure(owner: str, repo: str) -> list[str]:
    """
    Fetches top-level structure, plus one level deep into the first few subfolders.
    Returns a flat list of verified paths (files and folders).
    """
    verified_paths = []

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/",
            headers=_get_headers(),
        )
        if response.status_code != 200:
            return []

        top_level = response.json()
        if not isinstance(top_level, list):
            return []

        subfolders_to_expand = []
        for item in top_level:
            verified_paths.append(item["path"])
            if item["type"] == "dir":
                subfolders_to_expand.append(item["path"])

        for folder_path in subfolders_to_expand[:5]:
            sub_response = await client.get(
                f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{folder_path}",
                headers=_get_headers(),
            )
            if sub_response.status_code == 200:
                sub_items = sub_response.json()
                if isinstance(sub_items, list):
                    for sub_item in sub_items:
                        verified_paths.append(sub_item["path"])

    return verified_paths