"use client"

// Lightweight, dependency-free SVG charts themed with design tokens.

export function LineChart({
  data,
  height = 180,
}: {
  data: { step: string; psnr: number; ssim: number }[]
  height?: number
}) {
  const w = 320
  const h = height
  const padX = 28
  const padY = 18
  const innerW = w - padX * 2
  const innerH = h - padY * 2

  const maxPsnr = 40
  const psnrPts = data.map((d, i) => {
    const x = padX + (i / (data.length - 1)) * innerW
    const y = padY + innerH - (d.psnr / maxPsnr) * innerH
    return [x, y] as const
  })
  const ssimPts = data.map((d, i) => {
    const x = padX + (i / (data.length - 1)) * innerW
    const y = padY + innerH - d.ssim * innerH
    return [x, y] as const
  })

  const toPath = (pts: readonly (readonly [number, number])[]) =>
    pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p[0]} ${p[1]}`).join(" ")

  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      className="h-auto w-full"
      role="img"
      aria-label="PSNR and SSIM convergence across diffusion steps"
    >
      {[0, 0.25, 0.5, 0.75, 1].map((g) => (
        <line
          key={g}
          x1={padX}
          x2={w - padX}
          y1={padY + innerH * g}
          y2={padY + innerH * g}
          className="stroke-border"
          strokeWidth={0.5}
        />
      ))}
      {/* area under PSNR */}
      <path
        d={`${toPath(psnrPts)} L ${psnrPts[psnrPts.length - 1][0]} ${
          padY + innerH
        } L ${psnrPts[0][0]} ${padY + innerH} Z`}
        className="fill-primary/10"
      />
      <path d={toPath(psnrPts)} className="fill-none stroke-primary" strokeWidth={2} />
      <path d={toPath(ssimPts)} className="fill-none stroke-chart-3" strokeWidth={2} strokeDasharray="4 3" />
      {psnrPts.map((p, i) => (
        <circle key={i} cx={p[0]} cy={p[1]} r={2.5} className="fill-primary" />
      ))}
      {ssimPts.map((p, i) => (
        <circle key={i} cx={p[0]} cy={p[1]} r={2.5} className="fill-chart-3" />
      ))}
      {data.map((d, i) => (
        <text
          key={d.step}
          x={padX + (i / (data.length - 1)) * innerW}
          y={h - 4}
          textAnchor="middle"
          className="fill-muted-foreground text-[8px]"
        >
          {d.step}
        </text>
      ))}
    </svg>
  )
}

export function BarChart({
  data,
}: {
  data: { band: string; recon: number; ref: number }[]
}) {
  const w = 320
  const h = 180
  const padX = 30
  const padY = 16
  const innerW = w - padX * 2
  const innerH = h - padY * 2
  const groupW = innerW / data.length
  const barW = 14

  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      className="h-auto w-full"
      role="img"
      aria-label="Per-band spectral fidelity, reconstructed versus reference"
    >
      {[0, 0.5, 1].map((g) => (
        <line
          key={g}
          x1={padX}
          x2={w - padX}
          y1={padY + innerH * g}
          y2={padY + innerH * g}
          className="stroke-border"
          strokeWidth={0.5}
        />
      ))}
      {data.map((d, i) => {
        const cx = padX + groupW * i + groupW / 2
        const refH = d.ref * innerH
        const reconH = d.recon * innerH
        return (
          <g key={d.band}>
            <rect
              x={cx - barW - 2}
              y={padY + innerH - refH}
              width={barW}
              height={refH}
              rx={2}
              className="fill-secondary"
            />
            <rect
              x={cx + 2}
              y={padY + innerH - reconH}
              width={barW}
              height={reconH}
              rx={2}
              className="fill-primary"
            />
            <text
              x={cx}
              y={h - 3}
              textAnchor="middle"
              className="fill-muted-foreground text-[8px]"
            >
              {d.band}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

export function DonutChart({
  data,
}: {
  data: { label: string; pct: number; tone: "primary" | "green" | "accent" }[]
}) {
  const size = 150
  const r = 56
  const cx = size / 2
  const cy = size / 2
  const circ = 2 * Math.PI * r
  const segments = data.reduce<
    ({ label: string; pct: number; tone: "primary" | "green" | "accent" } & { len: number; offset: number })[]
  >((acc, d) => {
    const len = (d.pct / 100) * circ
    const offset = acc.reduce((sum, segment) => sum + segment.len, 0)
    return [...acc, { ...d, len, offset }]
  }, [])
  const toneClass = {
    primary: "stroke-primary",
    green: "stroke-chart-3",
    accent: "stroke-accent",
  }

  return (
    <div className="flex items-center gap-4">
      <svg
        viewBox={`0 0 ${size} ${size}`}
        className="size-32 -rotate-90"
        role="img"
        aria-label="Pixel classification breakdown"
      >
        {segments.map((d) => (
          <circle
            key={d.label}
            cx={cx}
            cy={cy}
            r={r}
            fill="none"
            strokeWidth={14}
            className={toneClass[d.tone]}
            strokeDasharray={`${d.len} ${circ - d.len}`}
            strokeDashoffset={-d.offset}
          />
        ))}
      </svg>
      <div className="flex flex-col gap-2">
        {data.map((d) => (
          <div key={d.label} className="flex items-center gap-2 text-xs">
            <span
              className={`size-2.5 rounded-sm ${
                d.tone === "primary"
                  ? "bg-primary"
                  : d.tone === "green"
                    ? "bg-chart-3"
                    : "bg-accent"
              }`}
            />
            <span className="text-muted-foreground">{d.label}</span>
            <span className="ml-auto font-medium tabular-nums text-foreground">
              {d.pct}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
