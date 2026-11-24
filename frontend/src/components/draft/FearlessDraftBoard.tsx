"use client";

import { useMemo, useState } from "react";

const patch = "14.24.1";
const champions = [
  ["Aatrox", "Aatrox"], ["Ahri", "Ahri"], ["Akali", "Akali"], ["Ashe", "Ashe"],
  ["Azir", "Azir"], ["Braum", "Braum"], ["Caitlyn", "Caitlyn"], ["Elise", "Elise"],
  ["Gnar", "Gnar"], ["Jinx", "Jinx"], ["Jax", "Jax"], ["Kalista", "Kalista"],
  ["Lee Sin", "LeeSin"], ["Maokai", "Maokai"], ["Orianna", "Orianna"], ["Rell", "Rell"],
  ["Renata Glasc", "Renata"], ["Sejuani", "Sejuani"], ["Syndra", "Syndra"], ["Varus", "Varus"],
  ["Annie", "Annie"], ["Bard", "Bard"], ["Camille", "Camille"], ["Cho'Gath", "Chogath"],
  ["Diana", "Diana"], ["Gwen", "Gwen"], ["Irelia", "Irelia"], ["Kennen", "Kennen"],
  ["Lillia", "Lillia"], ["Lulu", "Lulu"],
] as const;
type Side = "Blue" | "Red";
type SlotKind = "ban" | "pick";
type DraftSlot = { champion: string | null; kind: SlotKind };

const createSlots = (): Record<Side, DraftSlot[]> => ({
  Blue: Array.from({ length: 10 }, (_, index) => ({ champion: null, kind: index < 5 ? "ban" : "pick" })),
  Red: Array.from({ length: 10 }, (_, index) => ({ champion: null, kind: index < 5 ? "ban" : "pick" })),
});

export function FearlessDraftBoard() {
  const [format, setFormat] = useState<"Bo3" | "Bo5">("Bo3");
  const [slots, setSlots] = useState<Record<Side, DraftSlot[]>>(createSlots);
  const [selected, setSelected] = useState<string | null>(null);
  const [locked, setLocked] = useState<string[]>([]);
  const [game, setGame] = useState(1);
  const used = useMemo(() => new Set(Object.values(slots).flat().map((slot) => slot.champion).filter(Boolean)), [slots]);

  function assign(side: Side, index: number) {
    const slot = slots[side][index];
    if (!selected || slot.champion || (slot.kind === "pick" && locked.includes(selected))) return;
    setSlots((current) => ({ ...current, [side]: current[side].map((item, slotIndex) => slotIndex === index ? { ...item, champion: selected } : item) }));
    setSelected(null);
  }

  function nextGame() {
    const gamePicks = Object.values(slots).flatMap((sideSlots) => sideSlots.filter((slot) => slot.kind === "pick" && slot.champion).map((slot) => slot.champion as string));
    setLocked((current) => Array.from(new Set([...current, ...gamePicks])));
    setSlots(createSlots());
    setGame((current) => Math.min(current + 1, format === "Bo3" ? 3 : 5));
  }

  return (
    <section className="panel p-4" aria-label="Fearless draft board">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div><p className="eyebrow">01 / Draft room</p><h3 className="mt-1 text-base font-semibold">Hard Fearless Draft</h3></div>
        <label className="flex items-center gap-2 text-xs text-slate-400">Series
          <select value={format} onChange={(event) => { setFormat(event.target.value as "Bo3" | "Bo5"); setGame(1); setSlots(createSlots()); setLocked([]); setSelected(null); }} className="rounded-lg border border-line bg-[#0c1119] px-2 py-1.5 text-slate-200">
            <option>Bo3</option><option>Bo5</option>
          </select>
        </label>
      </div>

      <div className="mb-4 rounded-xl border border-line bg-[#0c1119] p-3">
        <div className="mb-2 flex items-center justify-between"><span className="eyebrow">Series tracker</span><span className="text-xs text-slate-500">Game {game} / {format === "Bo3" ? 3 : 5}</span></div>
        <div className="grid grid-cols-3 items-center text-center"><div><p className="text-[10px] text-sky-300">BLUE SIDE</p><p className="font-semibold">Cloud9</p><p className="text-xs text-slate-500">0 wins</p></div><div className="text-xs font-bold tracking-widest text-slate-600">VS</div><div><p className="text-[10px] text-rose-300">RED SIDE</p><p className="font-semibold">Opponent</p><p className="text-xs text-slate-500">0 wins</p></div></div>
      </div>

      <div className="mb-4 rounded-xl border border-amber-400/20 bg-amber-300/[0.04] p-3">
        <div className="mb-2 flex items-center justify-between"><p className="eyebrow text-amber-200/80">Global lockout · {locked.length} champions</p><span aria-hidden="true">🔒</span></div>
        <div className="flex flex-wrap gap-1.5">{locked.length ? locked.map((champion) => <span key={champion} className="rounded-md border border-amber-200/10 bg-amber-200/5 px-2 py-1 text-[11px] text-amber-100/70">{champion}</span>) : <span className="text-[11px] text-slate-500">No champions locked before game one.</span>}</div>
        <p className="mt-2 text-[10px] text-slate-500">Previously picked champions cannot be selected in later games.</p>
      </div>

      <div className="mb-2 flex items-center justify-between"><p className="eyebrow">Champion pool</p><span className="text-[10px] text-slate-500">Select a portrait, then a slot</span></div>
      <div className="mb-4 grid grid-cols-10 gap-1.5">
        {champions.map(([name, asset]) => {
          const isLocked = locked.includes(name);
          const isUsed = used.has(name);
          return <button key={name} title={`${name}${isLocked ? " — locked" : ""}`} disabled={isLocked || isUsed} onClick={() => setSelected(name)} className={`relative aspect-square overflow-hidden rounded-md border transition ${isLocked || isUsed ? "cursor-not-allowed border-line opacity-25 grayscale" : selected === name ? "border-sky-300 ring-2 ring-sky-300/50" : "border-line hover:border-slate-400"}`}>
            {/* Data Dragon's champion portrait URL is public and version-pinned. */}
            <img src={`https://ddragon.leagueoflegends.com/cdn/${patch}/img/champion/${asset}.png`} alt={name} className="h-full w-full object-cover" />
            {(isLocked || isUsed) && <span className="absolute inset-0 flex items-center justify-center bg-black/50 text-[10px]" aria-label="Locked">🔒</span>}
          </button>;
        })}
      </div>

      <div className="mb-2 flex items-center justify-between"><p className="eyebrow">20-slot pick &amp; ban board</p><button onClick={nextGame} disabled={game >= (format === "Bo3" ? 3 : 5)} className="text-[11px] text-sky-300 hover:text-sky-200 disabled:cursor-not-allowed disabled:opacity-40">Finalize &amp; next →</button></div>
      <div className="grid grid-cols-2 gap-3">
        {(["Blue", "Red"] as const).map((side) => <div key={side} className="rounded-xl border border-line bg-[#0c1119] p-2.5">
          <div className={`mb-2 flex items-center justify-between text-xs font-semibold ${side === "Blue" ? "text-sky-300" : "text-rose-300"}`}><span>{side} side</span><span className="text-[10px] text-slate-600">5 bans / 5 picks</span></div>
          <div className="space-y-1.5">{slots[side].map((slot, index) => <button key={`${side}-${index}`} onClick={() => assign(side, index)} disabled={!selected || Boolean(slot.champion) || (slot.kind === "pick" && Boolean(selected && locked.includes(selected)))} className={`flex w-full items-center gap-2 rounded-md border px-1.5 py-1 text-left text-[10px] ${slot.champion ? "border-line bg-slate-800/50 text-slate-200" : selected && !(slot.kind === "pick" && locked.includes(selected)) ? "border-sky-400/30 bg-sky-400/[0.04] hover:bg-sky-400/10" : "border-line/60 text-slate-600"}`}>
            <span className="flex h-6 w-6 items-center justify-center overflow-hidden rounded bg-slate-800">{slot.champion ? <img src={`https://ddragon.leagueoflegends.com/cdn/${patch}/img/champion/${champions.find(([name]) => name === slot.champion)?.[1] ?? slot.champion}.png`} alt="" className="h-full w-full object-cover" /> : slot.kind === "ban" ? "×" : "＋"}</span>
            <span className="truncate">{slot.champion ?? `${slot.kind === "ban" ? "Ban" : "Pick"} ${index % 5 + 1}`}</span>
            <span className="ml-auto text-[8px] uppercase text-slate-600">{slot.kind}</span>
          </button>)}</div>
        </div>)}
      </div>
    </section>
  );
}