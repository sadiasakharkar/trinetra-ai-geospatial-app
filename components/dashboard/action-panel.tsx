"use client"

import { Play, Pause, ClipboardCheck, Download } from "lucide-react"

export function ActionPanel({
  running,
  progress,
  onStart,
  onPause,
}: {
  running: boolean
  progress: number
  onStart: () => void
  onPause: () => void
}) {
  const done = progress >= 100

  return (
    <div className="fixed bottom-5 right-4 z-40 md:right-6">
      <div className="glass-strong flex flex-col gap-2 rounded-2xl border border-border p-2.5 shadow-2xl shadow-black/40">
        <button
          onClick={onStart}
          disabled={running}
          className="flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Play className="size-4" />
          {done ? "Re-run" : "Start Reconstruction"}
        </button>
        <button
          onClick={onPause}
          disabled={!running}
          className="flex items-center gap-2 rounded-xl border border-border bg-secondary/40 px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-secondary disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Pause className="size-4" />
          Pause Job
        </button>
        <button className="flex items-center gap-2 rounded-xl border border-border bg-secondary/40 px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-secondary">
          <ClipboardCheck className="size-4 text-chart-3" />
          View Validation
        </button>
        <button className="flex items-center gap-2 rounded-xl border border-border bg-secondary/40 px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-secondary">
          <Download className="size-4 text-primary" />
          Export Results
        </button>
      </div>
    </div>
  )
}
