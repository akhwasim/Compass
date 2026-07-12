import os
import httpx

GROQ_API_BASE = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def _get_headers() -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in environment")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


async def generate_contributor_profile(
    experience: str,
    languages: list[str],
    frameworks: list[str],
    interests: list[str],
    available_time: str,
) -> str:
    prompt = f"""Given this information about a person looking to contribute to open source, write a short natural-language contributor profile (3-4 sentences max). Be specific and concrete, not generic.

Experience level: {experience}
Languages known: {', '.join(languages) if languages else 'none specified'}
Frameworks known: {', '.join(frameworks) if frameworks else 'none specified'}
Interested in: {', '.join(interests) if interests else 'none specified'}
Available time: {available_time or 'not specified'}

Write only the profile description, no preamble."""

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 200,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GROQ_API_BASE, headers=_get_headers(), json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

import json


async def rank_issues_with_reasoning(
    contributor_profile: str,
    candidate_issues: list[dict],
) -> list[dict]:
    """
    candidate_issues: list of dicts, each with title, repo, url, body_snippet, and confidence breakdown.
    Returns the same issues annotated with 'why' and 'why_not', sorted best-first.
    """
    issues_summary = "\n\n".join(
        f"{i+1}. Title: {issue['title']}\n"
        f"   Repo: {issue['repo']}\n"
        f"   Issue excerpt: {issue.get('body_snippet', '')[:300]}\n"
        f"   Confidence: {issue['confidence']['final_confidence']} "
        f"(skill_overlap={issue['confidence']['skill_overlap']}, "
        f"complexity={issue['confidence']['complexity']}, "
        f"repo_health={issue['confidence']['repo_health']}, "
        f"clarity={issue['confidence']['clarity']})"
        for i, issue in enumerate(candidate_issues)
    )

    prompt = f"""You are a direct, no-fluff mentor helping an open source contributor pick their next issue.

Contributor profile:
{contributor_profile}

Candidate issues (each with a short excerpt and computed confidence signals):
{issues_summary}

For each issue, write:
- "why_not": only if confidence is Low or Medium AND there's a genuine, specific gap. If the fit is actually strong with only a trivial or no real concern, leave this as an empty string rather than inventing one. If confidence is High, always set this to an empty string.

Vary your sentence structure across issues. Do not reuse the same phrasing template repeatedly.

Return ONLY a JSON array, no preamble, no markdown fences, in this exact format:
[
  {{"index": 1, "why": "...", "why_not": "..."}},
  ...
]
Match the index number to the issue number above."""

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6,
        "max_tokens": 1800,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GROQ_API_BASE, headers=_get_headers(), json=payload)
        response.raise_for_status()
        data = response.json()
        raw_text = data["choices"][0]["message"]["content"].strip()

    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        reasoning_list = json.loads(raw_text)
    except json.JSONDecodeError:
        reasoning_list = []

    reasoning_by_index = {item["index"]: item for item in reasoning_list}

    for i, issue in enumerate(candidate_issues):
        reasoning = reasoning_by_index.get(i + 1, {})
        issue["why"] = reasoning.get("why", "")
        issue["why_not"] = reasoning.get("why_not", "")

    confidence_order = {"High": 0, "Medium": 1, "Low": 2}
    candidate_issues.sort(key=lambda x: confidence_order.get(x["confidence"]["final_confidence"], 3))

    return candidate_issues