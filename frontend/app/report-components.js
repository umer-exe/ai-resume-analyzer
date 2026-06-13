import {
  CheckCircle2,
  ChevronDown,
  CircleAlert,
  CircleX,
  Sparkles,
} from "lucide-react";

import {
  LOADING_ITEMS,
  PRIORITY_STYLES,
  REPORT_INCLUDES,
  REPORT_TABS,
  STATUS_STYLES,
} from "./analyzer-data";

const CHECK_SUMMARIES = [
  {
    key: "passed",
    label: "Passed checks",
    color: "text-[#166534]",
    fill: "bg-[#F4FAF5]",
    icon: CheckCircle2,
  },
  {
    key: "warnings",
    label: "Warnings",
    color: "text-[#B45309]",
    fill: "bg-[#FFFAED]",
    icon: CircleAlert,
  },
  {
    key: "issues",
    label: "Issues",
    color: "text-[#B91C1C]",
    fill: "bg-[#FFF5F4]",
    icon: CircleX,
  },
];

function getTabSlug(tab) {
  return tab.toLowerCase().replace(" ", "-");
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

export function SectionLabel({ children }) {
  return (
    <p className="text-xs font-semibold tracking-[0.18em] text-[#166534]">
      {children}
    </p>
  );
}

export function EmptyState() {
  return (
    <div className="rounded-2xl border border-[#E1DED6] bg-white p-5 shadow-[0_18px_55px_rgba(43,49,45,0.06)] sm:p-7">
      <div className="border-b border-[#EBEBEB] pb-5">
        <SectionLabel>ANALYSIS REPORT</SectionLabel>
        <h2 className="mt-3 text-xl font-semibold tracking-tight text-[#111827]">
          Ready to analyze your resume?
        </h2>
        <p className="mt-2 max-w-lg text-sm leading-6 text-[#6B7280]">
          Paste your resume text or upload a PDF, DOCX, or TXT file to generate
          a structured career-readiness report.
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

export function LoadingState({ completedSteps }) {
  return (
    <div
      className="min-h-[520px] rounded-2xl border border-[#E1DED6] bg-white p-6 shadow-[0_18px_55px_rgba(43,49,45,0.06)]"
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
      <section className="rounded-2xl border border-[#E1DED6] bg-white p-5 shadow-[0_8px_30px_rgba(43,49,45,0.035)]">
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

      <section className="grid grid-cols-3 overflow-hidden rounded-2xl border border-[#E1DED6] bg-white shadow-[0_8px_30px_rgba(43,49,45,0.035)]">
        {CHECK_SUMMARIES.map((item) => {
          const Icon = item.icon;

          return (
            <article
              key={item.label}
              className={`flex min-w-0 items-center gap-2.5 border-r border-[#E7E4DD] px-3 py-3 last:border-r-0 sm:px-4 ${item.fill}`}
            >
              <Icon className={`h-4 w-4 shrink-0 ${item.color}`} />
              <div className="min-w-0">
                <p
                  className={`text-lg font-semibold leading-none ${item.color}`}
                >
                  {checks[item.key] ?? 0}
                </p>
                <p className="mt-1 truncate text-[11px] text-[#6B7280]">
                  {item.label}
                </p>
              </div>
            </article>
          );
        })}
      </section>

      <section className="rounded-2xl border border-[#E1DED6] bg-white p-5 shadow-[0_8px_30px_rgba(43,49,45,0.035)]">
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

      <section className="rounded-2xl border border-[#E1DED6] bg-white p-5 shadow-[0_8px_30px_rgba(43,49,45,0.035)]">
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
  const detectedSkills = Array.isArray(result.skills) ? result.skills : [];

  return (
    <div className="space-y-5">
      <section className="grid gap-3 sm:grid-cols-2">
        {(result.category_analysis ?? []).map((item) => {
          const score = clampPercentage(item.score);

          return (
            <article
              key={item.category}
              className="rounded-2xl border border-[#E1DED6] bg-white p-4 shadow-[0_8px_30px_rgba(43,49,45,0.03)]"
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
              {item.action && (
                <div className="mt-4 border-t border-[#EBEBEB] pt-3">
                  <p className="text-[11px] font-semibold tracking-wide text-[#6B7280]">
                    SUGGESTED ACTION
                  </p>
                  <p className="mt-1.5 text-sm leading-5 text-[#374151]">
                    {item.action}
                  </p>
                </div>
              )}
            </article>
          );
        })}
      </section>

      <details className="group rounded-2xl border border-[#E1DED6] bg-white shadow-[0_8px_30px_rgba(43,49,45,0.03)]">
        <summary className="flex cursor-pointer list-none items-center gap-3 p-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#F1F7F2] text-[#166534]">
            <Sparkles className="h-4 w-4" />
          </div>
          <div className="min-w-0 flex-1">
            <SectionLabel>DETECTED SKILLS</SectionLabel>
            <p className="mt-1 text-sm text-[#6B7280]">
              {detectedSkills.length} technical skill
              {detectedSkills.length === 1 ? "" : "s"} found
            </p>
          </div>
          <ChevronDown className="h-4 w-4 text-[#6B7280] transition-transform group-open:rotate-180" />
        </summary>
        <div className="border-t border-[#EAE7E0] px-5 pb-5 pt-4">
          {detectedSkills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {detectedSkills.map((skill) => (
                <span
                  key={skill}
                  className="rounded-full border border-[#CDE8D2] bg-[#F4FAF5] px-3 py-1.5 text-xs font-medium text-[#166534]"
                >
                  {skill}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[#9CA3AF]">No skills detected</p>
          )}
        </div>
      </details>
    </div>
  );
}

function ActionPlanTab({ result }) {
  const actionPlan = Array.isArray(result.action_plan)
    ? result.action_plan
    : [];

  return (
    <div className="rounded-2xl border border-[#E1DED6] bg-white p-5 shadow-[0_8px_30px_rgba(43,49,45,0.03)]">
      <SectionLabel>ACTION PLAN</SectionLabel>
      <h2 className="mt-2 text-lg font-semibold text-[#111827]">
        Start with these improvements
      </h2>
      <p className="mt-1 text-sm leading-6 text-[#6B7280]">
        The plan is ordered by the weakest areas in your profile analysis.
      </p>

      {actionPlan.length > 0 ? (
        <ol className="mt-5 divide-y divide-[#EBEBEB]">
          {actionPlan.map((item, index) => (
            <li
              key={`${item.category}-${item.action}`}
              className="flex gap-4 py-4 first:pt-0 last:pb-0"
            >
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#F1F7F2] text-xs font-semibold text-[#166534]">
                {index + 1}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-sm font-semibold text-[#111827]">
                    {item.category}
                  </h3>
                  <span
                    className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${
                      PRIORITY_STYLES[item.priority] || PRIORITY_STYLES.Medium
                    }`}
                  >
                    {item.priority || "Medium"}
                  </span>
                </div>
                <p className="mt-1.5 text-sm leading-6 text-[#4B5563]">
                  {item.action}
                </p>
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <p className="mt-5 text-sm text-[#9CA3AF]">
          No action plan items are available.
        </p>
      )}
    </div>
  );
}

export function ResultsReport({ result, activeTab, onTabChange }) {
  const activeTabSlug = getTabSlug(activeTab);

  return (
    <div
      className="min-h-[520px] overflow-hidden rounded-2xl border border-[#DEDCD5] bg-[#FAFAF8] shadow-[0_20px_60px_rgba(43,49,45,0.07)]"
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
