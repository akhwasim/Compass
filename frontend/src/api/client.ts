import type {
  ProfileFormData,
  ProfileResponse,
  RecommendationRequest,
  RecommendationResponse,
  IssueExplainerResponse,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function buildProfile(data: ProfileFormData): Promise<ProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Profile request failed: ${response.status}`);
  }
  return response.json();
}

export async function getRecommendations(
  data: RecommendationRequest
): Promise<RecommendationResponse> {
  const response = await fetch(`${API_BASE_URL}/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Recommendations request failed: ${response.status}`);
  }
  return response.json();
}

export async function getIssueExplainer(
  owner: string,
  repo: string,
  issueNumber: number
): Promise<IssueExplainerResponse> {
  const response = await fetch(
    `${API_BASE_URL}/issue/${owner}/${repo}/${issueNumber}`
  );
  if (!response.ok) {
    throw new Error(`Issue explainer request failed: ${response.status}`);
  }
  return response.json();
}