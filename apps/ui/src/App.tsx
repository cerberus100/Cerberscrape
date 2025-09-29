import React, { useMemo, useState } from "react";
import { getApiUrl, getS3DownloadUrl } from "./aws-config";

// Minimal, single-file React UI for DataForge.
// Assumes a backend FastAPI with endpoints:
//  - POST /pull/business  { states: string[], naics?: string[], keywords?: string[], limit?: number }
//  - POST /pull/rfps      { states: string[], naics?: string[], keywords?: string[], posted_from?: string, posted_to?: string, limit?: number }
// Both return: { ok: boolean, message?: string, export_path?: string, qa_report?: any }
// Style: Tailwind (no external UI deps required). AWS-ready with S3 integration.

const US_STATES = [
  "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"
];

type Mode = "business" | "rfp";

export default function DataForgeMinimalUI() {
  const [mode, setMode] = useState<Mode>("business");
  const [selectedStates, setSelectedStates] = useState<string[]>([]);
  const [bizType, setBizType] = useState<string>(""); // NAICS or keyword
  const [leadCount, setLeadCount] = useState<number>(500);
  const [keywords, setKeywords] = useState<string>(""); // optional additional filters
  const [dateFrom, setDateFrom] = useState<string>(""); // RFP optional
  const [dateTo, setDateTo] = useState<string>("");   // RFP optional
  const [smallBusinessOnly, setSmallBusinessOnly] = useState<boolean>(false); // Business size filter
  const [businessSize, setBusinessSize] = useState<string>(""); // Specific business size
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resultMsg, setResultMsg] = useState<string>("");
  const [downloadLink, setDownloadLink] = useState<string>("");
  const [qaSummary, setQaSummary] = useState<string>("");

  const apiPath = useMemo(() => getApiUrl(mode === "business" ? "pull/business" : "pull/rfps"), [mode]);

  const toggleState = (s: string) => {
    setSelectedStates(prev => prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]);
  };

  const reset = () => {
    setSelectedStates([]);
    setBizType("");
    setLeadCount(500);
    setKeywords("");
    setDateFrom("");
    setDateTo("");
    setSmallBusinessOnly(false);
    setBusinessSize("");
    setResultMsg("");
    setDownloadLink("");
    setQaSummary("");
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setResultMsg("");
    setDownloadLink("");
    setQaSummary("");

    // Simple validation
    if (selectedStates.length === 0) {
      setIsSubmitting(false);
      setResultMsg("Pick at least one state.");
      return;
    }

    if (!bizType.trim()) {
      setIsSubmitting(false);
      setResultMsg(mode === "business" ? "Enter a business type (NAICS or keyword)." : "Enter a NAICS or keyword for the RFP search.");
      return;
    }

    if (leadCount <= 0) {
      setIsSubmitting(false);
      setResultMsg("Lead count must be greater than zero.");
      return;
    }

    const naics = bizType.split(",").map(s => s.trim()).filter(Boolean).filter(s => /\d{2,6}/.test(s));
    const kw = [bizType, ...keywords.split(",")].map(s => s.trim()).filter(Boolean);

    // Build payloads for each mode
    const payload: Record<string, any> = {
      states: selectedStates,
      limit: leadCount,
    };

    if (naics.length > 0) payload.naics = naics;
    if (kw.length > 0) payload.keywords = kw;

    if (mode === "rfp") {
      if (dateFrom) payload.posted_from = dateFrom;
      if (dateTo) payload.posted_to = dateTo;
    } else {
      // Business mode - add business size filters
      if (smallBusinessOnly) payload.small_business_only = true;
      if (businessSize) payload.business_size = businessSize;
    }

    try {
      const res = await fetch(apiPath, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data?.message || `Request failed (${res.status})`);
      }
      setResultMsg(data.message || "Export ready.");
      if (data.export_path) setDownloadLink(getS3DownloadUrl(data.export_path));
      if (data.qa_report) setQaSummary(summarizeQA(data.qa_report));
    } catch (err: any) {
      setResultMsg(err?.message || "Unexpected error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const summarizeQA = (qa: any) => {
    try {
      const { passed, total_rows, dupes, errors } = qa;
      const errs = Array.isArray(errors) ? errors.slice(0, 3).join("; ") : "";
      return `QA: ${passed ? "PASS" : "FAIL"} • rows=${total_rows ?? "?"} • dupes=${dupes ?? 0}${errs ? " • " + errs : ""}`;
    } catch { return ""; }
  };

  return (
    <div className="min-h-screen w-full bg-gray-50 text-gray-900">
      <div className="max-w-3xl mx-auto p-6">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold">DataForge</h1>
          <p className="text-sm text-gray-600">Pull clean CSV files you can sell. Choose mode, pick states, set business type, and size of batch.</p>
        </header>

        {/* Mode selector */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Mode</label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as Mode)}
            className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="business">Business Data (primary)</option>
            <option value="rfp">RFPs (solicitations)</option>
          </select>
        </div>

        {/* Simple form */}
        <form onSubmit={onSubmit} className="space-y-6 bg-white rounded-2xl shadow-sm p-5">
          {/* States */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium">Pick your states</label>
              <button type="button" onClick={() => setSelectedStates(US_STATES)} className="text-xs text-indigo-600 hover:underline">Select all</button>
            </div>
            <div className="grid grid-cols-6 gap-2 max-h-44 overflow-auto border rounded-xl p-3">
              {US_STATES.map(s => (
                <button
                  key={s}
                  type="button"
                  onClick={() => toggleState(s)}
                  className={`text-sm border rounded-lg px-2 py-1 ${selectedStates.includes(s) ? "bg-indigo-600 text-white border-indigo-600" : "bg-white hover:bg-gray-50"}`}
                >
                  {s}
                </button>
              ))}
            </div>
            <div className="mt-1 text-xs text-gray-500">Selected: {selectedStates.length > 0 ? selectedStates.join(", ") : "none"}</div>
          </div>

          {/* Business type / NAICS */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Business type (NAICS codes or keywords)
            </label>
            <input
              type="text"
              value={bizType}
              onChange={(e) => setBizType(e.target.value)}
              placeholder="e.g., 621111, 541511 or 'telehealth, logistics'"
              className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <p className="text-xs text-gray-500 mt-1">Separate multiple values with commas.</p>
          </div>

          {/* Optional keywords */}
          <div>
            <label className="block text-sm font-medium mb-1">Extra keywords (optional)</label>
            <input
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="e.g., EHR, EMR, wound care"
              className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Lead count / batch size */}
          <div>
            <label className="block text-sm font-medium mb-1">How many leads do you want in this batch?</label>
            <input
              type="number"
              min={1}
              max={2000000}
              value={leadCount}
              onChange={(e) => setLeadCount(parseInt(e.target.value || "0", 10))}
              className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <p className="text-xs text-gray-500 mt-1">We'll pull up to this limit after filters and dedupe.</p>
          </div>

          {/* Business size filters - only show for business mode */}
          {mode === "business" && (
            <div className="space-y-4">
              <div>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={smallBusinessOnly}
                    onChange={(e) => setSmallBusinessOnly(e.target.checked)}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-sm font-medium">Small businesses only</span>
                </label>
                <p className="text-xs text-gray-500 mt-1">Filter for micro and small businesses (≤49 employees)</p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Specific business size (optional)</label>
                <select
                  value={businessSize}
                  onChange={(e) => setBusinessSize(e.target.value)}
                  className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">All sizes</option>
                  <option value="micro">Micro (≤9 employees)</option>
                  <option value="small">Small (10-49 employees)</option>
                  <option value="medium">Medium (50-249 employees)</option>
                  <option value="large">Large (250+ employees)</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">Classify by employee count or revenue</p>
              </div>
            </div>
          )}

          {/* RFP-only fields */}
          {mode === "rfp" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium mb-1">Posted from (YYYY-MM-DD)</label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Posted to (YYYY-MM-DD)</label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center justify-center rounded-2xl bg-indigo-600 px-4 py-2 text-white shadow-sm hover:bg-indigo-700 disabled:opacity-60"
            >
              {isSubmitting ? "Working…" : mode === "business" ? "Pull Business Data" : "Pull RFPs"}
            </button>
            <button
              type="button"
              onClick={reset}
              className="rounded-2xl border border-gray-300 px-4 py-2 bg-white hover:bg-gray-50"
            >
              Reset
            </button>
          </div>

          {/* Result area */}
          {resultMsg && (
            <div className="mt-3 text-sm">
              <div className="font-medium">{resultMsg}</div>
              {downloadLink && (
                <div className="mt-1">
                  <a href={downloadLink} className="text-indigo-600 hover:underline" target="_blank" rel="noreferrer">
                    Download CSV
                  </a>
                </div>
              )}
              {qaSummary && <div className="mt-1 text-gray-600">{qaSummary}</div>}
            </div>
          )}
        </form>

        <footer className="mt-6 text-xs text-gray-500">
          <p>Tip: Business mode is the default. Switch to RFPs from the dropdown when you need solicitations.</p>
        </footer>
      </div>
    </div>
  );
}

export default function App() {
  return <DataForgeMinimalUI />;
}
