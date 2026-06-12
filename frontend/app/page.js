"use client";

import { useState } from "react";

const API_URL = "http://127.0.0.1:5000/api/v1/analyze";

const analyzerChecks = [
  {
    title: "ATS Compatibility",
    description: "Scores how well your profile would pass automated filters",
  },
  {
    title: "Skill Extraction",
    description: "Identifies technical and soft skills by category",
  },
  {
    title: "Role Matching",
    description: "Finds roles where your profile is strongest",
  },
  {
    title: "Career Roadmap",
    description: "Suggests concrete next steps to improve",
  },
];

function SectionLabel({ children }) {
  return (
    <p className="text-xs font-semibold tracking-[0.18em] text-[#166534]">
      {children}
    </p>
  );
}

function ScoreSummary({ score }) {
  let interpretation =
    "Needs work - focus on structure and keywords.";

  if (score >= 80) {
    interpretation = "Strong profile - well-optimized for ATS.";
  } else if (score >= 60) {
    interpretation =
      "Moderate - some improvements will increase visibility.";
  }

  return (
    <section className="rounded-xl border border-[#E4E2DC] bg-white p-5 shadow-sm sm:p-6">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <SectionLabel>ATS SCORE</SectionLabel>
          <h2 className="mt-2 text-xl font-semibold tracking-tight text-[#111827]">
            Profile compatibility
          </h2>
          <p className="mt-2 text-sm leading-6 text-[#6B7280]">
            {interpretation}
          </p>
        </div>
        <p className="shrink-0 text-3xl font-semibold tracking-tight text-[#166534]">
          {score}{" "}
          <span className="text-base font-medium text-[#6B7280]">/ 100</span>
        </p>
      </div>
      <div
        className="mt-5 h-2.5 overflow-hidden rounded-full bg-[#EBEBEB]"
        role="progressbar"
        aria-label="ATS score"
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow={score}
      >
        <div
          className="h-full rounded-full bg-[#166534]"
          style={{ width: `${Math.min(Math.max(score, 0), 100)}%` }}
        />
      </div>
    </section>
  );
}

function SkillsSection({ skills }) {
  return (
    <section className="mt-10">
      <SectionLabel>SKILLS BY CATEGORY</SectionLabel>
      <div className="mt-3 grid gap-4 sm:grid-cols-2">
        {Object.entries(skills).map(([category, categorySkills]) => (
          <article
            key={category}
            className="rounded-xl border border-[#E4E2DC] bg-white p-5 shadow-sm"
          >
            <h3 className="font-semibold text-[#111827]">{category}</h3>
            {categorySkills.length > 0 ? (
              <div className="mt-4 flex flex-wrap gap-2">
                {categorySkills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-full border border-[#BBF7D0] bg-[#F0FDF4] px-3 py-1 text-sm font-medium text-[#166534]"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-sm text-[#6B7280]">
                No skills detected
              </p>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}

function InsightCard({ label, title, items, tone }) {
  const bulletColor = tone === "positive" ? "bg-[#166534]" : "bg-[#B45309]";

  return (
    <article className="rounded-xl border border-[#E4E2DC] bg-white p-5 shadow-sm sm:p-6">
      <SectionLabel>{label}</SectionLabel>
      <h3 className="mt-2 text-lg font-semibold text-[#111827]">{title}</h3>
      <ul className="mt-5 space-y-3">
        {items.map((item) => (
          <li
            key={item}
            className="flex gap-3 text-sm leading-6 text-[#4B5563]"
          >
            <span
              className={`mt-2.5 h-1.5 w-1.5 shrink-0 rounded-full ${bulletColor}`}
            />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </article>
  );
}

function RoleCard({ role }) {
  const matchColor =
    role.match_percentage >= 70
      ? "bg-[#166534]"
      : role.match_percentage >= 50
        ? "bg-[#D97706]"
        : "bg-[#B91C1C]";

  return (
    <article className="rounded-xl border border-[#E4E2DC] bg-white p-5 shadow-sm sm:p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold text-[#111827]">{role.role}</h3>
          <p className="mt-1 text-sm text-[#6B7280]">
            Based on the skills currently shown in your profile
          </p>
        </div>
        <p className="shrink-0 text-sm font-semibold text-[#111827]">
          {role.match_percentage}% match
        </p>
      </div>

      <div
        className="mt-4 h-1.5 overflow-hidden rounded-full bg-[#EBEBEB]"
        role="progressbar"
        aria-label={`${role.role} match`}
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow={role.match_percentage}
      >
        <div
          className={`h-full rounded-full ${matchColor}`}
          style={{ width: `${role.match_percentage}%` }}
        />
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-xs font-semibold tracking-wide text-[#6B7280]">
            MATCHED SKILLS
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {role.matched_skills.map((skill) => (
              <span
                key={skill}
                className="rounded-full bg-[#F0FDF4] px-2.5 py-1 text-xs font-medium text-[#166534]"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold tracking-wide text-[#6B7280]">
            MISSING SKILLS
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {role.missing_skills.map((skill) => (
              <span
                key={skill}
                className="rounded-full bg-[#FEF2F2] px-2.5 py-1 text-xs font-medium text-[#B91C1C]"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>
    </article>
  );
}

function ResultsDashboard({ result }) {
  return (
    <div className="mt-10" aria-live="polite">
      <div className="mb-4 flex items-center gap-3">
        <div className="h-px flex-1 bg-[#D9D7D1]" />
        <p className="text-xs font-semibold tracking-[0.18em] text-[#6B7280]">
          ANALYSIS REPORT
        </p>
        <div className="h-px flex-1 bg-[#D9D7D1]" />
      </div>

      <ScoreSummary score={result.ats_score} />
      <SkillsSection skills={result.skills} />

      <section className="mt-10 grid gap-4 md:grid-cols-2">
        <InsightCard
          label="STRENGTHS"
          title="What is working"
          items={result.strengths}
          tone="positive"
        />
        <InsightCard
          label="AREAS TO IMPROVE"
          title="What needs attention"
          items={result.weaknesses}
          tone="warning"
        />
      </section>

      <section className="mt-10">
        <SectionLabel>RECOMMENDED CAREER PATHS</SectionLabel>
        <div className="mt-3 space-y-4">
          {result.recommended_roles.map((role) => (
            <RoleCard key={role.role} role={role} />
          ))}
        </div>
      </section>

      <section className="mt-10 rounded-xl border border-[#E4E2DC] bg-white p-5 shadow-sm sm:p-6">
        <SectionLabel>CAREER ROADMAP</SectionLabel>
        <h2 className="mt-2 text-xl font-semibold tracking-tight text-[#111827]">
          Recommended next steps
        </h2>
        <ol className="mt-6">
          {result.career_roadmap.map((step, index) => (
            <li
              key={step}
              className="relative flex gap-4 pb-6 last:pb-0"
            >
              {index < result.career_roadmap.length - 1 && (
                <span className="absolute left-4 top-8 h-full w-px bg-[#E4E2DC]" />
              )}
              <span className="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#D9D7D1] bg-[#F5F4F1] text-xs font-semibold text-[#4B5563]">
                {index + 1}
              </span>
              <p className="pt-1 text-sm leading-6 text-[#374151]">{step}</p>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}

export default function Home() {
  const [profileText, setProfileText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    const trimmedProfile = profileText.trim();

    if (!trimmedProfile) {
      setError("Profile text is required");
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("profile_text", trimmedProfile);

      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });
      const payload = await response.json();

      if (!response.ok || !payload.success) {
        throw new Error(payload.error || "Unable to analyze this profile");
      }

      setResult(payload.data);
    } catch (requestError) {
      setError(
        requestError.message ||
          "Unable to connect to the analyzer. Confirm the backend is running.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#F5F4F1] px-4 pb-20 pt-12 text-[#111827] sm:px-6">
      <div className="mx-auto max-w-5xl">
        <header className="max-w-3xl">
          <SectionLabel>RESUME ANALYZER</SectionLabel>
          <h1 className="mt-3 text-3xl font-semibold tracking-[-0.025em] text-[#111827] sm:text-4xl">
            Resume &amp; Profile Analyzer
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-[#6B7280]">
            Identify skill gaps, match roles, and build a clearer career path.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {["ATS Score", "Skill Gap Analysis", "Role Matching"].map(
              (feature) => (
                <span
                  key={feature}
                  className="rounded-full border border-[#D9D7D1] bg-white px-3 py-1.5 text-xs font-medium text-[#4B5563]"
                >
                  {feature}
                </span>
              ),
            )}
          </div>
        </header>

        <section className="mt-10 grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
          <form
            onSubmit={handleSubmit}
            className="rounded-xl border border-[#E4E2DC] bg-white p-5 shadow-sm sm:p-6"
          >
            <SectionLabel>PROFILE INPUT</SectionLabel>
            <h2 className="mt-2 text-xl font-semibold tracking-tight text-[#111827]">
              Paste your resume or profile
            </h2>
            <label htmlFor="profile-text" className="sr-only">
              Resume or profile text
            </label>
            <textarea
              id="profile-text"
              name="profile_text"
              value={profileText}
              onChange={(event) => setProfileText(event.target.value)}
              disabled={isLoading}
              className="mt-5 min-h-48 w-full resize-y rounded-lg border border-[#D9D7D1] bg-white px-4 py-3 text-sm leading-6 text-[#111827] outline-none transition placeholder:text-[#9CA3AF] focus:border-[#166534] focus:ring-2 focus:ring-[#166534]/15 disabled:cursor-not-allowed disabled:bg-[#F9FAFB]"
              placeholder="Paste your LinkedIn summary, resume text, or a brief professional bio here..."
            />
            <p className="mt-2 text-xs leading-5 text-[#6B7280]">
              Tip: Include your skills, experience, and education for better
              results.
            </p>

            {error && (
              <div
                className="mt-4 rounded-lg border border-[#FECACA] bg-[#FEF2F2] px-4 py-3 text-sm text-[#B91C1C]"
                role="alert"
              >
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="mt-5 flex w-full items-center justify-center rounded-lg bg-[#166534] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#14532D] focus:outline-none focus:ring-2 focus:ring-[#166534] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-65"
            >
              {isLoading ? "Analyzing..." : "Analyze Profile"}
            </button>
          </form>

          <aside className="rounded-xl border border-[#E4E2DC] bg-white p-5 shadow-sm sm:p-6">
            <SectionLabel>WHAT WE CHECK</SectionLabel>
            <h2 className="mt-2 text-xl font-semibold tracking-tight text-[#111827]">
              How the analyzer works
            </h2>
            <div className="mt-5 divide-y divide-[#EBEBEB]">
              {analyzerChecks.map((check) => (
                <div key={check.title} className="flex gap-3 py-4 first:pt-0">
                  <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-[#166534]" />
                  <div>
                    <h3 className="text-sm font-semibold text-[#111827]">
                      {check.title}
                    </h3>
                    <p className="mt-1 text-sm leading-5 text-[#6B7280]">
                      {check.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-2 rounded-lg border border-[#BBF7D0] bg-[#F0FDF4] p-4">
              <p className="text-xs leading-5 text-[#166534]">
                Current response uses dummy data. Rule-based analysis will be
                added in Phase 6.
              </p>
            </div>
          </aside>
        </section>

        {result && <ResultsDashboard result={result} />}
      </div>
    </main>
  );
}
