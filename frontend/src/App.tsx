import { useState } from "react";
import { ProfileForm } from "./components/ProfileForm";
import { buildProfile, getRecommendations } from "./api/client";
import type { ProfileFormData, RecommendedIssue } from "./types";
import "./App.css";

type ViewState = "form" | "loading-profile" | "loading-recommendations" | "results" | "error";

function App() {
  const [view, setView] = useState<ViewState>("form");
  const [formData, setFormData] = useState<ProfileFormData | null>(null);
  const [contributorProfile, setContributorProfile] = useState<string>("");
  const [recommendations, setRecommendations] = useState<RecommendedIssue[]>([]);
  const [errorMessage, setErrorMessage] = useState<string>("");

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
      setView("results");
    } catch (err) {
      console.error(err);
      setErrorMessage("Something went wrong while finding your matches. Please try again.");
      setView("error");
    }
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
        <h1>🧭 Compass</h1>
        <p>Find the open source issue you can actually solve.</p>
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

      {view === "error" && (
        <div className="error-state">
          <p>{errorMessage}</p>
          <button onClick={handleStartOver}>Try again</button>
        </div>
      )}

      {view === "results" && (
        <div className="results-view">
          <p className="contributor-profile-preview">"{contributorProfile}"</p>
          <button onClick={handleStartOver}>Start over</button>
          <div className="recommendations-list">
            {recommendations.map((rec, idx) => (
              <div key={idx} className="issue-card">
                <div className="issue-card-header">
                  <h3>{rec.title}</h3>
                  <span className={`confidence-badge confidence-${rec.confidence.toLowerCase()}`}>
                    {rec.confidence}
                  </span>
                </div>
                <p className="issue-repo">{rec.repo}</p>
                <p className="issue-why">{rec.why}</p>
                {rec.why_not && <p className="issue-why-not">⚠ {rec.why_not}</p>}
                <a href={rec.url} target="_blank" rel="noopener noreferrer">
                  View on GitHub →
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;