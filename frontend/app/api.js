const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

const ANALYZE_ENDPOINT = "/api/v1/analyze";

export async function analyzeProfile(formData) {
  const response = await fetch(`${API_BASE_URL}${ANALYZE_ENDPOINT}`, {
    method: "POST",
    body: formData,
  });

  let payload;

  try {
    payload = await response.json();
  } catch {
    throw new Error("The analyzer returned an invalid response");
  }

  if (!response.ok || !payload.success) {
    throw new Error(payload.error || "Unable to analyze this profile");
  }

  return payload.data;
}
