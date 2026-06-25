import type { ReactNode } from "react"
import { cn } from "@/lib/utils"

export function Panel({
  title,
  badge,
  icon,
  children,
  className,
}: {
  title: string
  badge?: ReactNode
  icon?: ReactNode
  children: ReactNode
  className?: string
}) {
  return (
    <section
      className={cn(
        "glass flex flex-col overflow-hidden rounded-xl border border-border shadow-xl shadow-black/20",
        className,
      )}
    >
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        {icon}
        <h2 className="text-sm font-semibold tracking-tight text-foreground">
          {title}
        </h2>
        {badge ? <div className="ml-auto">{badge}</div> : null}
      </div>
      <div className="flex flex-1 flex-col gap-4 p-4">{children}</div>
    </section>
  )
}

export function StatItem({
  label,
  value,
  hint,
}: {
  label: string
  value: ReactNode
  hint?: ReactNode
}) {
  return (
    <div className="flex items-baseline justify-between gap-3 border-b border-border/60 py-2 last:border-0">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="flex items-center gap-1.5 text-sm font-medium text-foreground">
        {value}
        {hint}
      </span>
    </div>
  )
}

const TONE_CLASSES: Record<string, string> = {
  primary: "bg-primary/15 text-primary ring-primary/30",
  accent: "bg-accent/15 text-accent ring-accent/30",
  green: "bg-chart-3/15 text-chart-3 ring-chart-3/30",
  red: "bg-destructive/15 text-destructive ring-destructive/30",
  muted: "bg-secondary text-muted-foreground ring-border",
}

export function Badge({
  children,
  tone = "muted",
  dot = false,
}: {
  children: ReactNode
  tone?: keyof typeof TONE_CLASSES | string
  dot?: boolean
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1 ring-inset",
        TONE_CLASSES[tone] ?? TONE_CLASSES.muted,
      )}
    >
      {dot ? <span className="size-1.5 rounded-full bg-current" /> : null}
      {children}
    </span>
  )
}

export function MetricCard({
  label,
  value,
  unit,
  sub,
  tone = "primary",
}: {
  label: string
  value: string
  unit?: string
  sub?: ReactNode
  tone?: keyof typeof TONE_CLASSES
}) {
  return (
    <div className="rounded-lg border border-border bg-secondary/30 p-3">
      <p className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
      <p className="mt-1 flex items-baseline gap-1">
        <span
          className={cn(
            "text-xl font-semibold tabular-nums",
            tone === "accent"
              ? "text-accent"
              : tone === "green"
                ? "text-chart-3"
                : tone === "red"
                  ? "text-destructive"
                  : "text-foreground",
          )}
        >
          {value}
        </span>
        {unit ? (
          <span className="text-xs text-muted-foreground">{unit}</span>
        ) : null}
      </p>
      {sub ? <p className="mt-1 text-[11px] text-muted-foreground">{sub}</p> : null}
    </div>
  )
}

export function ProgressBar({
  value,
  tone = "primary",
}: {
  value: number
  tone?: "primary" | "accent" | "green"
}) {
  const color =
    tone === "accent"
      ? "bg-accent"
      : tone === "green"
        ? "bg-chart-3"
        : "bg-primary"
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
      <div
        className={cn("h-full rounded-full transition-all duration-500", color)}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  )
}
