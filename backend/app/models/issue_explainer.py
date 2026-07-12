from pydantic import BaseModel


class IssueExplainerResponse(BaseModel):
    title: str
    summary: str
    likely_files: list[str]
    concepts: list[str]
    difficulty: str
    suggested_first_step: str
    read_first: list[str]