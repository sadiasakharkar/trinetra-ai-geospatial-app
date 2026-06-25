// ============================================================================
// Mock datasets, configuration options, and simulated "API" responses.
// Everything here is deterministic mock data for a hackathon demonstration.
// No real network calls are made.
// ============================================================================

export type Dataset = {
  id: string
  name: string
  sensor: string
  region: string
  acquired: string
  resolution: string
  area: string
  cloudCover: number
  size: string
  coords: string
  thumb: string
  reconstructed: string
  sar: string
  dem: string
  temporal: { date: string; img: string; clear: boolean }[]
}

export const DATASETS: Dataset[] = [
  {
    id: "LISS4-2026-0618-DT04",
    name: "Ganga Delta — Kolkata Sector",
    sensor: "LISS-IV (Resourcesat-2A)",
    region: "West Bengal, India",
    acquired: "2026-06-18 10:42 IST",
    resolution: "5.8 m / pixel",
    area: "1,204 km²",
    cloudCover: 42.7,
    size: "486 MB",
    coords: "22.5726°N · 88.3639°E",
    thumb: "/images/liss-iv-cloudy.png",
    reconstructed: "/images/liss-iv-reconstructed.png",
    sar: "/images/sentinel-sar.png",
    dem: "/images/dem-terrain.png",
    temporal: [
      { date: "Mar 2026", img: "/images/temporal-1.png", clear: true },
      { date: "Apr 2026", img: "/images/temporal-2.png", clear: true },
      { date: "May 2026", img: "/images/liss-iv-reconstructed.png", clear: true },
      { date: "Jun 2026", img: "/images/temporal-1.png", clear: false },
    ],
  },
  {
    id: "LISS4-2026-0521-MH12",
    name: "Krishna Basin — Vijayawada",
    sensor: "LISS-IV (Resourcesat-2A)",
    region: "Andhra Pradesh, India",
    acquired: "2026-05-21 11:08 IST",
    resolution: "5.8 m / pixel",
    area: "986 km²",
    cloudCover: 58.1,
    size: "402 MB",
    coords: "16.5062°N · 80.6480°E",
    thumb: "/images/temporal-1.png",
    reconstructed: "/images/liss-iv-reconstructed.png",
    sar: "/images/sentinel-sar.png",
    dem: "/images/dem-terrain.png",
    temporal: [
      { date: "Feb 2026", img: "/images/temporal-2.png", clear: true },
      { date: "Mar 2026", img: "/images/temporal-1.png", clear: true },
      { date: "Apr 2026", img: "/images/liss-iv-reconstructed.png", clear: true },
      { date: "May 2026", img: "/images/temporal-1.png", clear: false },
    ],
  },
  {
    id: "LISS4-2026-0407-AS09",
    name: "Brahmaputra Floodplain — Guwahati",
    sensor: "LISS-IV (Resourcesat-2A)",
    region: "Assam, India",
    acquired: "2026-04-07 09:55 IST",
    resolution: "5.8 m / pixel",
    area: "1,512 km²",
    cloudCover: 33.4,
    size: "551 MB",
    coords: "26.1445°N · 91.7362°E",
    thumb: "/images/temporal-2.png",
    reconstructed: "/images/liss-iv-reconstructed.png",
    sar: "/images/sentinel-sar.png",
    dem: "/images/dem-terrain.png",
    temporal: [
      { date: "Jan 2026", img: "/images/temporal-1.png", clear: true },
      { date: "Feb 2026", img: "/images/temporal-2.png", clear: true },
      { date: "Mar 2026", img: "/images/liss-iv-reconstructed.png", clear: true },
      { date: "Apr 2026", img: "/images/temporal-2.png", clear: false },
    ],
  },
]

// ---------------------------------------------------------------------------
// Reconstruction configuration
// ---------------------------------------------------------------------------

export type ModelOption = {
  id: string
  name: string
  desc: string
  speed: "Fast" | "Balanced" | "Best Quality"
}

export const MODELS: ModelOption[] = [
  {
    id: "diffcr-v2",
    name: "DiffCR-v2.1",
    desc: "Diffusion cloud-removal with SAR conditioning. Best fidelity.",
    speed: "Best Quality",
  },
  {
    id: "gan-mux",
    name: "MUX-GAN",
    desc: "Multimodal GAN fusion. Strong balance of speed and detail.",
    speed: "Balanced",
  },
  {
    id: "unet-lite",
    name: "U-Net Lite",
    desc: "Lightweight inpainting. Fastest, good for previews.",
    speed: "Fast",
  },
]

export type FusionSource = {
  id: string
  label: string
  desc: string
  enabled: boolean
}

export const DEFAULT_SOURCES: FusionSource[] = [
  { id: "sar", label: "Sentinel-1 SAR", desc: "VV + VH radar backscatter", enabled: true },
  { id: "temporal", label: "Temporal Composite", desc: "4 cloud-free reference scenes", enabled: true },
  { id: "dem", label: "CartoDEM v3", desc: "Terrain elevation prior", enabled: true },
  { id: "spectral", label: "Spectral Priors", desc: "NDVI / NDWI band guidance", enabled: false },
]

export type ReconConfig = {
  model: string
  sources: FusionSource[]
  fidelity: number // 0-100
  tileSize: number
  outputFormat: string
  preserveNdvi: boolean
}

export const DEFAULT_CONFIG: ReconConfig = {
  model: "diffcr-v2",
  sources: DEFAULT_SOURCES,
  fidelity: 75,
  tileSize: 256,
  outputFormat: "GeoTIFF",
  preserveNdvi: true,
}

export const OUTPUT_FORMATS = ["GeoTIFF", "Cloud-Optimized GeoTIFF", "PNG (RGB)", "JPEG2000"]
export const TILE_SIZES = [128, 256, 512]

// ---------------------------------------------------------------------------
// Simulated processing log lines
// ---------------------------------------------------------------------------

export const LOG_LINES: { at: number; level: "info" | "ok" | "warn"; text: string }[] = [
  { at: 0, level: "info", text: "Initializing reconstruction pipeline…" },
  { at: 4, level: "info", text: "Loading scene tiles into GPU memory (4× A100)" },
  { at: 10, level: "ok", text: "Cloud mask generated · 42.7% contamination detected" },
  { at: 18, level: "info", text: "Co-registering Sentinel-1 SAR (VV+VH)" },
  { at: 26, level: "ok", text: "SAR alignment RMSE 0.34 px · within tolerance" },
  { at: 34, level: "info", text: "Fetching 4 temporal reference composites" },
  { at: 42, level: "info", text: "Sampling DiffCR-v2.1 latent diffusion · step 1/8" },
  { at: 54, level: "info", text: "Diffusion step 4/8 · denoising cloud regions" },
  { at: 66, level: "warn", text: "Low-confidence patch at tile [142] · increasing guidance" },
  { at: 74, level: "info", text: "Diffusion step 7/8 · spectral harmonization" },
  { at: 84, level: "ok", text: "NDVI preservation check passed (97.6%)" },
  { at: 92, level: "info", text: "Stitching 256 reconstructed tiles" },
  { at: 98, level: "ok", text: "Validation metrics computed · PSNR 34.8 dB" },
  { at: 100, level: "ok", text: "Reconstruction complete · outputs ready for export" },
]

// ---------------------------------------------------------------------------
// Validation metrics & chart series
// ---------------------------------------------------------------------------

export const VALIDATION = {
  headline: [
    { label: "PSNR", value: "34.8", unit: "dB", tone: "green" as const, sub: "Target ≥ 30 dB" },
    { label: "SSIM", value: "0.931", unit: "", tone: "green" as const, sub: "Structural similarity" },
    { label: "SAM", value: "3.42", unit: "°", tone: "primary" as const, sub: "Spectral angle" },
    { label: "NDVI Preservation", value: "97.6", unit: "%", tone: "green" as const, sub: "Vegetation index" },
  ],
  // PSNR / SSIM trend across diffusion steps
  trend: [
    { step: "S1", psnr: 18.2, ssim: 0.52 },
    { step: "S2", psnr: 22.6, ssim: 0.64 },
    { step: "S3", psnr: 26.1, ssim: 0.73 },
    { step: "S4", psnr: 29.4, ssim: 0.81 },
    { step: "S5", psnr: 31.8, ssim: 0.87 },
    { step: "S6", psnr: 33.5, ssim: 0.91 },
    { step: "S7", psnr: 34.4, ssim: 0.925 },
    { step: "S8", psnr: 34.8, ssim: 0.931 },
  ],
  // Per-band spectral fidelity (reconstructed vs reference)
  bands: [
    { band: "Green", recon: 0.96, ref: 1 },
    { band: "Red", recon: 0.94, ref: 1 },
    { band: "NIR", recon: 0.97, ref: 1 },
    { band: "SWIR", recon: 0.91, ref: 1 },
  ],
  // Pixel classification breakdown
  classes: [
    { label: "Clear (original)", pct: 57.3, tone: "primary" as const },
    { label: "Reconstructed", pct: 38.9, tone: "green" as const },
    { label: "Low-confidence", pct: 3.8, tone: "accent" as const },
  ],
}

export type DownloadArtifact = {
  id: string
  name: string
  type: string
  size: string
  desc: string
}

export const DOWNLOADS: DownloadArtifact[] = [
  {
    id: "recon-tiff",
    name: "reconstructed_scene.tif",
    type: "GeoTIFF",
    size: "486 MB",
    desc: "Cloud-free reconstructed multispectral raster",
  },
  {
    id: "confidence",
    name: "confidence_map.tif",
    type: "GeoTIFF",
    size: "62 MB",
    desc: "Per-pixel reconstruction confidence (0–1)",
  },
  {
    id: "cloudmask",
    name: "cloud_mask.geojson",
    type: "GeoJSON",
    size: "1.2 MB",
    desc: "Detected cloud + shadow polygons",
  },
  {
    id: "metrics",
    name: "validation_metrics.json",
    type: "JSON",
    size: "8 KB",
    desc: "Full PSNR / SSIM / SAM / NDVI report",
  },
  {
    id: "report",
    name: "reconstruction_report.pdf",
    type: "PDF",
    size: "3.4 MB",
    desc: "Human-readable summary for stakeholders",
  },
]

// ---------------------------------------------------------------------------
// Simulated async "API" helpers — resolve after a delay to mimic latency.
// ---------------------------------------------------------------------------

export function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms))
}

// Generate a small mock JSON payload for download
export function buildMetricsJson() {
  return JSON.stringify(
    {
      job: "recon-job-7F3A",
      generatedAt: new Date().toISOString(),
      metrics: {
        psnr_db: 34.8,
        ssim: 0.931,
        sam_deg: 3.42,
        ndvi_preservation_pct: 97.6,
      },
      bands: VALIDATION.bands,
      classes: VALIDATION.classes,
    },
    null,
    2,
  )
}
