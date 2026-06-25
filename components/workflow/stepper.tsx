"use client"

import { Check, Lock } from "lucide-react"
import { cn } from "@/lib/utils"
import { STEPS, useWorkflow } from "./workflow-context"

export function Stepper() {
  const { step, furthest, goTo, canAccess } = useWorkflow()
  const currentIndex = STEPS.findIndex((s) => s.id === step)

  return (
    <nav
      aria-label="Reconstruction workflow progress"
      className="glass-strong sticky top-16 z-20 border-b border-border"
    >
      <ol className="mx-auto flex max-w-[1800px] items-center gap-1 overflow-x-auto px-4 py-3 md:gap-2 md:px-6">
        {STEPS.map((s, i) => {
          const done = i < furthest || (i < currentIndex)
          const active = s.id === step
          const accessible = canAccess(s.id)
          const completedFlag = i < furthest

          return (
            <li key={s.id} className="flex shrink-0 items-center">
              <button
                onClick={() => goTo(s.id)}
                disabled={!accessible}
                aria-current={active ? "step" : undefined}
                className={cn(
                  "group flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-sm transition-colors md:px-3",
                  active
                    ? "bg-primary/15 text-primary"
                    : accessible
                      ? "text-foreground hover:bg-secondary/60"
                      : "cursor-not-allowed text-muted-foreground/50",
                )}
              >
                <span
                  className={cn(
                    "flex size-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold ring-1 ring-inset transition-colors",
                    active
                      ? "bg-primary text-primary-foreground ring-primary"
                      : completedFlag
                        ? "bg-chart-3/20 text-chart-3 ring-chart-3/40"
                        : accessible
                          ? "bg-secondary text-muted-foreground ring-border"
                          : "bg-secondary/40 text-muted-foreground/40 ring-border/40",
                  )}
                >
                  {completedFlag && !active ? (
                    <Check className="size-3.5" />
                  ) : !accessible ? (
                    <Lock className="size-3" />
                  ) : (
                    i + 1
                  )}
                </span>
                <span className="hidden whitespace-nowrap font-medium sm:inline">
                  {s.label}
                </span>
                <span className="whitespace-nowrap font-medium sm:hidden">
                  {s.short}
                </span>
              </button>
              {i < STEPS.length - 1 ? (
                <span
                  className={cn(
                    "mx-0.5 h-px w-4 shrink-0 md:w-8",
                    i < furthest ? "bg-chart-3/50" : "bg-border",
                  )}
                  aria-hidden="true"
                />
              ) : null}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
