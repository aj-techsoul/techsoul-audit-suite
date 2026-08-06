"use client";

import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import {
  Globe, FileText, Download, Sparkles, CheckCircle2,
  XCircle, AlertTriangle, Layers, ShieldAlert, Search,
  ExternalLink, Settings, Save, Mail, TrendingDown,
  ChevronDown, ChevronUp, Copy, Check, RefreshCw,
  BarChart3, Zap, DollarSign, Target, Send, Eye, EyeOff,
  Lock, Unlock, KeyRound, ShieldCheck
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const TONES = [
  { value: "Aggressive & Urgent", label: "🔥 Aggressive & Urgent", desc: "High-pressure, compelling action" },
  { value: "Professional & Confident", label: "💼 Professional & Confident", desc: "Authoritative business tone" },
  { value: "Friendly & Consultative", label: "🤝 Friendly & Consultative", desc: "Warm, helpful advisor tone" },
  { value: "Data-Driven & Analytical", label: "📊 Data-Driven & Analytical", desc: "Numbers and facts focused" },
];

export default function Home() {
  const [url, setUrl] = useState("https://completeconsultingcalifornia.com");
  const [clientName, setClientName] = useState("Complete Consulting California");
  const [tone, setTone] = useState("Aggressive & Urgent");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"audit" | "email" | "settings">("audit");
  const [emailBody, setEmailBody] = useState("");
  const [emailSubject, setEmailSubject] = useState("");
  const [emailTo, setEmailTo] = useState("");
  const [copied, setCopied] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [settingsSaved, setSettingsSaved] = useState(false);
  const [expandedSection, setExpandedSection] = useState<string | null>("losses");

  // Passcode Auth State
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [passcodeInput, setPasscodeInput] = useState("");
  const [passcodeError, setPasscodeError] = useState("");
  const [passcodeLoading, setPasscodeLoading] = useState(false);
  const [showPasscodeText, setShowPasscodeText] = useState(false);

  // Settings state
  const [settings, setSettings] = useState({
    user_name: "AJ",
    designation: "Founder",
    company_name: "TECHSOUL",
    full_company: "GrowEagles TechSoul Pvt. Ltd.",
    website_url: "https://techsoul.in",
    email: "mail@techsoul.in",
    phone: "+919862542983",
    linkedin: "",
    gemini_api_key: "",
    passcode: "123456",
  });
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    // Check if session token exists
    const storedAuth = localStorage.getItem("techsoul_auth");
    if (storedAuth === "true") {
      setIsAuthenticated(true);
    }

    axios.get(`${API}/api/settings`).then((res) => {
      if (res.data) setSettings((s) => ({ ...s, ...res.data }));
    }).catch(() => {});
  }, []);

  const handleVerifyPasscode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passcodeInput.trim()) return;
    setPasscodeLoading(true);
    setPasscodeError("");

    try {
      const res = await axios.post(`${API}/api/verify-passcode`, {
        passcode: passcodeInput.trim(),
      });
      if (res.data?.success) {
        setIsAuthenticated(true);
        localStorage.setItem("techsoul_auth", "true");
        setPasscodeInput("");
      } else {
        setPasscodeError("Invalid passcode. Please try again.");
      }
    } catch {
      // Fallback check against settings state if API unreachable
      if (passcodeInput.trim() === (settings.passcode || "123456")) {
        setIsAuthenticated(true);
        localStorage.setItem("techsoul_auth", "true");
        setPasscodeInput("");
      } else {
        setPasscodeError("Invalid passcode. Default is 123456");
      }
    } finally {
      setPasscodeLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("techsoul_auth");
    setIsAuthenticated(false);
  };

  const handleSaveSettings = async () => {
    try {
      await axios.post(`${API}/api/settings`, settings);
      setSettingsSaved(true);
      setTimeout(() => setSettingsSaved(false), 2000);
    } catch {}
  };

  const handleAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    setError("");
    setReport(null);
    setActiveTab("audit");

    try {
      const response = await axios.post(`${API}/api/audit`, {
        url,
        client_name: clientName,
        api_key: settings.gemini_api_key || undefined,
        tone,
      });
      setReport(response.data);
      const email = response.data?.audit_data?.sales_email;
      if (email) {
        setEmailBody(email.email_body || "");
        setEmailSubject(email.subject_line || "");
        setEmailTo(email.recipient_email || "");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to generate report. Check your API key and try again.");
    } finally {
      setLoading(false);
    }
  };

  const copyEmail = () => {
    const full = `To: ${emailTo}\nSubject: ${emailSubject}\n\n${emailBody}`;
    navigator.clipboard.writeText(full);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const auditData = report?.audit_data;

  const ScoreBadge = ({ score }: { score: string }) => {
    const colors: Record<string, string> = {
      A: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10",
      B: "text-lime-400 border-lime-500/40 bg-lime-500/10",
      C: "text-amber-400 border-amber-500/40 bg-amber-500/10",
      D: "text-orange-400 border-orange-500/40 bg-orange-500/10",
      F: "text-rose-400 border-rose-500/40 bg-rose-500/10",
    };
    const key = score?.toString().toUpperCase()[0] || "D";
    return (
      <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl border-2 text-3xl font-black ${colors[key] || colors["D"]}`}>
        {key}
      </div>
    );
  };

  const SectionToggle = ({ id, title, icon, children }: any) => (
    <div className="border border-slate-800 rounded-2xl overflow-hidden bg-slate-900/60 mb-4 transition-all">
      <button
        onClick={() => setExpandedSection(expandedSection === id ? null : id)}
        className="w-full flex items-center justify-between p-5 text-left hover:bg-slate-800/40 transition-colors"
      >
        <div className="flex items-center gap-3 font-bold text-slate-100 text-sm md:text-base">
          {icon}
          {title}
        </div>
        {expandedSection === id ? (
          <ChevronUp className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        )}
      </button>
      {expandedSection === id && (
        <div className="p-5 pt-0 border-t border-slate-800/60">{children}</div>
      )}
    </div>
  );

  // ─── PASSCODE LOCK SCREEN ───
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4 relative overflow-hidden font-sans">
        {/* Background glow effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-blue-600/15 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute bottom-10 right-10 w-[300px] h-[300px] bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none" />

        <div className="w-full max-w-md bg-slate-900/80 border border-slate-800 rounded-3xl p-8 backdrop-blur-xl shadow-2xl relative z-10">
          <div className="flex flex-col items-center text-center mb-8">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20 mb-4">
              <Lock className="w-7 h-7 text-white" />
            </div>
            <img src="/techsoul-logo-white.svg" alt="TechSoul" className="h-6 w-auto mb-2 opacity-90" />
            <h1 className="text-xl font-bold text-slate-100 tracking-tight">TechSoul Audit Suite</h1>
            <p className="text-xs text-slate-400 mt-1">Enter Security Passcode to Access App</p>
          </div>

          <form onSubmit={handleVerifyPasscode} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-2 flex items-center justify-between">
                <span>Passcode</span>
                <span className="text-[10px] text-slate-500 font-normal">Default: 123456</span>
              </label>
              <div className="relative">
                <input
                  type={showPasscodeText ? "text" : "password"}
                  value={passcodeInput}
                  onChange={(e) => setPasscodeInput(e.target.value)}
                  placeholder="Enter passcode..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-4 pr-10 py-3 text-center text-lg tracking-widest text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-all font-mono"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={() => setShowPasscodeText(!showPasscodeText)}
                  className="absolute right-3 top-3.5 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {showPasscodeText ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {passcodeError && (
                <p className="text-xs text-rose-400 mt-2 text-center font-medium flex items-center justify-center gap-1">
                  <XCircle className="w-3.5 h-3.5" /> {passcodeError}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={passcodeLoading}
              className="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-semibold py-3 rounded-xl shadow-lg shadow-blue-500/25 transition-all text-sm flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {passcodeLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" /> Verifying...
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" /> Unlock Application
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-800/80 text-center">
            <p className="text-[11px] text-slate-500">
              Confidential Internal Sales Tool · <a href="https://techsoul.in" target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">TechSoul</a>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* ─── HEADER ─── */}
      <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <img
              src="/techsoul-logo-white.svg"
              alt="TechSoul"
              className="h-7 w-auto object-contain"
            />
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${showSettings ? "bg-blue-600 border-blue-500 text-white" : "border-slate-700 text-slate-400 hover:text-slate-200 hover:border-slate-600"}`}
            >
              <Settings className="w-3.5 h-3.5" /> Settings
            </button>
            <button
              onClick={handleLogout}
              title="Lock App"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/40 transition-all bg-slate-900/50"
            >
              <Lock className="w-3.5 h-3.5" /> Lock
            </button>
            <a href="https://techsoul.in" target="_blank" rel="noreferrer"
              className="text-xs font-medium text-blue-400 hover:text-blue-300 flex items-center gap-1 bg-blue-500/10 px-3 py-1.5 rounded-full border border-blue-500/20">
              techsoul.in <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </header>

      {/* ─── SETTINGS PANEL ─── */}
      {showSettings && (
        <div className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <h2 className="text-sm font-bold text-slate-300 mb-4 flex items-center gap-2">
              <Settings className="w-4 h-4 text-blue-400" /> Company Settings & Security
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
              {[
                { label: "Your Name", key: "user_name", placeholder: "AJ" },
                { label: "Designation", key: "designation", placeholder: "Founder" },
                { label: "Company Name", key: "company_name", placeholder: "TECHSOUL" },
                { label: "Full Company Name", key: "full_company", placeholder: "GrowEagles TechSoul Pvt. Ltd." },
                { label: "Website URL", key: "website_url", placeholder: "https://techsoul.in" },
                { label: "Email", key: "email", placeholder: "mail@techsoul.in" },
                { label: "Phone", key: "phone", placeholder: "+919862542983" },
                { label: "LinkedIn", key: "linkedin", placeholder: "https://linkedin.com/in/yourprofile" },
              ].map(({ label, key, placeholder }) => (
                <div key={key}>
                  <label className="block text-[10px] font-medium text-slate-500 mb-1">{label}</label>
                  <input
                    type="text"
                    value={(settings as any)[key]}
                    onChange={(e) => setSettings((s) => ({ ...s, [key]: e.target.value }))}
                    placeholder={placeholder}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-700 focus:outline-none focus:border-blue-500"
                  />
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
              <div>
                <label className="block text-[10px] font-medium text-slate-500 mb-1">Gemini API Key</label>
                <div className="relative">
                  <input
                    type={showApiKey ? "text" : "password"}
                    value={settings.gemini_api_key}
                    onChange={(e) => setSettings((s) => ({ ...s, gemini_api_key: e.target.value }))}
                    placeholder="Paste your Gemini API key here"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-3 pr-8 py-2 text-xs text-slate-200 placeholder-slate-700 focus:outline-none focus:border-blue-500"
                  />
                  <button onClick={() => setShowApiKey(!showApiKey)} className="absolute right-2 top-2 text-slate-600 hover:text-slate-400">
                    {showApiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-medium text-slate-500 mb-1">App Security Passcode</label>
                <div className="relative">
                  <input
                    type="text"
                    value={settings.passcode || "123456"}
                    onChange={(e) => setSettings((s) => ({ ...s, passcode: e.target.value }))}
                    placeholder="Set passcode (e.g. 123456)"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-700 focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleSaveSettings}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${settingsSaved ? "bg-emerald-600 text-white" : "bg-blue-600 hover:bg-blue-500 text-white"}`}
                >
                  {settingsSaved ? <><Check className="w-3.5 h-3.5" /> Saved!</> : <><Save className="w-3.5 h-3.5" /> Save Settings</>}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* ─── AUDIT FORM ─── */}
        <div className="bg-gradient-to-br from-slate-900 to-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 mb-8 shadow-2xl">
          <div className="flex items-center gap-2 text-xs font-bold text-blue-400 uppercase tracking-widest mb-2">
            <Sparkles className="w-4 h-4" /> AI Website Revenue Audit Engine
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-slate-100 mb-2">
            Generate Audit & Sales Pitch
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mb-6">
            Enter target website URL. Gemini AI will analyze business flaws, quantify losses, and build a modern executive PDF report.
          </p>

          <form onSubmit={handleAudit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Target Website URL</label>
                <div className="relative">
                  <Globe className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://clientwebsite.com"
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-colors"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Client / Business Name</label>
                <input
                  type="text"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="Complete Consulting California"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5">Sales Outreach Tone</label>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
                {TONES.map((t) => (
                  <button
                    key={t.value}
                    type="button"
                    onClick={() => setTone(t.value)}
                    className={`p-3 rounded-xl border text-left transition-all ${tone === t.value ? "bg-blue-600/15 border-blue-500 text-blue-300" : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"}`}
                  >
                    <div className="font-bold text-xs">{t.label}</div>
                    <div className="text-[10px] opacity-75 mt-0.5">{t.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-blue-500/20 transition-all flex items-center justify-center gap-2 text-sm disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" /> Analyzing Website & Generating Report...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" /> Run Audit & Build PDF Report
                </>
              )}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* ─── AUDIT RESULTS ─── */}
        {report && (
          <div className="space-y-6">
            {/* Top Bar Actions */}
            <div className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-2xl p-4">
              <div className="flex items-center gap-3">
                <ScoreBadge score={auditData?.overall_score} />
                <div>
                  <div className="text-xs text-slate-400">Verdict</div>
                  <div className="font-bold text-slate-100 text-base">{auditData?.verdict}</div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setActiveTab("audit")}
                  className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${activeTab === "audit" ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-300 hover:bg-slate-700"}`}
                >
                  <FileText className="w-3.5 h-3.5 inline mr-1" /> Audit Report
                </button>
                <button
                  onClick={() => setActiveTab("email")}
                  className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${activeTab === "email" ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-300 hover:bg-slate-700"}`}
                >
                  <Mail className="w-3.5 h-3.5 inline mr-1" /> Outreach Email
                </button>
                <a
                  href={`${API}${report.pdf_url}`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-lg shadow-emerald-500/20"
                >
                  <Download className="w-3.5 h-3.5" /> Download PDF
                </a>
              </div>
            </div>

            {/* ── AUDIT REPORT TAB ── */}
            {activeTab === "audit" && (
              <div className="space-y-4">
                {/* Executive Summary */}
                <SectionToggle id="summary" title="Executive Summary & Verdict" icon={<ShieldAlert className="w-5 h-5 text-rose-400" />}>
                  <p className="text-sm text-slate-300 leading-relaxed mb-4">{auditData?.verdict_summary}</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                      <div className="text-[10px] text-slate-500 uppercase font-bold">Pages Audited</div>
                      <div className="text-xl font-black text-blue-400">{auditData?.stats?.pages_reviewed}</div>
                    </div>
                    <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                      <div className="text-[10px] text-slate-500 uppercase font-bold">Issues Found</div>
                      <div className="text-xl font-black text-amber-400">{auditData?.stats?.checklist_failed}</div>
                    </div>
                    <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                      <div className="text-[10px] text-slate-500 uppercase font-bold">Critical Bugs</div>
                      <div className="text-xl font-black text-rose-400">{auditData?.stats?.broken_elements}</div>
                    </div>
                  </div>
                </SectionToggle>

                {/* Business Losses */}
                <SectionToggle id="losses" title="Plain English Business Losses" icon={<TrendingDown className="w-5 h-5 text-amber-400" />}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {auditData?.business_losses?.map((loss: string, idx: number) => (
                      <div key={idx} className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl flex items-start gap-3">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center justify-center text-xs font-bold">
                          {idx + 1}
                        </span>
                        <p className="text-xs text-slate-300 leading-relaxed">{loss}</p>
                      </div>
                    ))}
                  </div>
                </SectionToggle>

                {/* Cost of Waiting */}
                <SectionToggle id="cost" title="Cost of Waiting (Financial Impact)" icon={<DollarSign className="w-5 h-5 text-emerald-400" />}>
                  <div className="space-y-3">
                    {auditData?.cost_of_waiting?.map((item: any, idx: number) => (
                      <div key={idx} className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div>
                          <div className="font-bold text-slate-200 text-sm">{item.title}</div>
                          <div className="text-xs text-slate-400 mt-0.5">{item.description}</div>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase border self-start md:self-auto ${item.impact?.toLowerCase() === "high" ? "bg-rose-500/10 text-rose-400 border-rose-500/20" : "bg-amber-500/10 text-amber-400 border-amber-500/20"}`}>
                          {item.impact} Impact
                        </span>
                      </div>
                    ))}
                  </div>
                </SectionToggle>

                {/* Good / Bad / Ugly */}
                <SectionToggle id="gbu" title="Findings Breakdown (Good, Bad & Ugly)" icon={<Layers className="w-5 h-5 text-blue-400" />}>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-emerald-950/20 border border-emerald-800/40 rounded-xl">
                      <h4 className="font-bold text-emerald-400 text-sm mb-3 flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4" /> What's Working</h4>
                      <div className="space-y-2.5">
                        {auditData?.the_good?.map((g: any, i: number) => (
                          <div key={i} className="text-xs bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                            <div className="text-[10px] font-bold text-emerald-400 uppercase mb-0.5">{g.where}</div>
                            <div className="font-semibold text-slate-200">{g.what_found}</div>
                            <div className="text-[11px] text-slate-400 mt-1">{g.why_matters}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="p-4 bg-amber-950/20 border border-amber-800/40 rounded-xl">
                      <h4 className="font-bold text-amber-400 text-sm mb-3 flex items-center gap-1.5"><AlertTriangle className="w-4 h-4" /> What's Missing</h4>
                      <div className="space-y-2.5">
                        {auditData?.the_bad?.map((b: any, i: number) => (
                          <div key={i} className="text-xs bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                            <div className="text-[10px] font-bold text-amber-400 uppercase mb-0.5">{b.where}</div>
                            <div className="font-semibold text-slate-200">{b.what_found}</div>
                            <div className="text-[11px] text-slate-400 mt-1">{b.why_matters}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="p-4 bg-rose-950/20 border border-rose-800/40 rounded-xl">
                      <h4 className="font-bold text-rose-400 text-sm mb-3 flex items-center gap-1.5"><XCircle className="w-4 h-4" /> What's Broken</h4>
                      <div className="space-y-2.5">
                        {auditData?.the_ugly?.map((u: any, i: number) => (
                          <div key={i} className="text-xs bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                            <div className="text-[10px] font-bold text-rose-400 uppercase mb-0.5">{u.where}</div>
                            <div className="font-semibold text-slate-200">{u.what_found}</div>
                            <div className="text-[11px] text-slate-400 mt-1">{u.why_matters}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </SectionToggle>

                {/* Revamp Scope */}
                <SectionToggle id="scope" title="Recommended Revamp Roadmap" icon={<Target className="w-5 h-5 text-purple-400" />}>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {auditData?.recommended_scope?.map((phase: any, idx: number) => (
                      <div key={idx} className="p-5 bg-slate-950 border border-slate-800 rounded-xl relative">
                        <div className="absolute top-3 right-3 w-7 h-7 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-xs font-black text-blue-400">{idx + 1}</div>
                        <div className="text-[10px] font-bold text-blue-400 uppercase tracking-wider mb-1">{phase.timeline}</div>
                        <div className="text-sm font-bold text-slate-100 mb-2">{phase.phase}</div>
                        <p className="text-xs text-slate-400 leading-relaxed">{phase.details}</p>
                      </div>
                    ))}
                  </div>
                </SectionToggle>
              </div>
            )}

            {/* ── EMAIL TAB ── */}
            {activeTab === "email" && (
              <div className="space-y-4">
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-2">
                      <Mail className="w-5 h-5 text-blue-400" />
                      <h3 className="font-bold text-slate-100">Sales Outreach Email</h3>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400">Editable</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-xs text-slate-500">Tone: <span className="text-slate-300 font-medium">{tone}</span></div>
                      <button onClick={copyEmail}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${copied ? "bg-emerald-600 border-emerald-500 text-white" : "border-slate-700 text-slate-400 hover:text-slate-200 hover:border-slate-600"}`}>
                        {copied ? <><Check className="w-3.5 h-3.5" /> Copied!</> : <><Copy className="w-3.5 h-3.5" /> Copy Email</>}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-500 mb-1.5">To (Recipient Email)</label>
                      <input type="email" value={emailTo} onChange={(e) => setEmailTo(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500 transition-colors" />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-500 mb-1.5">Subject Line</label>
                      <input type="text" value={emailSubject} onChange={(e) => setEmailSubject(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500 transition-colors" />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-500 mb-1.5">Email Body</label>
                      <textarea value={emailBody} onChange={(e) => setEmailBody(e.target.value)} rows={18}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-blue-500 transition-colors font-mono leading-relaxed resize-none" />
                    </div>
                  </div>

                  <div className="mt-4 flex items-center gap-3 justify-end">
                    <a href={`mailto:${emailTo}?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`}
                      className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition-all">
                      <Send className="w-4 h-4" /> Open in Email Client
                    </a>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
