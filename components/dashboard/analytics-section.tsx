"use client"

import {
  Cloud,
  Cpu,
  Activity,
  ShieldCheck,
  Clock,
  Zap,
} from "lucide-react"
import { ProgressBar, Badge } from "./ui"

function Card({
  title,
  icon,
  children,
}: {
  title: string
  icon: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <div className="glass flex flex-col rounded-xl border border-border p-4 shadow-lg shadow-black/20">
      <div className="mb-3 flex items-center gap-2">
        {icon}
        <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      </div>
      {children}
    </div>
  )
}

function Row({
  label,
  value,
  tone = "text-foreground",
}: {
  label: string
  value: string
  tone?: string
}) {
  return (
    <div className="flex items-center justify-between py-1.5 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className={`font-medium tabular-nums ${tone}`}>{value}</span>
    </div>
  )
}

export function AnalyticsSection({
  progress,
}: {
  progress: number
}) {
  const totalTiles = 256
  const completed = Math.round((progress / 100) * totalTiles)
  const remaining = totalTiles - completed

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {/* Cloud detection */}
      <Card
        title="Cloud Detection Summary"
        icon={<Cloud className="size-4 text-accent" aria-hidden="true" />}
      >
        <Row label="Cloud Coverage" value="42.7%" tone="text-accent" />
        <ProgressBar value={42.7} tone="accent" />
        <div className="mt-2" />
        <Row label="Shadow Coverage" value="11.3%" />
        <ProgressBar value={11.3} tone="primary" />
        <div className="mt-2" />
        <Row label="Uncertain Pixels" value="3.8%" tone="text-destructive" />
        <ProgressBar value={3.8} tone="green" />
      </Card>

      {/* Reconstruction progress */}
      <Card
        title="AI Reconstruction Progress"
        icon={<Activity className="size-4 text-primary" aria-hidden="true" />}
      >
        <div className="flex items-baseline justify-between">
          <span className="text-3xl font-semibold tabular-nums text-foreground">
            {progress}%
          </span>
          <Badge tone={progress >= 100 ? "green" : "primary"} dot>
            {progress >= 100 ? "Done" : "Running"}
          </Badge>
        </div>
        <div className="my-3">
          <ProgressBar value={progress} />
        </div>
        <Row label="Completed Tiles" value={`${completed} / ${totalTiles}`} tone="text-chart-3" />
        <Row label="Remaining Tiles" value={`${remaining}`} />
      </Card>

      {/* Validation metrics */}
      <Card
        title="Validation Metrics"
        icon={<ShieldCheck className="size-4 text-chart-3" aria-hidden="true" />}
      >
        <Row label="PSNR" value="34.8 dB" tone="text-chart-3" />
        <Row label="SSIM" value="0.931" tone="text-chart-3" />
        <Row label="SAM" value="3.42°" />
        <Row label="NDVI Preservation" value="97.6%" tone="text-chart-3" />
      </Card>

      {/* System status */}
      <Card
        title="System Status"
        icon={<Cpu className="size-4 text-primary" aria-hidden="true" />}
      >
        <Row label="GPU" value="4× A100 · 78%" tone="text-chart-3" />
        <ProgressBar value={78} tone="green" />
        <div className="mt-2" />
        <div className="flex items-center justify-between py-1.5 text-sm">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <Clock className="size-3.5" /> Runtime
          </span>
          <span className="font-medium tabular-nums text-foreground">
            00:04:12
          </span>
        </div>
        <div className="flex items-center justify-between py-1.5 text-sm">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <Zap className="size-3.5" /> Active Model
          </span>
          <span className="font-medium text-primary">DiffCR-v2.1</span>
        </div>
      </Card>
    </div>
  )
}
