"use client";

import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import {
  Globe, FileText, Download, Sparkles, CheckCircle2,
  XCircle, AlertTriangle, Layers, ShieldAlert, Search,
  ExternalLink, Settings, Save, Mail, TrendingDown,
  ChevronDown, ChevronUp, Copy, Check, RefreshCw,
  BarChart3, Zap, DollarSign, Target, Send, Eye, EyeOff
} from "lucide-react";

const API = "http://localhost:8000";

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
  });
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    axios.get(`${API}/api/settings`).then((res) => {
      if (res.data) setSettings((s) => ({ ...s, ...res.data }));
    }).catch(() => {});
  }, []);

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
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
      <button
        onClick={() => setExpandedSection(expandedSection === id ? null : id)}
        className="w-full flex items-center justify-between p-5 text-left hover:bg-slate-800/40 transition-colors"
      >
        <div className="flex items-center gap-3 font-semibold text-slate-100">{icon}{title}</div>
        {expandedSection === id ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
      </button>
      {expandedSection === id && <div className="px-5 pb-5">{children}</div>}
    </div>
  );

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
              <Settings className="w-4 h-4 text-blue-400" /> Company Settings
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
            <div className="flex items-center gap-3">
              <div className="flex-1 max-w-xs">
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
              <button
                onClick={handleSaveSettings}
                className={`mt-4 flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${settingsSaved ? "bg-emerald-600 text-white" : "bg-blue-600 hover:bg-blue-500 text-white"}`}
              >
                {settingsSaved ? <><Check className="w-3.5 h-3.5" /> Saved!</> : <><Save className="w-3.5 h-3.5" /> Save Settings</>}
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* ─── AUDIT FORM ─── */}
        <div className="bg-gradient-to-br from-slate-900 to-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 mb-8 shadow-2xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100">AI Website Audit Generator</h2>
              <p className="text-xs text-slate-500">Crawl → Gemini Analysis → Branded PDF Report + Sales Email</p>
            </div>
          </div>

          <form onSubmit={handleAudit}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div className="lg:col-span-2">
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Target Website URL *</label>
                <div className="relative">
                  <Globe className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                  <input type="url" value={url} onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://example.com" required
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-colors" />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Client / Company Name</label>
                <input type="text" value={clientName} onChange={(e) => setClientName(e.target.value)}
                  placeholder="Company Name"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-colors" />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Email Tone</label>
                <select value={tone} onChange={(e) => setTone(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500 transition-colors appearance-none cursor-pointer">
                  {TONES.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                {TONES.map((t) => (
                  <button key={t.value} type="button" onClick={() => setTone(t.value)}
                    className={`text-[10px] px-2.5 py-1 rounded-full border transition-all ${tone === t.value ? "bg-blue-600 border-blue-500 text-white" : "border-slate-700 text-slate-500 hover:border-slate-600 hover:text-slate-400"}`}>
                    {t.label}
                  </button>
                ))}
              </div>

              <button type="submit" disabled={loading}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold px-7 py-2.5 rounded-xl shadow-lg shadow-blue-500/25 flex items-center gap-2 disabled:opacity-60 transition-all text-sm cursor-pointer">
                {loading ? (
                  <><RefreshCw className="w-4 h-4 animate-spin" /> Crawling & Analyzing...</>
                ) : (
                  <><FileText className="w-4 h-4" /> Generate Audit Report</>
                )}
              </button>
            </div>
          </form>

          {loading && (
            <div className="mt-4 p-4 rounded-xl bg-blue-500/5 border border-blue-500/20">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse delay-100" />
                <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse delay-200" />
                <span className="text-xs text-blue-400">Crawling website → Sending to Gemini AI → Building PDF report...</span>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-start gap-3">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <div>{error}</div>
            </div>
          )}
        </div>

        {/* ─── RESULTS ─── */}
        {auditData && (
          <div className="space-y-6">
            {/* Top Download + Score Bar */}
            <div className="bg-gradient-to-r from-slate-900 via-blue-950/50 to-slate-900 border border-blue-500/30 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-4 shadow-xl">
              <div className="flex items-center gap-5">
                <ScoreBadge score={auditData.overall_score || "D"} />
                <div>
                  <div className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-1">Audit Complete</div>
                  <h3 className="text-2xl font-bold text-white">{auditData.client_name}</h3>
                  <p className="text-sm text-slate-400 mt-0.5">{auditData.client_url}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {/* Tab Toggle */}
                <div className="flex bg-slate-900 border border-slate-800 rounded-xl p-1 gap-1">
                  {[
                    { key: "audit", label: "Audit", icon: <BarChart3 className="w-3.5 h-3.5" /> },
                    { key: "email", label: "Email", icon: <Mail className="w-3.5 h-3.5" /> },
                  ].map((tab) => (
                    <button key={tab.key} onClick={() => setActiveTab(tab.key as any)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${activeTab === tab.key ? "bg-blue-600 text-white" : "text-slate-400 hover:text-slate-200"}`}>
                      {tab.icon}{tab.label}
                    </button>
                  ))}
                </div>

                <a href={`${API}${report.download_url}`} target="_blank" rel="noreferrer"
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-2.5 rounded-xl shadow-lg shadow-emerald-600/30 flex items-center gap-2 transition-all text-sm">
                  <Download className="w-4 h-4" /> Download PDF
                </a>
              </div>
            </div>

            {/* ── AUDIT TAB ── */}
            {activeTab === "audit" && (
              <div className="space-y-4">
                {/* Stats Row */}
                <div className="grid grid-cols-3 gap-4">
                  {[
                    { label: "Pages Audited", val: auditData.stats?.pages_reviewed || 5, color: "text-blue-400", icon: <Search className="w-4 h-4" /> },
                    { label: "Issues Found", val: auditData.stats?.checklist_failed || 12, color: "text-amber-400", icon: <AlertTriangle className="w-4 h-4" /> },
                    { label: "Critical Bugs", val: auditData.stats?.broken_elements || 6, color: "text-rose-400", icon: <ShieldAlert className="w-4 h-4" /> },
                  ].map((s) => (
                    <div key={s.label} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 text-center">
                      <div className={`flex justify-center mb-2 ${s.color}`}>{s.icon}</div>
                      <div className={`text-4xl font-black ${s.color}`}>{s.val}</div>
                      <div className="text-xs text-slate-500 mt-1">{s.label}</div>
                    </div>
                  ))}
                </div>

                {/* Verdict */}
                <div className="bg-rose-950/20 border border-rose-500/30 rounded-2xl p-5">
                  <div className="flex items-start gap-4">
                    <div className="shrink-0 px-3 py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 font-black text-sm">
                      {auditData.verdict}
                    </div>
                    <p className="text-slate-300 text-sm leading-relaxed">{auditData.verdict_summary}</p>
                  </div>
                </div>

                {/* Business Losses */}
                <SectionToggle id="losses" title="What This Website Is Costing You Right Now" icon={<DollarSign className="w-5 h-5 text-rose-400" />}>
                  <div className="space-y-2 mt-1">
                    {(auditData.business_losses || []).map((loss: string, i: number) => (
                      <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-rose-950/20 border border-rose-500/10">
                        <span className="text-rose-400 font-bold shrink-0 mt-0.5">⚠</span>
                        <span className="text-sm text-slate-200">{loss}</span>
                      </div>
                    ))}
                  </div>
                </SectionToggle>

                {/* Good, Bad, Ugly */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                  {[
                    { key: "the_good", label: "The Good", subtitle: "What to Keep", color: "emerald", icon: <CheckCircle2 className="w-4 h-4" />, items: auditData.the_good },
                    { key: "the_bad", label: "The Bad", subtitle: "Missing Fundamentals", color: "amber", icon: <AlertTriangle className="w-4 h-4" />, items: auditData.the_bad },
                    { key: "the_ugly", label: "The Ugly", subtitle: "Bugs & Broken Elements", color: "rose", icon: <XCircle className="w-4 h-4" />, items: auditData.the_ugly },
                  ].map((section) => (
                    <div key={section.key} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
                      <div className={`flex items-center gap-2 text-${section.color}-400 font-bold mb-3 text-sm`}>
                        {section.icon} {section.label}
                        <span className={`text-[10px] text-${section.color}-500 font-normal`}>— {section.subtitle}</span>
                      </div>
                      <div className="space-y-3">
                        {(section.items || []).map((item: any, idx: number) => (
                          <div key={idx} className="bg-slate-950/60 rounded-xl p-3 border border-slate-800/80">
                            <div className={`text-[10px] font-semibold text-${section.color}-400 mb-1`}>{item.where}</div>
                            <div className="text-xs font-medium text-slate-200">{item.what_found}</div>
                            <div className="text-[10px] text-slate-500 mt-1">{item.why_matters}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Revamp Checklist */}
                <SectionToggle id="checklist" title="Current Site vs. After Revamp Checklist" icon={<Layers className="w-5 h-5 text-blue-400" />}>
                  <div className="divide-y divide-slate-800/60">
                    {(auditData.revamp_checklist || []).map((item: any, idx: number) => (
                      <div key={idx} className="py-2.5 flex items-center justify-between gap-4">
                        <div>
                          <span className="text-[10px] font-bold text-blue-400 mr-2">[{item.category}]</span>
                          <span className="text-xs text-slate-300">{item.item}</span>
                        </div>
                        <div className="flex items-center gap-4 text-[10px] font-bold shrink-0">
                          <span className={item.current ? "text-emerald-400" : "text-rose-400"}>{item.current ? "✓ Pass" : "✗ Fail"}</span>
                          <span className="text-slate-600">→</span>
                          <span className="text-emerald-400">✓ Optimized</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </SectionToggle>

                {/* Page Matrix */}
                <SectionToggle id="matrix" title="Page-by-Page Audit Matrix" icon={<Target className="w-5 h-5 text-violet-400" />}>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-slate-800">
                          {["Page", "Mobile UX", "Clear CTA", "Contact Form", "Trust Signals", "SEO"].map((h) => (
                            <th key={h} className="text-left py-2 pr-4 text-slate-500 font-medium">{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {(auditData.issue_matrix || []).map((row: any, idx: number) => {
                          const cell = (v: string) => {
                            const lower = v?.toLowerCase();
                            if (lower === "pass") return <span className="text-emerald-400 font-bold">✓ Pass</span>;
                            if (lower === "partial") return <span className="text-amber-400 font-bold">~ Partial</span>;
                            return <span className="text-rose-400 font-bold">✗ Fail</span>;
                          };
                          return (
                            <tr key={idx} className="border-b border-slate-800/50">
                              <td className="py-2 pr-4 font-medium text-slate-200">{row.page}</td>
                              <td className="py-2 pr-4">{cell(row.mobile_ux)}</td>
                              <td className="py-2 pr-4">{cell(row.cta_clarity)}</td>
                              <td className="py-2 pr-4">{cell(row.forms)}</td>
                              <td className="py-2 pr-4">{cell(row.trust)}</td>
                              <td className="py-2 pr-4">{cell(row.seo)}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </SectionToggle>

                {/* Cost of Waiting */}
                <SectionToggle id="cost" title="The Cost of Inaction — Risks Growing Every Day" icon={<TrendingDown className="w-5 h-5 text-orange-400" />}>
                  <div className="space-y-3 mt-1">
                    {(auditData.cost_of_waiting || []).map((item: any, idx: number) => {
                      const impactColor = item.impact === "High" ? "rose" : item.impact === "Medium" ? "amber" : "emerald";
                      return (
                        <div key={idx} className="flex gap-3 p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                          <div className={`shrink-0 mt-0.5 px-2 py-0.5 rounded text-[10px] font-bold text-${impactColor}-400 bg-${impactColor}-500/10 border border-${impactColor}-500/20 h-fit`}>
                            {item.impact?.toUpperCase()}
                          </div>
                          <div>
                            <div className="text-sm font-semibold text-slate-200 mb-1">{item.title}</div>
                            <div className="text-xs text-slate-400 leading-relaxed">{item.description}</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </SectionToggle>

                {/* Roadmap */}
                <SectionToggle id="roadmap" title="Recommended 3-Phase Revamp Roadmap" icon={<Zap className="w-5 h-5 text-blue-400" />}>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-1">
                    {(auditData.recommended_scope || []).map((phase: any, idx: number) => (
                      <div key={idx} className="bg-slate-950/60 rounded-xl p-4 border border-slate-800 relative">
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
