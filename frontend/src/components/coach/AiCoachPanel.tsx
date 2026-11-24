"use client";

import { FormEvent, useState } from "react";
import { requestCoachBrief } from "@/lib/api";

export function AiCoachPanel() {
  const [question, setQuestion] = useState("What should we prioritize around the first dragon setup?");
  const [brief, setBrief] = useState("Select an opponent report to generate a prompt grounded in verified scouting metrics. The starter does not call an external LLM.");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    try {
      const result = await requestCoachBrief("Opponent", question);
      setBrief(result.brief);
    } catch (error) {
      setBrief(error instanceof Error ? error.message : "Unable to create the grounded brief. Sign in and upload an opponent report first.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel p-4" aria-label="AI coach">
      <div className="mb-4 flex items-start justify-between"><div><p className="eyebrow">03 / Coaching desk</p><h3 className="mt-1 text-base font-semibold">AI macro coach</h3></div><span className="rounded-md border border-violet-300/20 bg-violet-300/5 px-2 py-1 text-[9px] text-violet-200">GROUNDED MODE</span></div>
      <div className="mb-4 rounded-xl border border-line bg-[#0c1119] p-3"><div className="mb-2 flex items-center justify-between"><p className="eyebrow">Pre-match brief</p><span className="text-[10px] text-slate-600">verified metrics only</span></div><p className="whitespace-pre-wrap text-xs leading-5 text-slate-300">{brief}</p></div>
      <form onSubmit={submit} className="space-y-2">
        <label htmlFor="coach-question" className="eyebrow">Ask your coach</label>
        <textarea id="coach-question" value={question} onChange={(event) => setQuestion(event.target.value)} rows={4} maxLength={1000} className="w-full resize-none rounded-xl border border-line bg-[#0c1119] p-3 text-xs leading-5 text-slate-200 outline-none focus:border-sky-400/50" />
        <button disabled={busy || !question.trim()} className="w-full rounded-xl bg-sky-400 px-4 py-2.5 text-xs font-semibold text-slate-950 transition hover:bg-sky-300 disabled:cursor-wait disabled:opacity-60">{busy ? "Building brief…" : "Generate grounded brief"}</button>
      </form>
      <div className="mt-4 rounded-xl border border-line/70 p-3"><p className="eyebrow">How grounding works</p><p className="mt-1 text-[11px] leading-5 text-slate-500">The API inserts server-aggregated match metrics as the factual source and instructs the model to disclose missing evidence. LLM inference is intentionally not configured.</p></div>
    </section>
  );
}