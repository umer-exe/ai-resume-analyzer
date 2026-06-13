"use client";

import { useRef, useState } from "react";
import {
  ChevronDown,
  FileText,
  Upload,
  X,
} from "lucide-react";

import {
  API_URL,
  LOADING_ITEMS,
  SAMPLE_PROFILES,
} from "./analyzer-data";
import {
  EmptyState,
  LoadingState,
  ResultsReport,
  SectionLabel,
} from "./report-components";

function wait(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

const MAX_FILE_SIZE = 2 * 1024 * 1024;
const SUPPORTED_FILE_EXTENSIONS = [".pdf", ".docx", ".txt"];

function getFileExtension(filename) {
  const extensionStart = filename.lastIndexOf(".");
  return extensionStart >= 0
    ? filename.slice(extensionStart).toLowerCase()
    : "";
}

function formatFileSize(sizeInBytes) {
  if (sizeInBytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(sizeInBytes / 1024))} KB`;
  }

  return `${(sizeInBytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Home() {
  const [profileText, setProfileText] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [completedStepCount, setCompletedStepCount] = useState(0);
  const [activeTab, setActiveTab] = useState("Overview");
  const fileInputRef = useRef(null);

  function resetReportState() {
    setErrorMessage("");
    setAnalysisResult(null);
    setActiveTab("Overview");
  }

  function clearSelectedFile() {
    setSelectedFile(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function handleSampleProfileChange(event) {
    const selectedProfile = SAMPLE_PROFILES.find(
      (sample) => sample.label === event.target.value,
    );

    if (!selectedProfile) {
      return;
    }

    clearSelectedFile();
    setProfileText(selectedProfile.value);
    resetReportState();
  }

  function handleProfileTextChange(event) {
    clearSelectedFile();
    setProfileText(event.target.value);

    if (errorMessage) {
      setErrorMessage("");
    }
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    const extension = getFileExtension(file.name);

    if (!SUPPORTED_FILE_EXTENSIONS.includes(extension)) {
      clearSelectedFile();
      setErrorMessage("Upload a PDF, DOCX, or TXT file");
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      clearSelectedFile();
      setErrorMessage("Resume file must be 2 MB or smaller");
      return;
    }

    setSelectedFile(file);
    setProfileText("");
    resetReportState();
  }

  function handleRemoveFile() {
    clearSelectedFile();
    resetReportState();
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setErrorMessage("");
    setAnalysisResult(null);
    setActiveTab("Overview");

    const trimmedProfile = profileText.trim();

    if (!trimmedProfile && !selectedFile) {
      setErrorMessage("Profile text or a resume file is required");
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

      if (selectedFile) {
        formData.append("resume_file", selectedFile);
      } else {
        formData.append("profile_text", trimmedProfile);
      }

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
    <main className="min-h-screen bg-[#F3F2EE] px-4 pb-20 pt-10 text-[#17201B] sm:px-6 sm:pt-14">
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

        <section className="mt-10 grid items-start gap-7 lg:grid-cols-[0.82fr_1.18fr]">
          <form
            onSubmit={handleSubmit}
            className="rounded-2xl border border-[#DEDCD5] bg-white p-5 shadow-[0_18px_55px_rgba(43,49,45,0.06)] sm:p-6 lg:sticky lg:top-8"
          >
            <SectionLabel>PROFILE INPUT</SectionLabel>
            <h2 className="mt-2 text-xl font-semibold tracking-tight text-[#111827]">
              Paste your resume or profile
            </h2>

            <div className="mt-5 flex items-center justify-between gap-3">
              <label
                htmlFor="profile-text"
                className="text-xs font-semibold tracking-wide text-[#6B7280]"
              >
                PROFILE TEXT
              </label>
              <div className="relative">
                <select
                  aria-label="Use a sample profile"
                  value=""
                  onChange={handleSampleProfileChange}
                  disabled={isLoading}
                  className="appearance-none rounded-lg border border-[#D8D5CD] bg-[#FAFAF8] py-2 pl-3 pr-8 text-xs font-semibold text-[#166534] outline-none transition hover:border-[#BFC8BE] focus:border-[#166534] focus:ring-2 focus:ring-[#166534]/10 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="">Use sample profile</option>
                  {SAMPLE_PROFILES.map((sample) => (
                    <option key={sample.label} value={sample.label}>
                      {sample.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#166534]" />
              </div>
            </div>
            <textarea
              id="profile-text"
              name="profile_text"
              value={profileText}
              onChange={handleProfileTextChange}
              disabled={isLoading}
              className="mt-2.5 min-h-64 w-full resize-y rounded-xl border border-[#D8D5CD] bg-[#FEFEFD] px-4 py-3 text-sm leading-6 text-[#17201B] outline-none transition placeholder:text-[#9CA3AF] focus:border-[#166534] focus:ring-2 focus:ring-[#166534]/12 disabled:cursor-not-allowed disabled:bg-[#F9FAFB]"
              placeholder="Paste your resume text, profile details, or professional summary here..."
            />

            <div className="my-5 flex items-center gap-3" aria-hidden="true">
              <span className="h-px flex-1 bg-[#E7E4DD]" />
              <span className="text-[11px] font-semibold tracking-[0.16em] text-[#9CA3AF]">
                OR
              </span>
              <span className="h-px flex-1 bg-[#E7E4DD]" />
            </div>

            <div>
              <label
                htmlFor="resume-file"
                className="flex cursor-pointer items-center justify-center gap-2 rounded-xl border border-dashed border-[#CFCBC1] bg-[#FAFAF8] px-4 py-4 text-sm font-semibold text-[#166534] transition hover:border-[#166534]/50 hover:bg-[#F4FAF5]"
              >
                <Upload className="h-4 w-4" />
                Upload resume
              </label>
              <input
                ref={fileInputRef}
                id="resume-file"
                name="resume_file"
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                disabled={isLoading}
                className="sr-only"
              />
              <p className="mt-2 text-center text-xs text-[#6B7280]">
                PDF, DOCX, or TXT up to 2 MB
              </p>
            </div>

            {selectedFile && (
              <div className="mt-3 flex items-center gap-3 rounded-xl border border-[#CDE8D2] bg-[#F4FAF5] px-3 py-3">
                <FileText className="h-4 w-4 shrink-0 text-[#166534]" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-[#17201B]">
                    {selectedFile.name}
                  </p>
                  <p className="mt-0.5 text-xs text-[#6B7280]">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  disabled={isLoading}
                  aria-label="Remove selected resume"
                  className="rounded-lg p-1.5 text-[#6B7280] transition hover:bg-white hover:text-[#111827] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}

            <p className="mt-3 text-xs leading-5 text-[#6B7280]">
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
              className="mt-5 flex w-full items-center justify-center rounded-xl bg-[#166534] px-4 py-3 text-sm font-semibold text-white shadow-[0_8px_22px_rgba(22,101,52,0.18)] transition hover:bg-[#14532D] focus:outline-none focus:ring-2 focus:ring-[#166534] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-65"
            >
              {isLoading ? "Analyzing..." : "Analyze Profile"}
            </button>
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
