// Static UI configuration and sample catalog metadata.

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
    name: "Ganga Delta - Kolkata Sector",
    sensor: "LISS-IV (Resourcesat-2A)",
    region: "West Bengal, India",
    acquired: "2026-06-18 10:42 IST",
    resolution: "5.8 m / pixel",
    area: "1,204 km2",
    cloudCover: 42.7,
    size: "486 MB",
    coords: "22.5726N / 88.3639E",
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
    name: "Krishna Basin - Vijayawada",
    sensor: "LISS-IV (Resourcesat-2A)",
    region: "Andhra Pradesh, India",
    acquired: "2026-05-21 11:08 IST",
    resolution: "5.8 m / pixel",
    area: "986 km2",
    cloudCover: 58.1,
    size: "402 MB",
    coords: "16.5062N / 80.6480E",
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
    name: "Brahmaputra Floodplain - Guwahati",
    sensor: "LISS-IV (Resourcesat-2A)",
    region: "Assam, India",
    acquired: "2026-04-07 09:55 IST",
    resolution: "5.8 m / pixel",
    area: "1,512 km2",
    cloudCover: 33.4,
    size: "551 MB",
    coords: "26.1445N / 91.7362E",
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

export type ModelOption = {
  id: string
  name: string
  desc: string
  speed: "Fast" | "Balanced" | "Best Quality"
}

export const MODELS: ModelOption[] = [
  {
    id: "diffcr-v2",
    name: "Attention ResUNet",
    desc: "Production cloud-removal model with multimodal satellite fusion.",
    speed: "Best Quality",
  },
  {
    id: "gan-mux",
    name: "Attention ResUNet Balanced",
    desc: "Balanced operating point for CPU-first deployments.",
    speed: "Balanced",
  },
  {
    id: "unet-lite",
    name: "Attention ResUNet Preview",
    desc: "Lower-latency preview profile using smaller tiles.",
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
  { id: "temporal", label: "Temporal Composite", desc: "Historical cloud-free reference", enabled: true },
  { id: "dem", label: "CartoDEM v3", desc: "Terrain elevation prior", enabled: true },
  { id: "spectral", label: "Spectral Priors", desc: "NDVI / NDWI band guidance", enabled: false },
]

export type ReconConfig = {
  model: string
  sources: FusionSource[]
  fidelity: number
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
    desc: "Per-pixel reconstruction confidence",
  },
  {
    id: "cloudmask",
    name: "cloud_mask.geojson",
    type: "GeoJSON",
    size: "1.2 MB",
    desc: "Detected cloud and shadow polygons",
  },
  {
    id: "metrics",
    name: "validation_metrics.json",
    type: "JSON",
    size: "8 KB",
    desc: "Full PSNR, SSIM, SAM, and NDVI report",
  },
  {
    id: "report",
    name: "reconstruction_report.pdf",
    type: "PDF",
    size: "3.4 MB",
    desc: "Human-readable summary for stakeholders",
  },
]
