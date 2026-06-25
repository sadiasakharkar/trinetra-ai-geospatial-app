"use client"

import { useState } from "react"
import Image from "next/image"
import {
  CloudRain,
  Plus,
  Minus,
  Layers,
  Maximize2,
  Eye,
  EyeOff,
  Crosshair,
} from "lucide-react"
import { Panel, StatItem, Badge } from "./ui"

const LAYERS = [
  { id: "true", label: "True Color", on: true },
  { id: "cloud", label: "Cloud Mask", on: true },
  { id: "grid", label: "Geo Grid", on: false },
]

export function InputPanel() {
  const [zoom, setZoom] = useState(100)
  const [layers, setLayers] = useState(LAYERS)

  const toggleLayer = (id: string) =>
    setLayers((prev) =>
      prev.map((l) => (l.id === id ? { ...l, on: !l.on } : l)),
    )

  const showGrid = layers.find((l) => l.id === "grid")?.on
  const showMask = layers.find((l) => l.id === "cloud")?.on

  return (
    <Panel
      title="Cloudy LISS-IV Scene"
      icon={<CloudRain className="size-4 text-accent" aria-hidden="true" />}
      badge={<Badge tone="accent" dot>Input</Badge>}
    >
      {/* Viewer */}
      <div className="relative aspect-square w-full overflow-hidden rounded-lg border border-border bg-black/40">
        <Image
          src="/images/liss-iv-cloudy.png"
          alt="Cloud-contaminated LISS-IV satellite scene of an agricultural delta region"
          fill
          sizes="(max-width: 1024px) 100vw, 33vw"
          className="object-cover transition-transform duration-300"
          style={{ transform: `scale(${zoom / 100})` }}
          priority
        />

        {showGrid ? (
          <div className="grid-bg pointer-events-none absolute inset-0 opacity-60" />
        ) : null}

        {showMask ? (
          <div className="pointer-events-none absolute left-3 top-3">
            <span className="rounded-md bg-accent/85 px-2 py-1 text-[10px] font-semibold text-accent-foreground">
              CLOUD MASK ACTIVE
            </span>
          </div>
        ) : null}

        {/* Coordinate readout */}
        <div className="pointer-events-none absolute bottom-3 left-3 rounded-md bg-black/55 px-2 py-1 font-mono text-[10px] text-primary backdrop-blur-sm">
          22.5726°N · 88.3639°E
        </div>

        {/* Zoom controls */}
        <div className="absolute right-3 top-3 flex flex-col overflow-hidden rounded-lg border border-border bg-black/55 backdrop-blur-sm">
          <button
            onClick={() => setZoom((z) => Math.min(180, z + 20))}
            className="flex size-8 items-center justify-center text-foreground transition-colors hover:bg-primary/20"
            aria-label="Zoom in"
          >
            <Plus className="size-4" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(100, z - 20))}
            className="flex size-8 items-center justify-center border-t border-border text-foreground transition-colors hover:bg-primary/20"
            aria-label="Zoom out"
          >
            <Minus className="size-4" />
          </button>
          <button
            onClick={() => setZoom(100)}
            className="flex size-8 items-center justify-center border-t border-border text-foreground transition-colors hover:bg-primary/20"
            aria-label="Reset view"
          >
            <Maximize2 className="size-3.5" />
          </button>
        </div>

        <div className="pointer-events-none absolute bottom-3 right-3 rounded-md bg-black/55 px-2 py-1 font-mono text-[10px] text-foreground backdrop-blur-sm">
          {zoom}%
        </div>
      </div>

      {/* Layer controls */}
      <div>
        <div className="mb-2 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
          <Layers className="size-3.5" aria-hidden="true" />
          Layer Controls
        </div>
        <div className="flex flex-col gap-1.5">
          {layers.map((layer) => (
            <button
              key={layer.id}
              onClick={() => toggleLayer(layer.id)}
              className="flex items-center justify-between rounded-md border border-border bg-secondary/30 px-3 py-2 text-sm transition-colors hover:bg-secondary/60"
            >
              <span className="text-foreground">{layer.label}</span>
              {layer.on ? (
                <Eye className="size-4 text-primary" aria-hidden="true" />
              ) : (
                <EyeOff
                  className="size-4 text-muted-foreground"
                  aria-hidden="true"
                />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="rounded-lg border border-border bg-secondary/20 px-3 py-1">
        <div className="flex items-center gap-1.5 py-2 text-xs font-medium text-muted-foreground">
          <Crosshair className="size-3.5" aria-hidden="true" />
          Scene Metadata
        </div>
        <StatItem label="Acquisition Date" value="2026-06-18 10:42 IST" />
        <StatItem label="Resolution" value="5.8 m / pixel" />
        <StatItem
          label="Cloud Coverage"
          value="42.7%"
          hint={<Badge tone="accent">High</Badge>}
        />
        <StatItem label="Area Covered" value="1,204 km²" />
        <StatItem label="Sensor Type" value="LISS-IV (Resourcesat-2A)" />
      </div>
    </Panel>
  )
}
