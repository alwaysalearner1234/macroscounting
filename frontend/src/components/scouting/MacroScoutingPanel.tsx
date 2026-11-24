"use client";

import { RiftMinimapCanvas } from "@/components/scouting/RiftMinimapCanvas";

const metrics = [
  { label: "Gold diff @ 15", value: "+1.8k", detail: "sample scrim set", tone: "text-emerald-300" },
  { label: "First blood", value: "62%", detail: "opponent baseline", tone: "text-sky-300" },
  { label: "First tower", value: "54%", detail: "opponent baseline", tone: "text-sky-300" },
];
const objectives = [
  ["First Dragon", "68%"], ["Voidgrubs", "42%"], ["Rift Herald", "57%"], ["Baron", "31%"],
];

export function MacroScoutingPanel() {
  return (
    <section className="panel p-4" aria-label="Macro scouting">
      <div className="mb-4 flex items-start justify-between"><div><p className="eyebrow">02 / Macro scouting</p><h3 className="mt-1 text-base font-semibold">Opponent tendencies</h3></div><span className="rounded-lg border border-line px-2 py-1 text-[10px] text-slate-400">GRID TELEMETRY</span></div>
      <div className="mb-4 grid grid-cols-3 gap-2">
        {metrics.map((metric) => <article key={metric.label} className="rounded-xl border border-line bg-[#0c1119] p-3"><p className="text-[10px] leading-4 text-slate-500">{metric.label}</p><p className={`mt-1 text-xl font-semibold ${metric.tone}`}>{metric.value}</p><p className="mt-1 text-[9px] text-slate-600">{metric.detail}</p></article>)}
      </div>
      <div className="mb-3"><div className="mb-2 flex items-center justify-between"><p className="eyebrow">First objective capture</p><span className="text-[10px] text-slate-600">rate / games scouted</span></div><div className="grid grid-cols-2 gap-2">
        {objectives.map(([name, value]) => <div key={name} className="flex items-center justify-between rounded-lg border border-line bg-[#0c1119] px-3 py-2"><span className="text-xs text-slate-300">{name}</span><span className="text-xs font-semibold text-sky-300">{value}</span></div>)}
      </div></div>
      <div className="mb-2 flex items-center justify-between"><p className="eyebrow">Opening jungle &amp; vision layer</p><span className="text-[10px] text-slate-600">0:00–5:00 / wards ±60s objective</span></div>
      <RiftMinimapCanvas />
      <p className="mt-2 text-[10px] text-slate-600">Illustrative mock percentages and map marks; connect authenticated telemetry reports for verified values.</p>
    </section>
  );
}