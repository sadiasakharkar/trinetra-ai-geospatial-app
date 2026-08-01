"use client"

import { useEffect, useMemo, useRef } from "react"
import Image from "next/image"
import {
  Play,
  Pause,
  RotateCcw,
  Cpu,
  Terminal,
  CheckCircle2,
  Loader2,
  Clock,
  Zap,
  Activity,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { MODELS } from "@/lib/mock"
import { useWorkflow } from "./workflow-context"
import { StepHeader, StepFooter, StepCard } from "./step-shell"
import { Badge, ProgressBar, MetricCard } from "@/components/dashboard/ui"

const LEVEL_STYLES = {
  info: "text-muted-foreground",
  ok: "text-chart-3",
  warn: "text-accent",
}

export function StepRun() {
  const {
    dataset,
    config,
    status,
    progress,
    logs,
    startJob,
    pauseJob,
    resetJob,
    next,
    back,
  } = useWorkflow()

  const logRef = useRef<HTMLDivElement>(null)
  const model = MODELS.find((m) => m.id === config.model)
  const done = status === "complete"

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight
  }, [logs])

  const totalTiles = 256
  const completedTiles = Math.round((progress / 100) * totalTiles)
  const tiles = useMemo(() => Array.from({ length: totalTiles }), [])

  const eta = useMemo(() => {
    if (done) return "00:00"
    const remaining = Math.max(0, 100 - progress)
    const secs = Math.round((remaining / 2) * 0.26)
    const m = Math.floor(secs / 60)
    const s = secs % 60
    return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
  }, [progress, done])

  return (
    <div>
      <StepHeader
        eyebrow="Step 3 of 6"
        title="Run Reconstruction"
        description={`Executing ${model?.name ?? "the model"} on ${
          dataset?.name ?? "the scene"
        }. Watch live progress, tile completion, and the pipeline log stream.`}
        icon={<Activity className="size-5 text-primary" aria-hidden="true" />}
      />

      <StepCard className="mb-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <div className="flex gap-2">
            <button
              onClick={startJob}
              disabled={status === "running"}
              className="flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Play className="size-4" />
              {done ? "Re-run" : status === "paused" ? "Resume" : "Start Job"}
            </button>
            <button
              onClick={pauseJob}
              disabled={status !== "running"}
              className="flex items-center gap-2 rounded-lg border border-border bg-secondary/40 px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-secondary disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Pause className="size-4" />
              Pause
            </button>
            <button
              onClick={resetJob}
              disabled={status === "idle" || status === "running"}
              className="flex items-center gap-2 rounded-lg border border-border bg-secondary/40 px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-secondary disabled:cursor-not-allowed disabled:opacity-40"
            >
              <RotateCcw className="size-4" />
              Reset
            </button>
          </div>

          <div className="flex flex-1 items-center gap-4 sm:justify-end">
            <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Clock className="size-3.5" /> ETA {eta}
            </span>
            <Badge
              tone={done ? "green" : status === "running" ? "primary" : "muted"}
              dot
            >
              {done
                ? "Complete"
                : status === "running"
                  ? "Running"
                  : status === "paused"
                    ? "Paused"
                    : "Ready"}
            </Badge>
          </div>
        </div>

        <div className="mt-4">
          <div className="mb-1.5 flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Overall progress</span>
            <span className="font-mono font-semibold text-primary">
              {progress}%
            </span>
          </div>
          <ProgressBar value={progress} tone={done ? "green" : "primary"} />
        </div>
      </StepCard>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <StepCard className="lg:col-span-1">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <Cpu className="size-4 text-primary" /> Tile Processing
            </h2>
            <span className="font-mono text-xs text-muted-foreground">
              {completedTiles}/{totalTiles}
            </span>
          </div>
          <div className="relative aspect-square overflow-hidden rounded-lg border border-border bg-black/40">
            <Image
              src={dataset?.thumb ?? "/images/liss-iv-cloudy.png"}
              alt="Scene being reconstructed"
              fill
              sizes="(max-width: 1024px) 100vw, 33vw"
              className="object-cover opacity-60"
            />
            <div
              className="absolute inset-0 grid"
              style={{
                gridTemplateColumns: "repeat(16, 1fr)",
                gridTemplateRows: "repeat(16, 1fr)",
              }}
            >
              {tiles.map((_, i) => {
                const isDone = i < completedTiles
                const isActive = i === completedTiles && status === "running"
                return (
                  <span
                    key={i}
                    className={cn(
                      "border-[0.5px] border-primary/10 transition-colors duration-300",
                      isDone
                        ? "bg-primary/35"
                        : isActive
                          ? "animate-pulse bg-accent/60"
                          : "bg-black/30",
                    )}
                  />
                )
              })}
            </div>
          </div>
          <p className="mt-2 text-center text-[11px] text-muted-foreground">
            {config.tileSize}px tiles - {model?.name}
          </p>
        </StepCard>

        <StepCard className="lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <Terminal className="size-4 text-primary" /> Pipeline Log
            </h2>
            <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Zap className="size-3.5 text-primary" /> {model?.name ?? "Active model"}
            </span>
          </div>
          <div
            ref={logRef}
            className="h-64 overflow-y-auto rounded-lg border border-border bg-black/50 p-3 font-mono text-xs leading-relaxed"
          >
            {logs.length === 0 ? (
              <p className="text-muted-foreground/60">$ awaiting job start...</p>
            ) : (
              logs.map((l, i) => (
                <div key={i} className="flex gap-2">
                  <span className="shrink-0 text-muted-foreground/50">
                    {l.time}
                  </span>
                  <span className={LEVEL_STYLES[l.level]}>
                    {l.level === "ok" ? "OK " : l.level === "warn" ? "! " : "> "}
                    {l.text}
                  </span>
                </div>
              ))
            )}
            {status === "running" ? (
              <div className="mt-1 flex items-center gap-2 text-primary">
                <Loader2 className="size-3 animate-spin" />
                <span className="animate-pulse">processing...</span>
              </div>
            ) : null}
          </div>

          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
            <MetricCard label="Completed" value={`${completedTiles}`} sub="tiles" tone="green" />
            <MetricCard label="Throughput" value={status === "running" ? "Live" : "Idle"} />
            <MetricCard label="Engine" value={status === "running" ? "Active" : "Pending"} tone="primary" />
            <MetricCard
              label="Status"
              value={done ? "Done" : status === "running" ? "Live" : "Idle"}
              tone={done ? "green" : "accent"}
            />
          </div>
        </StepCard>
      </div>

      {done ? (
        <StepCard className="mt-4 border-chart-3/30 bg-chart-3/8">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="size-6 text-chart-3" />
            <div>
              <p className="text-sm font-semibold text-foreground">
                Reconstruction finished successfully
              </p>
              <p className="text-xs text-muted-foreground">
                Tile reconstruction completed and backend metrics are ready to review.
              </p>
            </div>
          </div>
        </StepCard>
      ) : null}

      <StepFooter
        onBack={back}
        onNext={next}
        nextDisabled={!done}
        nextLabel="Open Validation Dashboard"
        nextHint={!done ? "Finish the job to view validation" : undefined}
      />
    </div>
  )
}
