"use client";

import { useEffect, useRef } from "react";

const bluePath = [[0.08, 0.88], [0.19, 0.73], [0.32, 0.70], [0.48, 0.53], [0.56, 0.37], [0.72, 0.31]];
const redPath = [[0.91, 0.10], [0.79, 0.25], [0.68, 0.30], [0.55, 0.46], [0.46, 0.59], [0.30, 0.68]];
const wards = [[0.33, 0.62], [0.57, 0.43], [0.73, 0.28], [0.23, 0.75], [0.62, 0.67]];

export function RiftMinimapCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    if (!canvas || !context) return;
    const { width, height } = canvas.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    context.scale(ratio, ratio);
    context.fillStyle = "#0a1119";
    context.fillRect(0, 0, width, height);

    const point = ([x, y]: number[]) => [x * width, y * height] as const;
    context.strokeStyle = "#233342";
    context.lineWidth = 1;
    context.beginPath();
    context.moveTo(width * 0.08, height * 0.9);
    context.lineTo(width * 0.9, height * 0.08);
    context.moveTo(width * 0.1, height * 0.1);
    context.lineTo(width * 0.9, height * 0.9);
    context.stroke();
    context.fillStyle = "#152432";
    context.beginPath();
    context.moveTo(width * 0.06, height * 0.92);
    context.lineTo(width * 0.08, height * 0.76);
    context.lineTo(width * 0.24, height * 0.92);
    context.fill();
    context.beginPath();
    context.moveTo(width * 0.94, height * 0.08);
    context.lineTo(width * 0.92, height * 0.24);
    context.lineTo(width * 0.76, height * 0.08);
    context.fill();

    for (const [path, color] of [[bluePath, "#43b9e8"], [redPath, "#f27b8e"]] as const) {
      context.beginPath();
      path.forEach((coordinates, index) => {
        const [x, y] = point(coordinates);
        if (index === 0) context.moveTo(x, y); else context.lineTo(x, y);
      });
      context.strokeStyle = color;
      context.lineWidth = 2.5;
      context.globalAlpha = 0.85;
      context.stroke();
      path.forEach((coordinates) => {
        const [x, y] = point(coordinates);
        context.beginPath(); context.arc(x, y, 2.4, 0, Math.PI * 2); context.fillStyle = color; context.fill();
      });
    }
    wards.forEach((coordinates) => {
      const [x, y] = point(coordinates);
      const heat = context.createRadialGradient(x, y, 1, x, y, 24);
      heat.addColorStop(0, "rgba(253, 203, 98, .30)"); heat.addColorStop(1, "rgba(253, 203, 98, 0)");
      context.globalAlpha = 1; context.fillStyle = heat; context.fillRect(x - 24, y - 24, 48, 48);
      context.beginPath(); context.arc(x, y, 3, 0, Math.PI * 2); context.fillStyle = "#fcd36e"; context.fill();
    });
    context.globalAlpha = 1;
  }, []);

  return <div className="overflow-hidden rounded-xl border border-line bg-[#0a1119]"><canvas ref={canvasRef} className="block h-[280px] w-full" role="img" aria-label="Summoner's Rift opening jungle routes and pre-objective ward heatmap" /><div className="flex flex-wrap gap-4 border-t border-line px-3 py-2 text-[10px] text-slate-400"><span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-sky-400" />Blue path</span><span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-rose-400" />Red path</span><span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-amber-300" />Ward heat</span></div></div>;
}