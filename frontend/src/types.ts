export type ExperienceLevel = "beginner" | "intermediate" | "advanced";

export interface RecommendationRequest {
  contributor_profile: string;
  experience: string;
  languages: string[];
  frameworks: string[];
  interests: string[];
}

export interface ProfileFormData {
  experience: ExperienceLevel;
  languages: string[];
  frameworks: string[];
  interests: string[];
  available_time: string;
}

export interface ProfileResponse {
  contributor_profile: string;
}

export interface ConfidenceBreakdown {
  skill_overlap: string;
  complexity: string;
  repo_health: string;
  clarity: string;
  final_confidence: string;
}

export interface RecommendedIssue {
  title: string;
  repo: string;
  url: string;
  confidence: string;
  why: string;
  why_not: string;
}

export interface RecommendationResponse {
  count: number;
  recommendations: RecommendedIssue[];
}

export interface IssueExplainerResponse {
  title: string;
  summary: string;
  likely_files: string[];
  concepts: string[];
  difficulty: string;
  suggested_first_step: string;
  read_first: string[];
}