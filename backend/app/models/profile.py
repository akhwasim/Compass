from pydantic import BaseModel
from typing import Literal


class ProfileRequest(BaseModel):
    experience: Literal["beginner", "intermediate", "advanced"]
    languages: list[str]
    frameworks: list[str] = []
    interests: list[str] = []
    available_time: str = ""  # e.g. "1 hour", "2 hours", "weekend"


class ProfileResponse(BaseModel):
    contributor_profile: str