"use client"

import { useState } from "react"
import {
  SlidersHorizontal,
  Cpu,
  Layers3,
  Check,
  Gauge,
  FileOutput,
  Grid3x3,
  Sprout,
} from "lucide-react"
import { cn } from "@/lib/utils"
import {
  MODELS,
  OUTPUT_FORMATS,
  TILE_SIZES,
  type FusionSource,
} from "@/lib/mock"
import { useWorkflow } from "./workflow-context"
import { StepHeader, StepFooter, StepCard } from "./step-shell"
import { Badge } from "@/components/dashboard/ui"

function Toggle({ on }: { on: boolean }) {
  return (
    <span
      className={cn(
        "relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors",
        on ? "bg-primary" : "bg-secondary",
      )}
    >
      <span
        className={cn(
          "inline-block size-4 transform rounded-full bg-background transition-transform",
          on ? "translate-x-4" : "translate-x-0.5",
        )}
      />
    </span>
  )
}

export function StepConfigure() {
  const { config, setConfig, next, back, dataset } = useWorkflow()
  const [local, setLocal] = useState(config)

  const toggleSource = (id: string) =>
    setLocal((c) => ({
      ...c,
      sources: c.sources.map((s) =>
        s.id === id ? { ...s, enabled: !s.enabled } : s,
      ),
    }))

  const activeSources = local.sources.filter((s) => s.enabled).length

  const handleNext = () => {
    setConfig(local)
    next()
  }

  return (
    <div>
      <StepHeader
        eyebrow="Step 2 of 6"
        title="Configure Reconstruction"
        description={`Tune the generative pipeline for ${
          dataset?.name ?? "the selected scene"
        }. Pick a model, choose multimodal fusion sources, and set output parameters.`}
        icon={<SlidersHorizontal className="size-5 text-primary" aria-hidden="true" />}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Model selection */}
        <StepCard className="lg:col-span-2">
          <div className="mb-3 flex items-center gap-2">
            <Cpu className="size-4 text-primary" />
            <h2 className="text-sm font-semibold text-foreground">
              Reconstruction Model
            </h2>
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {MODELS.map((m) => {
              const selected = local.model === m.id
              return (
                <button
                  key={m.id}
                  onClick={() => setLocal((c) => ({ ...c, model: m.id }))}
                  className={cn(
                    "flex flex-col gap-2 rounded-xl border p-3 text-left transition-all",
                    selected
                      ? "border-primary bg-primary/10 ring-1 ring-primary"
                      : "border-border bg-secondary/20 hover:border-primary/40",
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-foreground">
                      {m.name}
                    </span>
                    {selected ? (
                      <span className="flex size-5 items-center justify-center rounded-full bg-primary text-primary-foreground">
                        <Check className="size-3" />
                      </span>
                    ) : null}
                  </div>
                  <Badge
                    tone={
                      m.speed === "Best Quality"
                        ? "green"
                        : m.speed === "Balanced"
                          ? "primary"
                          : "accent"
                    }
                  >
                    {m.speed}
                  </Badge>
                  <p className="text-[11px] leading-relaxed text-muted-foreground">
                    {m.desc}
                  </p>
                </button>
              )
            })}
          </div>

          {/* Fidelity slider */}
          <div className="mt-5">
            <div className="mb-2 flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-sm font-medium text-foreground">
                <Gauge className="size-4 text-primary" />
                Reconstruction Fidelity
              </span>
              <span className="font-mono text-sm text-primary">
                {local.fidelity}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={100}
              value={local.fidelity}
              onChange={(e) =>
                setLocal((c) => ({ ...c, fidelity: Number(e.target.value) }))
              }
              className="h-2 w-full cursor-pointer appearance-none rounded-full bg-secondary accent-primary"
              aria-label="Reconstruction fidelity"
            />
            <div className="mt-1 flex justify-between text-[11px] text-muted-foreground">
              <span>Faster</span>
              <span>Higher detail</span>
            </div>
          </div>
        </StepCard>

        {/* Fusion sources */}
        <StepCard>
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers3 className="size-4 text-primary" />
              <h2 className="text-sm font-semibold text-foreground">
                Fusion Sources
              </h2>
            </div>
            <Badge tone="primary">{activeSources} active</Badge>
          </div>
          <div className="flex flex-col gap-2">
            {local.sources.map((s: FusionSource) => (
              <button
                key={s.id}
                onClick={() => toggleSource(s.id)}
                className={cn(
                  "flex items-center justify-between gap-3 rounded-lg border px-3 py-2.5 text-left transition-colors",
                  s.enabled
                    ? "border-primary/40 bg-primary/8"
                    : "border-border bg-secondary/20",
                )}
              >
                <span className="flex flex-col">
                  <span className="text-sm font-medium text-foreground">
                    {s.label}
                  </span>
                  <span className="text-[11px] text-muted-foreground">
                    {s.desc}
                  </span>
                </span>
                <Toggle on={s.enabled} />
              </button>
            ))}
          </div>
        </StepCard>
      </div>

      {/* Output params */}
      <StepCard className="mt-4">
        <div className="mb-4 flex items-center gap-2">
          <FileOutput className="size-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">
            Output Parameters
          </h2>
        </div>
        <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
          {/* Output format */}
          <div>
            <span className="mb-2 block text-xs font-medium text-muted-foreground">
              Output Format
            </span>
            <div className="flex flex-wrap gap-2">
              {OUTPUT_FORMATS.map((f) => (
                <button
                  key={f}
                  onClick={() => setLocal((c) => ({ ...c, outputFormat: f }))}
                  className={cn(
                    "rounded-md border px-2.5 py-1.5 text-xs font-medium transition-colors",
                    local.outputFormat === f
                      ? "border-primary bg-primary/15 text-primary"
                      : "border-border bg-secondary/30 text-muted-foreground hover:text-foreground",
                  )}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Tile size */}
          <div>
            <span className="mb-2 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <Grid3x3 className="size-3.5" /> Tile Size
            </span>
            <div className="flex gap-2">
              {TILE_SIZES.map((t) => (
                <button
                  key={t}
                  onClick={() => setLocal((c) => ({ ...c, tileSize: t }))}
                  className={cn(
                    "flex-1 rounded-md border px-2.5 py-1.5 text-xs font-medium transition-colors",
                    local.tileSize === t
                      ? "border-primary bg-primary/15 text-primary"
                      : "border-border bg-secondary/30 text-muted-foreground hover:text-foreground",
                  )}
                >
                  {t}px
                </button>
              ))}
            </div>
          </div>

          {/* NDVI toggle */}
          <div>
            <span className="mb-2 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <Sprout className="size-3.5" /> Vegetation Index
            </span>
            <button
              onClick={() =>
                setLocal((c) => ({ ...c, preserveNdvi: !c.preserveNdvi }))
              }
              className={cn(
                "flex w-full items-center justify-between rounded-md border px-3 py-1.5 text-xs font-medium transition-colors",
                local.preserveNdvi
                  ? "border-primary/40 bg-primary/8 text-foreground"
                  : "border-border bg-secondary/30 text-muted-foreground",
              )}
            >
              Preserve NDVI consistency
              <Toggle on={local.preserveNdvi} />
            </button>
          </div>
        </div>
      </StepCard>

      <StepFooter
        onBack={back}
        onNext={handleNext}
        nextDisabled={activeSources === 0}
        nextLabel="Run Reconstruction"
        nextHint={
          activeSources === 0 ? "Enable at least one fusion source" : undefined
        }
      />
    </div>
  )
}
