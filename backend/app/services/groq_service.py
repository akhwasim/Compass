import os
import json
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


async def rank_issues_with_reasoning(
    contributor_profile: str,
    candidate_issues: list[dict],
    interests: list[str] = None,
) -> list[dict]:
    """
    candidate_issues: list of dicts, each with title, repo, url, body_snippet, and baseline confidence breakdown.
    The LLM reads the real issue text and may downgrade (never upgrade) the baseline
    confidence if the issue is genuinely unclear. It also judges topical fit against
    stated interests, but that only affects the "why" explanation, not the confidence tier.
    Returns issues annotated with 'why', 'why_not', and final 'confidence', sorted best-first.
    """
    issues_summary = "\n\n".join(
        f"{i+1}. Title: {issue['title']}\n"
        f"   Repo: {issue['repo']}\n"
        f"   Issue excerpt: {issue.get('body_snippet', '')[:300]}\n"
        f"   Baseline confidence: {issue['confidence']['baseline_confidence']} "
        f"(skill_overlap={issue['confidence']['skill_overlap']}, "
        f"complexity={issue['confidence']['complexity']}, "
        f"repo_health={issue['confidence']['repo_health']})"
        for i, issue in enumerate(candidate_issues)
    )

    interests_line = (
        f"Interested in: {', '.join(interests)}" if interests else "No specific interest area stated"
    )

    prompt = f"""You are a direct, no-fluff mentor helping an open source contributor pick their next issue.

Contributor profile:
{contributor_profile}
{interests_line}

Candidate issues (each with a real excerpt and a baseline confidence computed from skill match, complexity, and repo activity):
{issues_summary}

For each issue:
1. Read the actual excerpt and judge if it is genuinely clear (a beginner could understand what's being asked) or genuinely vague (missing context, unclear scope, ambiguous). Short issues can absolutely be clear — don't confuse brevity with vagueness. Only mark it vague if a reasonable person would actually be confused about what to do.
2. Decide the final confidence: start from the baseline confidence given. If the issue is vague, downgrade it by exactly one tier (High->Medium, Medium->Low). If it's clear, keep the baseline as-is. NEVER upgrade above the baseline.
3. Write "why": 1-2 sentences, SPECIFIC to what the issue actually asks for (reference the actual excerpt content). State plainly whether it fits, don't hedge unless truly uncertain.
4. Write "why_not": only if final confidence is Low or Medium AND there's a genuine, specific gap (which may include "the issue description is vague" if you judged it that way). If the fit is strong with no real concern, leave this as an empty string. If final confidence is High, always set this to an empty string.
5. If the contributor stated an interest area (e.g. frontend, backend, AI), judge from the issue excerpt whether this issue actually relates to that interest. This should influence your "why" explanation (mention the connection or lack of it) but should NOT change the confidence tier — confidence is about ability to solve it, not topic match.

Vary your sentence structure across issues. Do not reuse the same phrasing template repeatedly.

Return ONLY a JSON array, no preamble, no markdown fences, in this exact format:
[
  {{"index": 1, "clarity": "clear", "confidence": "High", "why": "...", "why_not": "..."}},
  ...
]
Match the index number to the issue number above. "confidence" must be one of "High", "Medium", "Low"."""

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 2000,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GROQ_API_BASE, headers=_get_headers(), json=payload)
            response.raise_for_status()
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"].strip()

        raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        reasoning_list = json.loads(raw_text)
    except (httpx.HTTPError, httpx.TimeoutException, json.JSONDecodeError, KeyError):
        reasoning_list = []

    reasoning_by_index = {item["index"]: item for item in reasoning_list}

    for i, issue in enumerate(candidate_issues):
        reasoning = reasoning_by_index.get(i + 1, {})
        issue["confidence"]["final_confidence"] = reasoning.get(
            "confidence", issue["confidence"]["baseline_confidence"]
        )
        issue["why"] = reasoning.get("why", "")
        issue["why_not"] = reasoning.get("why_not", "")

    confidence_order = {"High": 0, "Medium": 1, "Low": 2}
    candidate_issues.sort(
        key=lambda x: confidence_order.get(x["confidence"]["final_confidence"], 3)
    )

    return candidate_issues


async def explain_issue(
    issue_title: str,
    issue_body: str,
    readme_text: str,
    folder_structure: list[str],
) -> dict:
    folder_list = ", ".join(folder_structure[:60]) if folder_structure else "unknown"
    readme_excerpt = (readme_text or "")[:1500]
    issue_excerpt = (issue_body or "")[:1500]

    prompt = f"""You are helping a beginner understand a GitHub issue before they attempt it.

Issue title: {issue_title}
Issue body:
{issue_excerpt}

Repository README excerpt:
{readme_excerpt}

Top-level folder/file structure: {folder_list}

Based ONLY on the information above (do not invent file contents you cannot see), provide:
- "summary": 2-3 plain-language sentences explaining what this issue is asking for.
- "likely_files": ONLY reference exact paths that appear in the "Top-level folder/file structure" list above. Do not invent or guess filenames that aren't in that list. If no specific verified file clearly matches, instead describe the likely location in plain words (e.g. "a routes file inside the backend/routes folder") rather than naming an unverified file.
- "concepts": a list of 2-5 concepts/skills someone would need to understand to work on this (e.g. "Regex", "Async/await", "CSS Flexbox").
- "difficulty": one of "Easy", "Medium", "Hard".
- "suggested_first_step": one concrete, honest suggestion for where to start looking (e.g. "Start by reading X to understand how Y currently works") — NOT a solution, just a starting point.
- "read_first": a list of docs to read first, typically ["README.md"] and/or ["CONTRIBUTING.md"] if relevant.

Return ONLY valid JSON, no preamble, no markdown fences, in this exact format:
{{"summary": "...", "likely_files": ["..."], "concepts": ["..."], "difficulty": "...", "suggested_first_step": "...", "read_first": ["..."]}}"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 700,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GROQ_API_BASE, headers=_get_headers(), json=payload)
            response.raise_for_status()
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"].strip()

        raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw_text)
    except (httpx.HTTPError, httpx.TimeoutException, json.JSONDecodeError, KeyError):
        return {
            "summary": "Unable to generate a summary for this issue right now.",
            "likely_files": [],
            "concepts": [],
            "difficulty": "Unknown",
            "suggested_first_step": "",
            "read_first": ["README.md"],
        }