"use client";

import { useState } from "react";

const API_URL = "http://127.0.0.1:5000/api/v1/analyze";

const REPORT_TABS = ["Overview", "Analysis", "Action Plan"];

const LOADING_ITEMS = [
  "Reading profile text",
  "Checking profile structure",
  "Extracting skills",
  "Predicting resume category",
  "Preparing recommendations",
];

const SAMPLE_PROFILE =
  "I am a computer science student with skills in Python, Flask, HTML, CSS, " +
  "SQL, GitHub, and basic AI concepts. I have built academic projects using " +
  "web development and databases. I am interested in software development, " +
  "AI, and data analysis roles.";

const REPORT_INCLUDES = [
  "Profile quality score",
  "Skill category breakdown",
  "ML category prediction",
  "Priority recommendations",
];

const CHECK_SUMMARIES = [
  {
    key: "passed",
    label: "Passed checks",
    color: "text-[#166534]",
    fill: "bg-[#F0FDF4]",
  },
  {
    key: "warnings",
    label: "Warnings",
    color: "text-[#B45309]",
    fill: "bg-[#FFFBEB]",
  },
  {
    key: "issues",
    label: "Issues",
    color: "text-[#B91C1C]",
    fill: "bg-[#FEF2F2]",
  },
];

const STATUS_STYLES = {
  Good: "border-[#BBF7D0] bg-[#F0FDF4] text-[#166534]",
  Warning: "border-[#FDE68A] bg-[#FFFBEB] text-[#B45309]",
  "Needs Work": "border-[#FECACA] bg-[#FEF2F2] text-[#B91C1C]",
  Strong: "border-[#BBF7D0] bg-[#F0FDF4] text-[#166534]",
  Moderate: "border-[#FDE68A] bg-[#FFFBEB] text-[#B45309]",
};

const ACTION_PLAN_SECTIONS = [
  {
    key: "priority",
    label: "Priority Fixes",
    description: "Start with the highest-impact profile improvements.",
    dotClass: "bg-[#B91C1C]",
  },
  {
    key: "skills",
    label: "Skill Improvements",
    description: "Strengthen role-relevant skills and keywords.",
    dotClass: "bg-[#D97706]",
  },
  {
    key: "projects",
    label: "Project Suggestions",
    description: "Improve project evidence and technical presentation.",
    dotClass: "bg-[#166534]",
  },
  {
    key: "profile",
    label: "Resume/Profile Improvements",
    description: "Improve clarity, structure, and professional presentation.",
    dotClass: "bg-[#4B5563]",
  },
];

function getTabSlug(tab) {
  return tab.toLowerCase().replace(" ", "-");
}

function wait(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function clampPercentage(value) {
  const percentage = Number(value);

  if (!Number.isFinite(percentage)) {
    return 0;
  }

  return Math.min(100, Math.max(0, Math.round(percentage)));
}

function formatCategoryLabel(category) {
  return String(category).replaceAll("_", " ");
}

function uniqueItems(items) {
  return [...new Set(items.filter(Boolean))];
}

function includesAny(text, keywords) {
  const normalizedText = text.toLowerCase();
  return keywords.some((keyword) => normalizedText.includes(keyword));
}

function buildActionPlan(result) {
  const recommendations = result.recommendations ?? {};
  const priorityItems = uniqueItems(recommendations.high_priority ?? []);
  const remainingItems = uniqueItems([
    ...(recommendations.medium_priority ?? []),
    ...(recommendations.low_priority ?? []),
    ...(result.next_steps ?? []),
  ]).filter((item) => !priorityItems.includes(item));

  const sections = {
    priority: priorityItems,
    skills: [],
    projects: [],
    profile: [],
  };

  remainingItems.forEach((item) => {
    if (
      includesAny(item, [
        "project",
        "github",
        "portfolio",
        "repository",
      ])
    ) {
      sections.projects.push(item);
    } else if (
      includesAny(item, [
        "skill",
        "keyword",
        "tool",
        "technology",
      ])
    ) {
      sections.skills.push(item);
    } else if (
      includesAny(item, [
        "profile",
        "summary",
        "format",
        "section",
        "sentence",
        "education",
        "experience",
        "qualification",
        "action verb",
        "structure",
      ])
    ) {
      sections.profile.push(item);
    }
  });

  return sections;
}

function SectionLabel({ children }) {
  return (
    <p className="text-xs font-semibold tracking-[0.18em] text-[#166534]">
      {children}
    </p>
  );
}

function EmptyState() {
  return (
    <div className="rounded-xl border border-[#E4E2DC] bg-white p-5 shadow-sm sm:p-6">
      <div className="border-b border-[#EBEBEB] pb-5">
        <SectionLabel>ANALYSIS REPORT</SectionLabel>
        <h2 className="mt-3 text-xl font-semibold tracking-tight text-[#111827]">
          Ready to analyze your resume?
        </h2>
        <p className="mt-2 max-w-lg text-sm leading-6 text-[#6B7280]">
          Paste your resume text, profile details, or professional summary to
          generate a structured career-readiness report.
        </p>
      </div>

      <section className="mt-6">
        <h3 className="text-sm font-semibold text-[#111827]">
          Your report will include
        </h3>
        <ul className="mt-4 space-y-3">
          {REPORT_INCLUDES.map((item) => (
            <li
              key={item}
              className="flex items-center gap-3 text-sm text-[#4B5563]"
            >
              <span className="h-2 w-2 shrink-0 rounded-full bg-[#166534]" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </section>

      <p className="mt-6 border-t border-[#EBEBEB] pt-4 text-center text-xs text-[#9CA3AF]">
        Results will appear here after analysis.
      </p>
    </div>
  );
}

function LoadingState({ completedSteps }) {
  return (
    <div
      className="min-h-[520px] rounded-xl border border-[#E4E2DC] bg-white p-6 shadow-sm"
      aria-live="polite"
    >
      <SectionLabel>ANALYZING PROFILE</SectionLabel>
      <h2 className="mt-3 text-xl font-semibold tracking-tight text-[#111827]">
        Preparing your report
      </h2>
      <p className="mt-2 text-sm leading-6 text-[#6B7280]">
        Reviewing the information you provided.
      </p>

      <div className="mt-8 space-y-3">
        {LOADING_ITEMS.map((item, index) => {
          const isComplete = index < completedSteps;
          const isCurrent = index === completedSteps;

          return (
            <div
              key={item}
              className={`flex items-center gap-3 rounded-lg border px-4 py-3 transition-colors ${
                isComplete
                  ? "border-[#BBF7D0] bg-[#F0FDF4]"
                  : isCurrent
                    ? "border-[#D9D7D1] bg-[#FAFAF9]"
                    : "border-[#EBEBEB] bg-white"
              }`}
            >
              <span
                className={`h-2.5 w-2.5 shrink-0 rounded-full ${
                  isComplete
                    ? "bg-[#166534]"
                    : isCurrent
                      ? "animate-pulse bg-[#D97706]"
                      : "bg-[#D1D5DB]"
                }`}
              />
              <span
                className={`text-sm ${
                  isComplete || isCurrent
                    ? "font-medium text-[#374151]"
                    : "text-[#9CA3AF]"
                }`}
              >
                {item}
              </span>
              <span className="ml-auto text-xs text-[#6B7280]">
                {isComplete ? "Complete" : isCurrent ? "Checking" : "Waiting"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  return (
    <span
      className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${
        STATUS_STYLES[status] || STATUS_STYLES["Needs Work"]
      }`}
    >
      {status}
    </span>
  );
}

function OverviewTab({ result }) {
  const score = clampPercentage(result.score);
  const checks = result.checks ?? {};
  const categoryAnalysis = result.category_analysis ?? [];
  const mlPrediction = result.ml_prediction ?? {};
  const mlCategory =
    mlPrediction.display_category ||
    (mlPrediction.predicted_category
      ? formatCategoryLabel(mlPrediction.predicted_category)
      : "");
  const mlConfidence = clampPercentage(mlPrediction.confidence);
  const topPredictions = mlPrediction.top_predictions ?? [];
  const rankedCategories = [...categoryAnalysis].sort(
    (first, second) =>
      clampPercentage(second.score) - clampPercentage(first.score),
  );
  const strongestAreas = rankedCategories.slice(0, 2);
  const improvementAreas = [...categoryAnalysis]
    .sort(
      (first, second) =>
        clampPercentage(first.score) - clampPercentage(second.score),
    )
    .slice(0, 2);

  return (
    <div className="space-y-5">
      <section className="rounded-xl border border-[#E4E2DC] bg-white p-5">
        <SectionLabel>OVERALL SCORE</SectionLabel>
        <div className="mt-3 flex items-center gap-3">
          <p className="text-4xl font-semibold tracking-tight text-[#111827]">
            {score}
            <span className="text-base font-medium text-[#6B7280]">
              {" "}
              / 100
            </span>
          </p>
          <StatusBadge status={result.status} />
        </div>
        <div
          className="mt-5 h-2 overflow-hidden rounded-full bg-[#EBEBEB]"
          role="progressbar"
          aria-label="Overall profile score"
          aria-valuemin="0"
          aria-valuemax="100"
          aria-valuenow={score}
        >
          <div
            className="h-full rounded-full bg-[#166534]"
            style={{ width: `${score}%` }}
          />
        </div>
      </section>

      <section className="grid grid-cols-3 gap-3">
        {CHECK_SUMMARIES.map((item) => (
          <article
            key={item.label}
            className={`rounded-xl border border-[#E4E2DC] p-4 ${item.fill}`}
          >
            <p className={`text-2xl font-semibold ${item.color}`}>
              {checks[item.key] ?? 0}
            </p>
            <p className="mt-1 text-xs leading-5 text-[#6B7280]">
              {item.label}
            </p>
          </article>
        ))}
      </section>

      <section className="rounded-xl border border-[#E4E2DC] bg-white p-5">
        <SectionLabel>ML CATEGORY PREDICTION</SectionLabel>
        {mlCategory ? (
          <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-base font-semibold text-[#111827]">
                {mlCategory}
              </p>
              <p className="mt-1 text-xs leading-5 text-[#6B7280]">
                Predicted using the trained TF-IDF resume category classifier.
              </p>
            </div>
            <p className="text-sm font-semibold text-[#166534]">
              {mlConfidence}% confidence
            </p>
          </div>
        ) : mlPrediction.message ? (
          <p className="mt-3 text-sm text-[#6B7280]">
            {mlPrediction.message}
          </p>
        ) : (
          <p className="mt-3 text-sm text-[#6B7280]">
            No ML category prediction is available for this report.
          </p>
        )}

        {topPredictions.length > 1 && (
          <div className="mt-4 border-t border-[#EBEBEB] pt-4">
            <p className="text-xs font-semibold tracking-wide text-[#6B7280]">
              TOP CATEGORY MATCHES
            </p>
            <div className="mt-3 space-y-2">
              {topPredictions.slice(0, 3).map((prediction) => (
                <div
                  key={prediction.predicted_category}
                  className="flex items-center justify-between gap-4 text-sm"
                >
                  <span className="text-[#4B5563]">
                    {prediction.display_category ||
                      formatCategoryLabel(prediction.predicted_category)}
                  </span>
                  <span className="font-medium text-[#166534]">
                    {clampPercentage(prediction.confidence)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      <section className="rounded-xl border border-[#E4E2DC] bg-white p-5">
        <SectionLabel>SUMMARY</SectionLabel>
        <p className="mt-3 text-sm leading-6 text-[#4B5563]">
          {result.summary}
        </p>
        <div className="mt-4 grid gap-3 border-t border-[#EBEBEB] pt-4 sm:grid-cols-2">
          <div>
            <p className="text-xs font-semibold tracking-wide text-[#6B7280]">
              STRONGEST PROFILE AREAS
            </p>
            <p className="mt-2 text-sm text-[#374151]">
              {strongestAreas.map((area) => area.category).join(", ") ||
                "Not available"}
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold tracking-wide text-[#6B7280]">
              MAIN IMPROVEMENT AREAS
            </p>
            <p className="mt-2 text-sm text-[#374151]">
              {improvementAreas.map((area) => area.category).join(", ") ||
                "Not available"}
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

function AnalysisTab({ result }) {
  return (
    <div className="space-y-5">
      <section className="grid gap-3 sm:grid-cols-2">
        {(result.category_analysis ?? []).map((item) => {
          const score = clampPercentage(item.score);

          return (
            <article
              key={item.category}
              className="rounded-xl border border-[#E4E2DC] bg-white p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-[#111827]">
                    {item.category}
                  </h3>
                  <p className="mt-1 text-2xl font-semibold text-[#111827]">
                    {score}
                    <span className="text-xs font-medium text-[#6B7280]">
                      {" "}
                      / 100
                    </span>
                  </p>
                </div>
                <StatusBadge status={item.status} />
              </div>
              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-[#EBEBEB]">
                <div
                  className="h-full rounded-full bg-[#166534]"
                  style={{ width: `${score}%` }}
                />
              </div>
              <p className="mt-3 text-sm leading-5 text-[#6B7280]">
                {item.feedback}
              </p>
            </article>
          );
        })}
      </section>

      <section className="rounded-xl border border-[#E4E2DC] bg-white p-5">
        <SectionLabel>DETECTED SKILLS</SectionLabel>
        <div className="mt-4 space-y-4">
          {Object.entries(result.skills ?? {}).map(([category, skills]) => (
            <div key={category}>
              <p className="text-sm font-semibold text-[#374151]">{category}</p>
              {skills.length > 0 ? (
                <div className="mt-2 flex flex-wrap gap-2">
                  {skills.map((skill) => (
                    <span
                      key={skill}
                      className="rounded-full border border-[#BBF7D0] bg-[#F0FDF4] px-2.5 py-1 text-xs font-medium text-[#166534]"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="mt-1 text-xs text-[#9CA3AF]">
                  No skills detected
                </p>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function ActionPlanTab({ result }) {
  const actionPlan = buildActionPlan(result);

  return (
    <div className="space-y-4">
      {ACTION_PLAN_SECTIONS.map((section, index) => (
        <details
          key={section.key}
          open={index === 0}
          className="group rounded-xl border border-[#E4E2DC] bg-white"
        >
          <summary className="flex cursor-pointer list-none items-center gap-3 p-5">
            <span
              className={`h-2.5 w-2.5 shrink-0 rounded-full ${section.dotClass}`}
            />
            <div className="min-w-0 flex-1">
              <h3 className="font-semibold text-[#111827]">{section.label}</h3>
              <p className="mt-1 text-xs leading-5 text-[#6B7280]">
                {section.description}
              </p>
            </div>
            <span className="text-lg text-[#6B7280] transition group-open:rotate-45">
              +
            </span>
          </summary>
          <div className="border-t border-[#EBEBEB] px-5 pb-5">
            {actionPlan[section.key].length > 0 ? (
              <ul className="space-y-3 pt-4">
                {actionPlan[section.key].map((item) => (
                  <li
                    key={item}
                    className="flex gap-3 text-sm leading-6 text-[#4B5563]"
                  >
                    <span className="mt-2.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#9CA3AF]" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="pt-4 text-sm text-[#9CA3AF]">
                No additional items in this section.
              </p>
            )}
          </div>
        </details>
      ))}
    </div>
  );
}

function ResultsReport({ result, activeTab, onTabChange }) {
  const activeTabSlug = getTabSlug(activeTab);

  return (
    <div
      className="min-h-[520px] rounded-xl border border-[#E4E2DC] bg-[#FAFAF9] shadow-sm"
      aria-live="polite"
    >
      <div className="border-b border-[#E4E2DC] bg-white px-5 pt-5 sm:px-6">
        <SectionLabel>PROFILE REPORT</SectionLabel>
        <div
          className="mt-4 flex gap-1 overflow-x-auto"
          role="tablist"
          aria-label="Profile report sections"
        >
          {REPORT_TABS.map((tab) => {
            const tabSlug = getTabSlug(tab);

            return (
              <button
                key={tab}
                id={`tab-${tabSlug}`}
                type="button"
                role="tab"
                aria-selected={activeTab === tab}
                aria-controls={`panel-${tabSlug}`}
                onClick={() => onTabChange(tab)}
                className={`shrink-0 border-b-2 px-3 pb-3 text-sm font-medium transition-colors ${
                  activeTab === tab
                    ? "border-[#166534] text-[#166534]"
                    : "border-transparent text-[#6B7280] hover:text-[#374151]"
                }`}
              >
                {tab}
              </button>
            );
          })}
        </div>
      </div>

      <div
        id={`panel-${activeTabSlug}`}
        role="tabpanel"
        aria-labelledby={`tab-${activeTabSlug}`}
        className="p-4 sm:p-5"
      >
        {activeTab === "Overview" && <OverviewTab result={result} />}
        {activeTab === "Analysis" && <AnalysisTab result={result} />}
        {activeTab === "Action Plan" && <ActionPlanTab result={result} />}
      </div>
    </div>
  );
}

export default function Home() {
  const [profileText, setProfileText] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [completedStepCount, setCompletedStepCount] = useState(0);
  const [activeTab, setActiveTab] = useState("Overview");

  function handleUseSampleProfile() {
    setProfileText(SAMPLE_PROFILE);
    setErrorMessage("");
    setAnalysisResult(null);
    setActiveTab("Overview");
  }

  function handleProfileTextChange(event) {
    setProfileText(event.target.value);

    if (errorMessage) {
      setErrorMessage("");
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setErrorMessage("");
    setAnalysisResult(null);
    setActiveTab("Overview");

    const trimmedProfile = profileText.trim();

    if (!trimmedProfile) {
      setErrorMessage("Profile text is required");
      return;
    }

    setIsLoading(true);
    setCompletedStepCount(0);

    const checklistTimer = window.setInterval(() => {
      setCompletedStepCount((current) =>
        Math.min(current + 1, LOADING_ITEMS.length),
      );
    }, 250);

    try {
      const formData = new FormData();
      formData.append("profile_text", trimmedProfile);

      const [response] = await Promise.all([
        fetch(API_URL, {
          method: "POST",
          body: formData,
        }),
        wait(1500),
      ]);
      const payload = await response.json();

      if (!response.ok || !payload.success) {
        throw new Error(payload.error || "Unable to analyze this profile");
      }

      setAnalysisResult(payload.data);
    } catch (requestError) {
      setErrorMessage(
        (requestError instanceof Error && requestError.message) ||
          "Unable to connect to the analyzer. Confirm the backend is running.",
      );
    } finally {
      window.clearInterval(checklistTimer);
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#F5F4F1] px-4 pb-20 pt-10 text-[#111827] sm:px-6 sm:pt-12">
      <div className="mx-auto max-w-6xl">
        <header className="max-w-3xl">
          <SectionLabel>RESUME ANALYZER</SectionLabel>
          <h1 className="mt-3 text-3xl font-semibold tracking-[-0.025em] text-[#111827] sm:text-4xl">
            Resume &amp; Profile Analyzer
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-[#6B7280]">
            Identify skill gaps, review profile quality, and build a clearer
            career path.
          </p>
        </header>

        <section className="mt-9 grid items-start gap-6 lg:grid-cols-[0.82fr_1.18fr]">
          <form
            onSubmit={handleSubmit}
            className="rounded-xl border border-[#E4E2DC] bg-white p-5 shadow-sm sm:p-6 lg:sticky lg:top-8"
          >
            <SectionLabel>PROFILE INPUT</SectionLabel>
            <h2 className="mt-2 text-xl font-semibold tracking-tight text-[#111827]">
              Paste your resume or profile
            </h2>
            <p className="mt-2 text-sm leading-6 text-[#6B7280]">
              Use resume text, profile details, or a professional summary.
            </p>

            <div className="mt-5 flex items-center justify-between gap-3">
              <label
                htmlFor="profile-text"
                className="text-xs font-semibold tracking-wide text-[#6B7280]"
              >
                PROFILE TEXT
              </label>
              <button
                type="button"
                onClick={handleUseSampleProfile}
                disabled={isLoading}
                className="text-xs font-semibold text-[#166534] underline decoration-[#BBF7D0] underline-offset-4 transition hover:text-[#14532D] disabled:cursor-not-allowed disabled:opacity-50"
              >
                Use sample profile
              </button>
            </div>
            <textarea
              id="profile-text"
              name="profile_text"
              value={profileText}
              onChange={handleProfileTextChange}
              disabled={isLoading}
              className="mt-2.5 min-h-64 w-full resize-y rounded-lg border border-[#D9D7D1] bg-white px-4 py-3 text-sm leading-6 text-[#111827] outline-none transition placeholder:text-[#9CA3AF] focus:border-[#166534] focus:ring-2 focus:ring-[#166534]/15 disabled:cursor-not-allowed disabled:bg-[#F9FAFB]"
              placeholder="Paste your resume text, profile details, or professional summary here..."
            />
            <p className="mt-2 text-xs leading-5 text-[#6B7280]">
              Tip: Include your skills, experience, education, and projects.
            </p>

            {errorMessage && (
              <div
                className="mt-4 rounded-lg border border-[#FECACA] bg-[#FEF2F2] px-4 py-3 text-sm text-[#B91C1C]"
                role="alert"
              >
                {errorMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="mt-5 flex w-full items-center justify-center rounded-lg bg-[#166534] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#14532D] focus:outline-none focus:ring-2 focus:ring-[#166534] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-65"
            >
              {isLoading ? "Analyzing..." : "Analyze Profile"}
            </button>
            <p className="mt-3 text-center text-xs text-[#9CA3AF]">
              Rule-based analysis with optional ML category prediction. This is
              not live job matching.
            </p>
          </form>

          <div>
            {isLoading ? (
              <LoadingState completedSteps={completedStepCount} />
            ) : analysisResult ? (
              <ResultsReport
                result={analysisResult}
                activeTab={activeTab}
                onTabChange={setActiveTab}
              />
            ) : (
              <EmptyState />
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
