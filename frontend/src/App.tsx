import { useState } from "react";
import { ProfileForm } from "./components/ProfileForm";
import { buildProfile, getRecommendations, getIssueExplainer } from "./api/client";
import type { ProfileFormData, RecommendedIssue, IssueExplainerResponse } from "./types";
import { ConfidenceIndicator } from "./components/ConfidenceIndicator";
import "./App.css";

type ViewState = "form" | "loading-profile" | "loading-recommendations" | "results" | "no-results" | "error";

function App() {
  const [view, setView] = useState<ViewState>("form");
  const [formData, setFormData] = useState<ProfileFormData | null>(null);
  const [contributorProfile, setContributorProfile] = useState<string>("");
  const [recommendations, setRecommendations] = useState<RecommendedIssue[]>([]);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [selectedExplainer, setSelectedExplainer] = useState<IssueExplainerResponse | null>(null);
  const [explainerLoading, setExplainerLoading] = useState(false);
  const [explainerError, setExplainerError] = useState<string>("");

  async function handleFormSubmit(data: ProfileFormData) {
    setFormData(data);
    setView("loading-profile");
    setErrorMessage("");

    try {
      const profileResult = await buildProfile(data);
      setContributorProfile(profileResult.contributor_profile);

      setView("loading-recommendations");
      const recsResult = await getRecommendations({
        contributor_profile: profileResult.contributor_profile,
        experience: data.experience,
        languages: data.languages,
        frameworks: data.frameworks,
        interests: data.interests,
      });
      setRecommendations(recsResult.recommendations);
      setView(recsResult.count === 0 ? "no-results" : "results");
    } catch (err) {
      console.error(err);
      setErrorMessage("Something went wrong while finding your matches. Please try again.");
      setView("error");
    }
  }

  function parseIssueUrl(url: string): { owner: string; repo: string; issueNumber: number } | null {
    const match = url.match(/github\.com\/([^/]+)\/([^/]+)\/issues\/(\d+)/);
    if (!match) return null;
    return { owner: match[1], repo: match[2], issueNumber: parseInt(match[3], 10) };
  }

  async function handleIssueClick(rec: RecommendedIssue) {
    const parsed = parseIssueUrl(rec.url);
    if (!parsed) {
      setExplainerError("Couldn't parse this issue's URL.");
      return;
    }
    setExplainerLoading(true);
    setExplainerError("");
    setSelectedExplainer(null);
    try {
      const explainer = await getIssueExplainer(parsed.owner, parsed.repo, parsed.issueNumber);
      setSelectedExplainer(explainer);
    } catch (err) {
      console.error(err);
      setExplainerError("Couldn't load details for this issue. Please try again.");
    } finally {
      setExplainerLoading(false);
    }
  }

  function closeExplainer() {
    setSelectedExplainer(null);
    setExplainerError("");
  }

  function handleStartOver() {
    setView("form");
    setFormData(null);
    setContributorProfile("");
    setRecommendations([]);
    setErrorMessage("");
  }

  return (
    <div className="app-container">
      <header>
        <p className="header-eyebrow">Open source navigation</p>
        <div className="header-main">
          <svg className="compass-mark" viewBox="0 0 36 36" fill="none">
            <circle cx="18" cy="18" r="16" stroke="#C9A227" strokeWidth="1.5" />
            <path d="M18 8 L21 18 L18 28 L15 18 Z" fill="#C9A227" />
            <circle cx="18" cy="18" r="2" fill="#10161F" stroke="#C9A227" strokeWidth="1" />
          </svg>
          <h1>Compass</h1>
        </div>
        <p className="header-tagline">
          Tell us who you are. We'll chart the issue you can actually solve - and explain why.
        </p>
      </header>

      {view === "form" && (
        <ProfileForm onSubmit={handleFormSubmit} isLoading={false} />
      )}

      {view === "loading-profile" && (
        <div className="loading-state">
          <p>Understanding your profile...</p>
        </div>
      )}

      {view === "loading-recommendations" && (
        <div className="loading-state">
          {contributorProfile && (
            <p className="contributor-profile-preview">"{contributorProfile}"</p>
          )}
          <p>Searching GitHub for your best matches...</p>
        </div>
      )}

      {view === "no-results" && (
        <div className="error-state">
          <p>No matching issues found for this combination. Try adding another language or loosening your interests.</p>
          <button onClick={handleStartOver}>Adjust my profile</button>
        </div>
      )}

      {view === "results" && (
        <div className="results-view">
          <p className="contributor-profile-preview">"{contributorProfile}"</p>
          <button onClick={handleStartOver}>Start over</button>
          {!selectedExplainer && !explainerLoading && (
            <div className="recommendations-list">
              {recommendations.map((rec, idx) => (
                <div key={idx} className="issue-card">
                  <div className="issue-card-header">
                    <h3>{rec.title}</h3>
                    <ConfidenceIndicator level={rec.confidence} />
                  </div>
                  <p className="issue-repo">{rec.repo}</p>
                  <p className="issue-why">{rec.why}</p>
                  {rec.why_not && <p className="issue-why-not">⚠ {rec.why_not}</p>}
                  <div className="issue-card-actions">
                    <button onClick={() => handleIssueClick(rec)}>Understand this issue</button>
                    <a href={rec.url} target="_blank" rel="noopener noreferrer">
                      View on GitHub →
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}

          {explainerLoading && (
            <div className="loading-state">
              <p>Reading the issue and repo...</p>
            </div>
          )}

          {explainerError && <p className="error-state">{explainerError}</p>}

          {selectedExplainer && (
            <div className="issue-explainer">
              <button onClick={closeExplainer}>← Back to list</button>
              <h2>{selectedExplainer.title}</h2>
              <p>{selectedExplainer.summary}</p>

              <h4>Likely files</h4>
              <ul>
                {selectedExplainer.likely_files.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>

              <h4>Concepts you'll need</h4>
              <ul>
                {selectedExplainer.concepts.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>

              <p><strong>Difficulty:</strong> {selectedExplainer.difficulty}</p>
              <p><strong>Suggested first step:</strong> {selectedExplainer.suggested_first_step}</p>

              <h4>Read first</h4>
              <ul>
                {selectedExplainer.read_first.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;