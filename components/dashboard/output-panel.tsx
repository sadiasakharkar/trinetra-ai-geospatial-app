"use client"

import { useState } from "react"
import Image from "next/image"
import {
  Sparkles,
  SplitSquareHorizontal,
  Layers2,
  Loader2,
  CheckCircle2,
} from "lucide-react"
import { Panel, Badge, MetricCard } from "./ui"

export function OutputPanel({
  running,
  progress,
}: {
  running: boolean
  progress: number
}) {
  const [compare, setCompare] = useState(false)
  const [showConfidence, setShowConfidence] = useState(false)
  const [split, setSplit] = useState(50)

  const done = progress >= 100

  return (
    <Panel
      title="Reconstructed Cloud-Free Scene"
      icon={<Sparkles className="size-4 text-primary" aria-hidden="true" />}
      badge={
        done ? (
          <Badge tone="green" dot>
            Complete
          </Badge>
        ) : (
          <Badge tone="primary" dot>
            {running ? "Processing" : "Ready"}
          </Badge>
        )
      }
    >
      {/* Viewer */}
      <div className="relative aspect-square w-full overflow-hidden rounded-lg border border-border bg-black/40">
        <Image
          src="/images/liss-iv-reconstructed.png"
          alt="AI reconstructed cloud-free LISS-IV scene"
          fill
          sizes="(max-width: 1024px) 100vw, 33vw"
          className="object-cover"
        />

        {/* Before/after overlay */}
        {compare ? (
          <>
            <div
              className="absolute inset-0 overflow-hidden"
              style={{ clipPath: `inset(0 ${100 - split}% 0 0)` }}
            >
              <Image
                src="/images/liss-iv-cloudy.png"
                alt="Original cloudy scene for comparison"
                fill
                sizes="(max-width: 1024px) 100vw, 33vw"
                className="object-cover"
              />
            </div>
            <div
              className="absolute inset-y-0 w-0.5 bg-primary"
              style={{ left: `${split}%` }}
            >
              <span className="absolute left-1/2 top-1/2 flex size-7 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-primary bg-black/70 text-primary">
                <SplitSquareHorizontal className="size-4" />
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={100}
              value={split}
              onChange={(e) => setSplit(Number(e.target.value))}
              aria-label="Comparison slider"
              className="absolute inset-x-0 bottom-0 top-0 h-full w-full cursor-ew-resize opacity-0"
            />
            <span className="pointer-events-none absolute left-3 top-3 rounded bg-black/60 px-2 py-1 text-[10px] font-semibold text-accent backdrop-blur-sm">
              BEFORE
            </span>
            <span className="pointer-events-none absolute right-3 top-3 rounded bg-black/60 px-2 py-1 text-[10px] font-semibold text-primary backdrop-blur-sm">
              AFTER
            </span>
          </>
        ) : null}

        {/* Confidence heatmap overlay */}
        {showConfidence && !compare ? (
          <div
            className="pointer-events-none absolute inset-0 mix-blend-screen"
            style={{
              background:
                "radial-gradient(circle at 30% 35%, rgba(255,180,40,0.55), transparent 40%), radial-gradient(circle at 70% 60%, rgba(255,90,70,0.5), transparent 35%), radial-gradient(circle at 50% 80%, rgba(40,220,180,0.4), transparent 45%)",
            }}
          />
        ) : null}

        {/* Processing overlay */}
        {running && !done ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-black/55 backdrop-blur-sm">
            <Loader2 className="size-7 animate-spin text-primary" />
            <p className="font-mono text-xs text-primary">
              Reconstructing · {progress}%
            </p>
          </div>
        ) : null}

        {showConfidence && !compare ? (
          <div className="pointer-events-none absolute bottom-3 left-3 rounded-md bg-black/60 px-2 py-1 text-[10px] text-foreground backdrop-blur-sm">
            Confidence heatmap · low → high
          </div>
        ) : null}
      </div>

      {/* Toggles */}
      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={() => {
            setShowConfidence((v) => !v)
            setCompare(false)
          }}
          className={`flex items-center justify-center gap-2 rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
            showConfidence
              ? "border-accent/50 bg-accent/15 text-accent"
              : "border-border bg-secondary/30 text-muted-foreground hover:text-foreground"
          }`}
        >
          <Layers2 className="size-4" />
          Confidence Overlay
        </button>
        <button
          onClick={() => {
            setCompare((v) => !v)
            setShowConfidence(false)
          }}
          className={`flex items-center justify-center gap-2 rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
            compare
              ? "border-primary/50 bg-primary/15 text-primary"
              : "border-border bg-secondary/30 text-muted-foreground hover:text-foreground"
          }`}
        >
          <SplitSquareHorizontal className="size-4" />
          Before / After
        </button>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-2">
        <MetricCard label="Reconstruction Confidence" value="94.2" unit="%" tone="green" />
        <MetricCard label="Spectral Consistency" value="0.96" tone="primary" />
        <MetricCard label="Structural Similarity" value="0.93" tone="primary" />
        <div className="rounded-lg border border-border bg-secondary/30 p-3">
          <p className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
            Processing Status
          </p>
          <p className="mt-1 flex items-center gap-1.5 text-sm font-semibold">
            {done ? (
              <>
                <CheckCircle2 className="size-4 text-chart-3" />
                <span className="text-chart-3">Finalized</span>
              </>
            ) : running ? (
              <>
                <Loader2 className="size-4 animate-spin text-primary" />
                <span className="text-primary">In progress</span>
              </>
            ) : (
              <span className="text-muted-foreground">Idle</span>
            )}
          </p>
        </div>
      </div>
    </Panel>
  )
}
