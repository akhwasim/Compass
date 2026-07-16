import { useState } from "react";
import { ChipMultiSelect } from "./ChipMultiSelect";
import type { ProfileFormData, ExperienceLevel } from "../types";

const LANGUAGE_OPTIONS = ["Python", "JavaScript", "TypeScript", "Rust", "Java", "Go", "C++", "PHP"];
const FRAMEWORK_OPTIONS = ["React", "FastAPI", "Django", "Spring", "Express", "Next.js", "Flask", "Vue"];
const INTEREST_OPTIONS = ["AI", "Backend", "Frontend", "DevOps", "Security"];
const TIME_OPTIONS = ["1 hour", "2 hours", "Weekend"];

interface ProfileFormProps {
  onSubmit: (data: ProfileFormData) => void;
  isLoading: boolean;
}

export function ProfileForm({ onSubmit, isLoading }: ProfileFormProps) {
  const [experience, setExperience] = useState<ExperienceLevel>("beginner");
  const [languages, setLanguages] = useState<string[]>([]);
  const [frameworks, setFrameworks] = useState<string[]>([]);
  const [interests, setInterests] = useState<string[]>([]);
  const [availableTime, setAvailableTime] = useState<string>("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (languages.length === 0) {
      alert("Please select or add at least one language.");
      return;
    }
    onSubmit({
      experience,
      languages,
      frameworks,
      interests,
      available_time: availableTime,
    });
  }

  return (
    <form className="profile-form" onSubmit={handleSubmit}>
      <h2>Tell us who you are</h2>
      <p className="profile-form-subtitle">
        A few details on your skills and interests - Compass uses these to find issues you're actually equipped to solve.
      </p>

      <div className="form-section">
        <label><span className="step-num">01</span> Experience</label>
        <div className="experience-options">
          {(["beginner", "intermediate", "advanced"] as ExperienceLevel[]).map((level) => (
            <button
              type="button"
              key={level}
              className={`chip ${experience === level ? "chip-selected" : ""}`}
              onClick={() => setExperience(level)}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="form-section">
        <label><span className="step-num">02</span> Languages</label>
        <ChipMultiSelect
          options={LANGUAGE_OPTIONS}
          selected={languages}
          onChange={setLanguages}
          allowCustom
          placeholder="Add another language..."
        />
      </div>

      <div className="form-section">
        <label><span className="step-num">03</span> Frameworks</label>
        <ChipMultiSelect
          options={FRAMEWORK_OPTIONS}
          selected={frameworks}
          onChange={setFrameworks}
          allowCustom
          placeholder="Add another framework..."
        />
      </div>

      <div className="form-section">
        <label><span className="step-num">04</span> Interested In</label>
        <ChipMultiSelect
          options={INTEREST_OPTIONS}
          selected={interests}
          onChange={setInterests}
        />
      </div>

      <div className="form-section">
        <label><span className="step-num">05</span> Available Time</label>
        <div className="time-options">
          {TIME_OPTIONS.map((time) => (
            <button
              type="button"
              key={time}
              className={`chip ${availableTime === time ? "chip-selected" : ""}`}
              onClick={() => setAvailableTime(time)}
            >
              {time}
            </button>
          ))}
        </div>
      </div>

      <button type="submit" className="submit-btn" disabled={isLoading}>
        {isLoading ? "Finding your match..." : "Find my contribution"}
      </button>
    </form>
  );
}