"use client"

import { useEffect, useState } from "react"
import { TopNav } from "@/components/dashboard/top-nav"
import { InputPanel } from "@/components/dashboard/input-panel"
import { FusionPanel } from "@/components/dashboard/fusion-panel"
import { OutputPanel } from "@/components/dashboard/output-panel"
import { AnalyticsSection } from "@/components/dashboard/analytics-section"
import { ActionPanel } from "@/components/dashboard/action-panel"

export default function Page() {
  const [running, setRunning] = useState(false)
  const [progress, setProgress] = useState(68)

  useEffect(() => {
    if (!running) return
    const id = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          setRunning(false)
          return 100
        }
        return Math.min(100, p + 2)
      })
    }, 320)
    return () => clearInterval(id)
  }, [running])

  const handleStart = () => {
    if (progress >= 100) setProgress(0)
    setRunning(true)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Ambient grid backdrop */}
      <div className="grid-bg pointer-events-none fixed inset-0 opacity-30" />

      <div className="relative">
        <TopNav />

        <main className="mx-auto max-w-[1800px] px-4 py-6 md:px-6">
          {/* Page heading */}
          <div className="mb-6 flex flex-col gap-1">
            <h1 className="text-balance text-xl font-semibold tracking-tight text-foreground md:text-2xl">
              Cloud Removal &amp; Reconstruction Workspace
            </h1>
            <p className="text-pretty text-sm text-muted-foreground">
              Generative AI reconstruction for LISS-IV imagery via multimodal SAR,
              temporal, and DEM fusion · Scene{" "}
              <span className="font-mono text-primary">LISS4-2026-0618-DT04</span>
            </p>
          </div>

          {/* Three-panel workspace */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <InputPanel />
            <FusionPanel />
            <OutputPanel running={running} progress={progress} />
          </div>

          {/* Bottom analytics */}
          <div className="mt-4">
            <AnalyticsSection progress={progress} />
          </div>

          {/* Spacer so floating panel doesn't cover content */}
          <div className="h-24 lg:h-6" />
        </main>

        <ActionPanel
          running={running}
          progress={progress}
          onStart={handleStart}
          onPause={() => setRunning(false)}
        />
      </div>
    </div>
  )
}
