"use client"

import type { ReactNode } from "react"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { cn } from "@/lib/utils"

export function StepHeader({
  eyebrow,
  title,
  description,
  icon,
}: {
  eyebrow: string
  title: string
  description: string
  icon?: ReactNode
}) {
  return (
    <div className="mb-6 flex items-start gap-3">
      {icon ? (
        <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-primary/15 ring-1 ring-primary/30">
          {icon}
        </div>
      ) : null}
      <div className="flex flex-col gap-1">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary">
          {eyebrow}
        </p>
        <h1 className="text-balance text-xl font-semibold tracking-tight text-foreground md:text-2xl">
          {title}
        </h1>
        <p className="max-w-2xl text-pretty text-sm text-muted-foreground">
          {description}
        </p>
      </div>
    </div>
  )
}

export function StepFooter({
  onBack,
  onNext,
  nextLabel = "Continue",
  backLabel = "Back",
  nextDisabled = false,
  nextHint,
  hideBack = false,
}: {
  onBack?: () => void
  onNext?: () => void
  nextLabel?: string
  backLabel?: string
  nextDisabled?: boolean
  nextHint?: string
  hideBack?: boolean
}) {
  return (
    <div className="mt-6 flex flex-col gap-3 border-t border-border pt-5 sm:flex-row sm:items-center">
      {!hideBack ? (
        <button
          onClick={onBack}
          className="flex items-center justify-center gap-2 rounded-lg border border-border bg-secondary/40 px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
        >
          <ArrowLeft className="size-4" />
          {backLabel}
        </button>
      ) : null}

      <div className="flex flex-1 items-center justify-end gap-3">
        {nextHint ? (
          <span className="hidden text-xs text-muted-foreground sm:inline">
            {nextHint}
          </span>
        ) : null}
        {onNext ? (
          <button
            onClick={onNext}
            disabled={nextDisabled}
            className={cn(
              "flex items-center justify-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold transition-all",
              nextDisabled
                ? "cursor-not-allowed bg-secondary/40 text-muted-foreground"
                : "bg-primary text-primary-foreground hover:opacity-90",
            )}
          >
            {nextLabel}
            <ArrowRight className="size-4" />
          </button>
        ) : null}
      </div>
    </div>
  )
}

export function StepCard({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        "glass rounded-2xl border border-border p-5 shadow-xl shadow-black/20 md:p-6",
        className,
      )}
    >
      {children}
    </div>
  )
}
