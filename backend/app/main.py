from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.github_service import (
    get_authenticated_user,
    search_issues,
    get_repo_metadata,
    get_issue_details,
    get_readme,
    get_folder_structure,
)
from app.services.confidence_service import calculate_baseline_confidence
from app.services.groq_service import (
    generate_contributor_profile,
    rank_issues_with_reasoning,
    explain_issue,
)

from app.models.profile import ProfileRequest, ProfileResponse
from app.models.recommendation import RecommendationRequest, RecommendationResponse, RecommendedIssue
from app.models.issue_explainer import IssueExplainerResponse

app = FastAPI(title="Open Source Contribution Matcher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/profile", response_model=ProfileResponse)
async def build_profile(request: ProfileRequest):
    profile_text = await generate_contributor_profile(
        experience=request.experience,
        languages=request.languages,
        frameworks=request.frameworks,
        interests=request.interests,
        available_time=request.available_time,
    )
    return ProfileResponse(contributor_profile=profile_text)




@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    all_candidates = []

    for language in request.languages:
        issues = await search_issues(language=language, max_results=10)

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
                    "user_languages": request.languages,
                    "user_frameworks": request.frameworks,
                }

                confidence = calculate_baseline_confidence(issue_data)

                all_candidates.append({
                    "title": issue["title"],
                    "repo": repo_full_name,
                    "url": issue["html_url"],
                    "body_snippet": issue.get("body") or "",
                    "confidence": confidence,
                })

    if not all_candidates:
        return RecommendationResponse(count=0, recommendations=[])

    ranked = await rank_issues_with_reasoning(request.contributor_profile, all_candidates, request.interests)
    top_results = ranked[:10]

    return RecommendationResponse(
        count=len(top_results),
        recommendations=[
            RecommendedIssue(
                title=r["title"],
                repo=r["repo"],
                url=r["url"],
                confidence=r["confidence"]["final_confidence"],
                why=r["why"],
                why_not=r["why_not"],
            )
            for r in top_results
        ],
    )


@app.get("/issue/{owner}/{repo}/{issue_number}", response_model=IssueExplainerResponse)
async def get_issue_explainer(owner: str, repo: str, issue_number: int):
    issue = await get_issue_details(owner, repo, issue_number)
    readme = await get_readme(owner, repo)
    folder_structure = await get_folder_structure(owner, repo)

    explanation = await explain_issue(
        issue_title=issue["title"],
        issue_body=issue["body"],
        readme_text=readme,
        folder_structure=folder_structure,
    )

    return IssueExplainerResponse(
        title=issue["title"],
        summary=explanation.get("summary", ""),
        likely_files=explanation.get("likely_files", []),
        concepts=explanation.get("concepts", []),
        difficulty=explanation.get("difficulty", "Unknown"),
        suggested_first_step=explanation.get("suggested_first_step", ""),
        read_first=explanation.get("read_first", []),
    )