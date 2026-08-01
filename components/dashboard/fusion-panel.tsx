"use client"

import Image from "next/image"
import {
  Radar,
  History,
  Mountain,
  Layers3,
  CheckCircle2,
  CircleDot,
} from "lucide-react"
import { Panel, StatItem, Badge, MetricCard } from "./ui"

const TIMELINE = [
  { date: "Mar 2026", img: "/images/temporal-1.png", clear: true },
  { date: "Apr 2026", img: "/images/temporal-2.png", clear: true },
  { date: "May 2026", img: "/images/liss-iv-reconstructed.png", clear: true },
  { date: "Jun 2026", img: "/images/temporal-1.png", clear: false },
]

function SectionTitle({
  icon,
  children,
}: {
  icon: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
      {icon}
      {children}
    </div>
  )
}

export function FusionPanel() {
  return (
    <Panel
      title="Multimodal Evidence Sources"
      icon={<Layers3 className="size-4 text-primary" aria-hidden="true" />}
      badge={<Badge tone="primary" dot>4 Active</Badge>}
    >
      {/* Sentinel-1 SAR */}
      <div className="rounded-lg border border-border bg-secondary/20 p-3">
        <div className="mb-2 flex items-center justify-between">
          <SectionTitle icon={<Radar className="size-3.5" />}>
            Sentinel-1 SAR Data
          </SectionTitle>
          <Badge tone="green" dot>
            Acquired
          </Badge>
        </div>
        <div className="flex gap-3">
          <div className="relative size-20 shrink-0 overflow-hidden rounded-md border border-border">
            <Image
              src="/images/sentinel-sar.png"
              alt="Sentinel-1 SAR radar backscatter preview"
              fill
              sizes="80px"
              className="object-cover"
            />
          </div>
          <div className="flex-1">
            <StatItem
              label="Polarization"
              value="VV + VH"
            />
            <StatItem
              label="Co-registration"
              value={
                <span className="flex items-center gap-1 text-chart-3">
                  <CheckCircle2 className="size-3.5" /> Aligned
                </span>
              }
            />
          </div>
        </div>
      </div>

      {/* Temporal references */}
      <div className="rounded-lg border border-border bg-secondary/20 p-3">
        <div className="mb-3 flex items-center justify-between">
          <SectionTitle icon={<History className="size-3.5" />}>
            Temporal Reference Images
          </SectionTitle>
          <span className="text-[11px] text-muted-foreground">4 scenes</span>
        </div>
        <div className="relative">
          <div className="absolute left-0 right-0 top-[34px] h-px bg-border" />
          <div className="grid grid-cols-4 gap-2">
            {TIMELINE.map((t) => (
              <div key={t.date} className="flex flex-col items-center gap-2">
                <div className="relative size-full aspect-square overflow-hidden rounded-md border border-border">
                  <Image
                    src={t.img || "/images/liss-iv-cloudy.png"}
                    alt={`Temporal reference scene from ${t.date}`}
                    fill
                    sizes="80px"
                    className="object-cover"
                  />
                  <span
                    className={`absolute right-1 top-1 size-2 rounded-full ring-2 ring-black/40 ${
                      t.clear ? "bg-chart-3" : "bg-accent"
                    }`}
                    title={t.clear ? "Cloud-free" : "Partly cloudy"}
                  />
                </div>
                <span className="text-[10px] text-muted-foreground">
                  {t.date}
                </span>
              </div>
            ))}
          </div>
        </div>
        <div className="mt-3 flex items-center gap-4 text-[10px] text-muted-foreground">
          <span className="flex items-center gap-1">
            <span className="size-2 rounded-full bg-chart-3" /> Cloud-free ref
          </span>
          <span className="flex items-center gap-1">
            <span className="size-2 rounded-full bg-accent" /> Target scene
          </span>
        </div>
      </div>

      {/* DEM */}
      <div className="rounded-lg border border-border bg-secondary/20 p-3">
        <div className="mb-2">
          <SectionTitle icon={<Mountain className="size-3.5" />}>
            DEM Information
          </SectionTitle>
        </div>
        <div className="flex gap-3">
          <div className="relative h-20 w-28 shrink-0 overflow-hidden rounded-md border border-border">
            <Image
              src="/images/dem-terrain.png"
              alt="Digital elevation model terrain preview"
              fill
              sizes="112px"
              className="object-cover"
            />
          </div>
          <div className="flex-1">
            <StatItem label="Elevation" value="4 – 312 m" />
            <StatItem label="Mean Slope" value="2.4°" />
            <StatItem label="Source" value="CartoDEM v3 R1" />
          </div>
        </div>
      </div>

      {/* Fusion summary */}
      <div className="rounded-lg border border-primary/30 bg-primary/8 p-3">
        <div className="mb-3 flex items-center gap-1.5 text-xs font-semibold text-primary">
          <CircleDot className="size-3.5" />
          Fusion Summary
        </div>
        <div className="grid grid-cols-2 gap-2">
          <MetricCard label="Active Sources" value="4" sub="SAR · Temporal · DEM · Optical" />
          <MetricCard label="Temporal Gap" value="31" unit="days" tone="accent" />
          <MetricCard label="Alignment" value="98.6" unit="%" tone="green" />
          <MetricCard label="Data Quality" value="A+" sub="Composite score 0.94" tone="green" />
        </div>
      </div>
    </Panel>
  )
}
