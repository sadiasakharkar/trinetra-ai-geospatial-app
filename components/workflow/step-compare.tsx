"use client"

import { useState } from "react"
import Image from "next/image"
import {
  SplitSquareHorizontal,
  Layers2,
  Maximize2,
  GitCompare,
  Eye,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useWorkflow } from "./workflow-context"
import { StepHeader, StepFooter, StepCard } from "./step-shell"
import { Badge, MetricCard } from "@/components/dashboard/ui"

type ViewMode = "slider" | "side" | "confidence"

export function StepCompare() {
  const { dataset, next, back } = useWorkflow()
  const [mode, setMode] = useState<ViewMode>("slider")
  const [split, setSplit] = useState(50)

  const cloudy = dataset?.thumb ?? "/images/liss-iv-cloudy.png"
  const clear = dataset?.reconstructed ?? "/images/liss-iv-reconstructed.png"

  return (
    <div>
      <StepHeader
        eyebrow="Step 5 of 6"
        title="Compare Results"
        description="Inspect the reconstruction against the original cloud-contaminated input. Drag the slider, view side-by-side, or overlay the confidence heatmap."
        icon={<GitCompare className="size-5 text-primary" aria-hidden="true" />}
      />

      {/* Mode toggles */}
      <div className="mb-4 flex flex-wrap gap-2">
        {(
          [
            { id: "slider", label: "Slider", icon: SplitSquareHorizontal },
            { id: "side", label: "Side by Side", icon: Maximize2 },
            { id: "confidence", label: "Confidence Overlay", icon: Layers2 },
          ] as const
        ).map((m) => {
          const Icon = m.icon
          const active = mode === m.id
          return (
            <button
              key={m.id}
              onClick={() => setMode(m.id)}
              className={cn(
                "flex items-center gap-2 rounded-lg border px-3.5 py-2 text-sm font-medium transition-colors",
                active
                  ? "border-primary bg-primary/15 text-primary"
                  : "border-border bg-secondary/30 text-muted-foreground hover:text-foreground",
              )}
            >
              <Icon className="size-4" />
              {m.label}
            </button>
          )
        })}
      </div>

      <StepCard>
        {mode === "side" ? (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <figure className="relative">
              <div className="relative aspect-square overflow-hidden rounded-lg border border-border bg-black/40">
                <Image
                  src={cloudy || "/placeholder.svg"}
                  alt="Original cloudy input scene"
                  fill
                  sizes="(max-width: 640px) 100vw, 40vw"
                  className="object-cover"
                />
                <span className="absolute left-3 top-3">
                  <Badge tone="accent" dot>
                    Before · Cloudy
                  </Badge>
                </span>
              </div>
            </figure>
            <figure className="relative">
              <div className="relative aspect-square overflow-hidden rounded-lg border border-border bg-black/40">
                <Image
                  src={clear || "/placeholder.svg"}
                  alt="AI reconstructed cloud-free scene"
                  fill
                  sizes="(max-width: 640px) 100vw, 40vw"
                  className="object-cover"
                />
                <span className="absolute left-3 top-3">
                  <Badge tone="green" dot>
                    After · Reconstructed
                  </Badge>
                </span>
              </div>
            </figure>
          </div>
        ) : (
          <div className="relative mx-auto aspect-square w-full max-w-2xl overflow-hidden rounded-lg border border-border bg-black/40">
            <Image
              src={clear || "/placeholder.svg"}
              alt="AI reconstructed cloud-free scene"
              fill
              sizes="(max-width: 1024px) 100vw, 60vw"
              className="object-cover"
            />

            {mode === "slider" ? (
              <>
                <div
                  className="absolute inset-0 overflow-hidden"
                  style={{ clipPath: `inset(0 ${100 - split}% 0 0)` }}
                >
                  <Image
                    src={cloudy || "/placeholder.svg"}
                    alt="Original cloudy scene"
                    fill
                    sizes="(max-width: 1024px) 100vw, 60vw"
                    className="object-cover"
                  />
                </div>
                <div
                  className="absolute inset-y-0 w-0.5 bg-primary"
                  style={{ left: `${split}%` }}
                >
                  <span className="absolute left-1/2 top-1/2 flex size-8 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-primary bg-black/70 text-primary">
                    <SplitSquareHorizontal className="size-4" />
                  </span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={split}
                  onChange={(e) => setSplit(Number(e.target.value))}
                  aria-label="Comparison slider position"
                  className="absolute inset-0 size-full cursor-ew-resize opacity-0"
                />
                <span className="pointer-events-none absolute left-3 top-3 rounded bg-black/60 px-2 py-1 text-[10px] font-semibold text-accent backdrop-blur-sm">
                  BEFORE
                </span>
                <span className="pointer-events-none absolute right-3 top-3 rounded bg-black/60 px-2 py-1 text-[10px] font-semibold text-primary backdrop-blur-sm">
                  AFTER
                </span>
              </>
            ) : null}

            {mode === "confidence" ? (
              <>
                <div
                  className="pointer-events-none absolute inset-0 mix-blend-screen"
                  style={{
                    background:
                      "radial-gradient(circle at 30% 35%, rgba(255,180,40,0.55), transparent 40%), radial-gradient(circle at 70% 60%, rgba(255,90,70,0.5), transparent 35%), radial-gradient(circle at 50% 80%, rgba(40,220,180,0.4), transparent 45%)",
                  }}
                />
                <div className="pointer-events-none absolute bottom-3 left-3 flex items-center gap-2 rounded-md bg-black/60 px-2.5 py-1.5 backdrop-blur-sm">
                  <Eye className="size-3.5 text-primary" />
                  <span className="text-[10px] text-foreground">
                    Confidence
                  </span>
                  <span className="h-2 w-16 rounded-full bg-gradient-to-r from-chart-3 via-accent to-destructive" />
                  <span className="text-[10px] text-muted-foreground">
                    high → low
                  </span>
                </div>
              </>
            ) : null}
          </div>
        )}
      </StepCard>

      {/* Improvement metrics */}
      <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <MetricCard label="Cloud Removed" value="42.7" unit="%" tone="green" sub="of scene area" />
        <MetricCard label="Pixels Recovered" value="38.9" unit="M" tone="primary" sub="reconstructed" />
        <MetricCard label="Confidence" value="94.2" unit="%" tone="green" sub="mean over scene" />
        <MetricCard label="SSIM Gain" value="+0.41" tone="primary" sub="vs cloudy input" />
      </div>

      <StepFooter
        onBack={back}
        onNext={next}
        nextLabel="Download Outputs"
      />
    </div>
  )
}
