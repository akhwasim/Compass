from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    contributor_profile: str
    experience: str
    languages: list[str]
    frameworks: list[str] = []
    interests: list[str] = []


class RecommendedIssue(BaseModel):
    title: str
    repo: str
    url: str
    confidence: str
    why: str
    why_not: str = ""


class RecommendationResponse(BaseModel):
    count: int
    recommendations: list[RecommendedIssue]