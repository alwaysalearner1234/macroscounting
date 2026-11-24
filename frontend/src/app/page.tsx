"use client";

import { useState } from "react";
import { AiCoachPanel } from "@/components/coach/AiCoachPanel";
import { FearlessDraftBoard } from "@/components/draft/FearlessDraftBoard";
import { MacroScoutingPanel } from "@/components/scouting/MacroScoutingPanel";

const tabs = ["Draft room", "Scouting", "Coach"] as const;
type Tab = (typeof tabs)[number];

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<Tab>("Draft room");

  return (
    <main className="min-h-screen px-4 py-5 text-slate-100 md:px-7">
      <header className="mx-auto mb-5 flex max-w-[1700px] flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-sky-400/40 bg-sky-400/10 font-black text-sky-300">C9</div>
          <div><p className="eyebrow">Cloud9 · Competitive operations</p><h1 className="text-lg font-semibold">Draft &amp; Scout</h1></div>
        </div>
        <nav className="flex rounded-xl border border-line bg-panel p-1" aria-label="Dashboard sections">
          {tabs.map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)} className={`rounded-lg px-4 py-2 text-sm ${activeTab === tab ? "bg-sky-400/15 text-sky-300" : "text-slate-400 hover:text-white"}`}>
              {tab}
            </button>
          ))}
        </nav>
        <div className="flex items-center gap-2 text-xs text-slate-400"><span className="h-2 w-2 rounded-full bg-emerald-400" /> LOCAL WORKSPACE</div>
      </header>

      <div className="mx-auto mb-4 max-w-[1700px]">
        <p className="eyebrow">Pre-match command center / 2025 season</p>
        <h2 className="mt-1 text-2xl font-semibold tracking-tight">Macro edge starts before first pick.</h2>
      </div>

      <section className="mx-auto grid max-w-[1700px] grid-cols-1 items-start gap-4 xl:grid-cols-[minmax(350px,1.05fr)_minmax(420px,1.2fr)_minmax(320px,.9fr)]" aria-label="Draft and scouting dashboard">
        <div className={activeTab === "Draft room" ? "" : "hidden xl:block"}><FearlessDraftBoard /></div>
        <div className={activeTab === "Scouting" ? "" : "hidden xl:block"}><MacroScoutingPanel /></div>
        <div className={activeTab === "Coach" ? "" : "hidden xl:block"}><AiCoachPanel /></div>
      </section>
      <footer className="mx-auto mt-5 flex max-w-[1700px] justify-between text-[11px] text-slate-600"><span>Prototype telemetry · verify opponent reports before use</span><span>GRID-style data · Riot Data Dragon</span></footer>
    </main>
  );
}