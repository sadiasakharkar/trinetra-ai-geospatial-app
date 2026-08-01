"use client"

import { useState } from "react"
import {
  Satellite,
  LayoutDashboard,
  Layers,
  BarChart3,
  FileText,
  ChevronDown,
  Globe2,
} from "lucide-react"

const NAV_ITEMS = [
  { label: "Dashboard", icon: LayoutDashboard, active: true },
  { label: "Reconstruction Jobs", icon: Layers, active: false },
  { label: "Analytics", icon: BarChart3, active: false },
  { label: "Documentation", icon: FileText, active: false },
]

export function TopNav() {
  const [active, setActive] = useState("Dashboard")

  return (
    <header className="glass-strong sticky top-0 z-30 border-b border-border">
      <div className="flex h-16 items-center gap-4 px-4 md:px-6">
        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div className="relative flex size-9 items-center justify-center rounded-lg bg-primary/15 ring-1 ring-primary/40">
            <Satellite className="size-5 text-primary" aria-hidden="true" />
          </div>
          <div className="leading-tight">
            <p className="text-sm font-semibold tracking-tight text-foreground">
              CloudVision AI
            </p>
            <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-primary">
              TRINETRA
            </p>
          </div>
        </div>

        {/* Nav */}
        <nav className="ml-4 hidden items-center gap-1 lg:flex">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon
            const isActive = active === item.label
            return (
              <button
                key={item.label}
                onClick={() => setActive(item.label)}
                className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary/12 text-primary"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                }`}
              >
                <Icon className="size-4" aria-hidden="true" />
                {item.label}
              </button>
            )
          })}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-border bg-secondary/50 px-3 py-1.5 sm:flex">
            <span className="relative flex size-2">
              <span className="absolute inline-flex size-2 animate-ping rounded-full bg-chart-3 opacity-75" />
              <span className="relative inline-flex size-2 rounded-full bg-chart-3" />
            </span>
            <span className="text-xs font-medium text-muted-foreground">
              Ground Station Online
            </span>
          </div>

          <button className="flex items-center gap-2 rounded-full border border-border bg-secondary/50 py-1 pl-1 pr-2.5 transition-colors hover:bg-secondary">
            <span className="flex size-7 items-center justify-center rounded-full bg-primary/20 text-xs font-semibold text-primary">
              RS
            </span>
            <span className="hidden text-sm font-medium text-foreground sm:inline">
              R. Sharma
            </span>
            <ChevronDown
              className="size-4 text-muted-foreground"
              aria-hidden="true"
            />
          </button>
        </div>
      </div>
    </header>
  )
}
