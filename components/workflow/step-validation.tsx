"use client"

import {
  ShieldCheck,
  TrendingUp,
  BarChart3,
  PieChart,
  Sprout,
  Waves,
} from "lucide-react"
import { VALIDATION } from "@/lib/mock"
import { useWorkflow } from "./workflow-context"
import { StepHeader, StepFooter, StepCard } from "./step-shell"
import { MetricCard, ProgressBar } from "@/components/dashboard/ui"
import { LineChart, BarChart, DonutChart } from "./charts"

export function StepValidation() {
  const { next, back } = useWorkflow()

  return (
    <div>
      <StepHeader
        eyebrow="Step 4 of 6"
        title="Validation Dashboard"
        description="Quantitative quality assessment of the reconstruction against cloud-free reference imagery — pixel fidelity, spectral consistency, and structural similarity."
        icon={<ShieldCheck className="size-5 text-primary" aria-hidden="true" />}
      />

      {/* Headline metrics */}
      <div className="mb-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        {VALIDATION.headline.map((m) => (
          <MetricCard
            key={m.label}
            label={m.label}
            value={m.value}
            unit={m.unit}
            sub={m.sub}
            tone={m.tone}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Convergence line chart */}
        <StepCard className="lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <TrendingUp className="size-4 text-primary" /> Quality Convergence
            </h2>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="h-0.5 w-3 bg-primary" /> PSNR (dB)
              </span>
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="h-0.5 w-3 bg-chart-3" /> SSIM
              </span>
            </div>
          </div>
          <LineChart data={VALIDATION.trend} />
          <p className="mt-2 text-[11px] text-muted-foreground">
            Both metrics converge by diffusion step 8, exceeding the 30 dB PSNR
            acceptance threshold.
          </p>
        </StepCard>

        {/* Pixel classification donut */}
        <StepCard>
          <div className="mb-3 flex items-center gap-2">
            <PieChart className="size-4 text-primary" />
            <h2 className="text-sm font-semibold text-foreground">
              Pixel Classification
            </h2>
          </div>
          <DonutChart data={VALIDATION.classes} />
          <p className="mt-3 text-[11px] text-muted-foreground">
            Only 3.8% of pixels fall below the confidence threshold and are
            flagged for review.
          </p>
        </StepCard>

        {/* Spectral band fidelity */}
        <StepCard className="lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <BarChart3 className="size-4 text-primary" /> Spectral Band Fidelity
            </h2>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="size-2.5 rounded-sm bg-secondary" /> Reference
              </span>
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="size-2.5 rounded-sm bg-primary" /> Reconstructed
              </span>
            </div>
          </div>
          <BarChart data={VALIDATION.bands} />
        </StepCard>

        {/* Index preservation */}
        <StepCard>
          <div className="mb-3 flex items-center gap-2">
            <Sprout className="size-4 text-chart-3" />
            <h2 className="text-sm font-semibold text-foreground">
              Index Preservation
            </h2>
          </div>
          <div className="flex flex-col gap-4">
            <div>
              <div className="mb-1.5 flex items-center justify-between text-sm">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Sprout className="size-3.5" /> NDVI
                </span>
                <span className="font-medium text-chart-3">97.6%</span>
              </div>
              <ProgressBar value={97.6} tone="green" />
            </div>
            <div>
              <div className="mb-1.5 flex items-center justify-between text-sm">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Waves className="size-3.5" /> NDWI
                </span>
                <span className="font-medium text-chart-3">95.1%</span>
              </div>
              <ProgressBar value={95.1} tone="green" />
            </div>
            <div>
              <div className="mb-1.5 flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Texture (GLCM)</span>
                <span className="font-medium text-primary">92.4%</span>
              </div>
              <ProgressBar value={92.4} tone="primary" />
            </div>
          </div>
        </StepCard>
      </div>

      <StepFooter
        onBack={back}
        onNext={next}
        nextLabel="Compare Results"
      />
    </div>
  )
}
