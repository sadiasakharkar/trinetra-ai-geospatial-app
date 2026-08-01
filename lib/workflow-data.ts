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
  preview_image_url?: string
  thumbnail_url?: string
  cloud_mask_url?: string
  confidence_map_url?: string
  reconstructed_image_url?: string
  clear_reference_url?: string
  historical_image_url?: string
  dataset_json_url?: string
  metadata?: Record<string, unknown>
  geographic_info?: Record<string, unknown>
  temporal: { date: string; img: string; clear: boolean }[]
}

export const DATASETS: Dataset[] = [
  {
    id: "sample_01",
    name: "Ganga Delta Fog Event",
    sensor: "Terra MODIS / Landsat 7 ETM+",
    region: "Sundarbans, Ganga-Brahmaputra Delta",
    acquired: "2026-01-06",
    resolution: "250 m MODIS preview / 30 m Landsat reference",
    area: "Sundarbans delta and Bay of Bengal cloud streets",
    cloudCover: 58.3,
    size: "Bundled scene",
    coords: "22.0 N, 89.5 E",
    thumb: "/datasets/sample_01/thumbnail.png",
    reconstructed: "/datasets/sample_01/reconstructed.png",
    sar: "/datasets/sample_01/cloud_mask.png",
    dem: "/datasets/sample_01/historical.png",
    preview_image_url: "/datasets/sample_01/cloudy.png",
    thumbnail_url: "/datasets/sample_01/thumbnail.png",
    cloud_mask_url: "/datasets/sample_01/cloud_mask.png",
    confidence_map_url: "/datasets/sample_01/confidence_heatmap.png",
    reconstructed_image_url: "/datasets/sample_01/reconstructed.png",
    clear_reference_url: "/datasets/sample_01/clear_reference.png",
    historical_image_url: "/datasets/sample_01/historical.png",
    dataset_json_url: "/datasets/sample_01/dataset.json",
    temporal: [
      { date: "2000-02-28", img: "/datasets/sample_01/historical.png", clear: true },
      { date: "2026-01-06", img: "/datasets/sample_01/cloudy.png", clear: false },
      { date: "Analysis output", img: "/datasets/sample_01/reconstructed.png", clear: true },
    ],
  },
  {
    id: "sample_02",
    name: "Krishna River Floodplain",
    sensor: "Terra MODIS",
    region: "Andhra Pradesh, Krishna River Basin",
    acquired: "2009-10-05",
    resolution: "250-500 m MODIS false-color composite",
    area: "Krishna River delta and flood channels",
    cloudCover: 38.3,
    size: "Bundled scene",
    coords: "16.2 N, 80.8 E",
    thumb: "/datasets/sample_02/thumbnail.png",
    reconstructed: "/datasets/sample_02/reconstructed.png",
    sar: "/datasets/sample_02/cloud_mask.png",
    dem: "/datasets/sample_02/historical.png",
    preview_image_url: "/datasets/sample_02/cloudy.png",
    thumbnail_url: "/datasets/sample_02/thumbnail.png",
    cloud_mask_url: "/datasets/sample_02/cloud_mask.png",
    confidence_map_url: "/datasets/sample_02/confidence_heatmap.png",
    reconstructed_image_url: "/datasets/sample_02/reconstructed.png",
    clear_reference_url: "/datasets/sample_02/clear_reference.png",
    historical_image_url: "/datasets/sample_02/historical.png",
    dataset_json_url: "/datasets/sample_02/dataset.json",
    temporal: [
      { date: "2009-09-10", img: "/datasets/sample_02/historical.png", clear: true },
      { date: "2009-10-05", img: "/datasets/sample_02/cloudy.png", clear: false },
      { date: "Analysis output", img: "/datasets/sample_02/reconstructed.png", clear: true },
    ],
  },
  {
    id: "sample_03",
    name: "Brahmaputra Floodplain",
    sensor: "Aqua MODIS",
    region: "Assam, Northeast India",
    acquired: "2008-09-07",
    resolution: "500 m MODIS false-color composite",
    area: "Kaziranga-Brahmaputra braided floodplain",
    cloudCover: 32.1,
    size: "Bundled scene",
    coords: "26.5 N, 92.8 E",
    thumb: "/datasets/sample_03/thumbnail.png",
    reconstructed: "/datasets/sample_03/reconstructed.png",
    sar: "/datasets/sample_03/cloud_mask.png",
    dem: "/datasets/sample_03/historical.png",
    preview_image_url: "/datasets/sample_03/cloudy.png",
    thumbnail_url: "/datasets/sample_03/thumbnail.png",
    cloud_mask_url: "/datasets/sample_03/cloud_mask.png",
    confidence_map_url: "/datasets/sample_03/confidence_heatmap.png",
    reconstructed_image_url: "/datasets/sample_03/reconstructed.png",
    clear_reference_url: "/datasets/sample_03/clear_reference.png",
    historical_image_url: "/datasets/sample_03/historical.png",
    dataset_json_url: "/datasets/sample_03/dataset.json",
    temporal: [
      { date: "2008-09-07", img: "/datasets/sample_03/historical.png", clear: true },
      { date: "2008-09-07", img: "/datasets/sample_03/cloudy.png", clear: false },
      { date: "Analysis output", img: "/datasets/sample_03/reconstructed.png", clear: true },
    ],
  },
  {
    id: "sample_04",
    name: "Himalayan Snow Corridor",
    sensor: "Terra MODIS",
    region: "Central Himalaya and Tibetan Plateau",
    acquired: "2015-11-20",
    resolution: "250-500 m MODIS natural-color composite",
    area: "Snow, haze, and high-relief Himalayan terrain",
    cloudCover: 11.8,
    size: "Bundled scene",
    coords: "28.5 N, 86.9 E",
    thumb: "/datasets/sample_04/thumbnail.png",
    reconstructed: "/datasets/sample_04/reconstructed.png",
    sar: "/datasets/sample_04/cloud_mask.png",
    dem: "/datasets/sample_04/historical.png",
    preview_image_url: "/datasets/sample_04/cloudy.png",
    thumbnail_url: "/datasets/sample_04/thumbnail.png",
    cloud_mask_url: "/datasets/sample_04/cloud_mask.png",
    confidence_map_url: "/datasets/sample_04/confidence_heatmap.png",
    reconstructed_image_url: "/datasets/sample_04/reconstructed.png",
    clear_reference_url: "/datasets/sample_04/clear_reference.png",
    historical_image_url: "/datasets/sample_04/historical.png",
    dataset_json_url: "/datasets/sample_04/dataset.json",
    temporal: [
      { date: "2015-11-20", img: "/datasets/sample_04/historical.png", clear: true },
      { date: "2015-11-20", img: "/datasets/sample_04/cloudy.png", clear: false },
      { date: "Analysis output", img: "/datasets/sample_04/reconstructed.png", clear: true },
    ],
  },
  {
    id: "sample_05",
    name: "Rajasthan Thar Solar Complex",
    sensor: "Landsat 8 OLI",
    region: "Bhadla, Rajasthan Desert",
    acquired: "2022-01-26",
    resolution: "30 m Landsat natural-color composite",
    area: "Bhadla Solar Park and arid desert infrastructure",
    cloudCover: 51.8,
    size: "Bundled scene",
    coords: "27.5 N, 71.9 E",
    thumb: "/datasets/sample_05/thumbnail.png",
    reconstructed: "/datasets/sample_05/reconstructed.png",
    sar: "/datasets/sample_05/cloud_mask.png",
    dem: "/datasets/sample_05/historical.png",
    preview_image_url: "/datasets/sample_05/cloudy.png",
    thumbnail_url: "/datasets/sample_05/thumbnail.png",
    cloud_mask_url: "/datasets/sample_05/cloud_mask.png",
    confidence_map_url: "/datasets/sample_05/confidence_heatmap.png",
    reconstructed_image_url: "/datasets/sample_05/reconstructed.png",
    clear_reference_url: "/datasets/sample_05/clear_reference.png",
    historical_image_url: "/datasets/sample_05/historical.png",
    dataset_json_url: "/datasets/sample_05/dataset.json",
    temporal: [
      { date: "2022-01-26", img: "/datasets/sample_05/historical.png", clear: true },
      { date: "2022-01-26", img: "/datasets/sample_05/cloudy.png", clear: false },
      { date: "Analysis output", img: "/datasets/sample_05/reconstructed.png", clear: true },
    ],
  },
  {
    id: "sample_06",
    name: "Kerala Coast Flood Scene",
    sensor: "Sentinel-2 MSI / Landsat 8 OLI",
    region: "Kochi-Periyar lowlands, Kerala Coast",
    acquired: "2018-08-22",
    resolution: "10-30 m false-color flood composite",
    area: "Coastal wetlands, Western Ghats foothills, floodplain channels",
    cloudCover: 25.3,
    size: "Bundled scene",
    coords: "10.1 N, 76.3 E",
    thumb: "/datasets/sample_06/thumbnail.png",
    reconstructed: "/datasets/sample_06/reconstructed.png",
    sar: "/datasets/sample_06/cloud_mask.png",
    dem: "/datasets/sample_06/historical.png",
    preview_image_url: "/datasets/sample_06/cloudy.png",
    thumbnail_url: "/datasets/sample_06/thumbnail.png",
    cloud_mask_url: "/datasets/sample_06/cloud_mask.png",
    confidence_map_url: "/datasets/sample_06/confidence_heatmap.png",
    reconstructed_image_url: "/datasets/sample_06/reconstructed.png",
    clear_reference_url: "/datasets/sample_06/clear_reference.png",
    historical_image_url: "/datasets/sample_06/historical.png",
    dataset_json_url: "/datasets/sample_06/dataset.json",
    temporal: [
      { date: "2018-02-06", img: "/datasets/sample_06/historical.png", clear: true },
      { date: "2018-08-22", img: "/datasets/sample_06/cloudy.png", clear: false },
      { date: "Analysis output", img: "/datasets/sample_06/reconstructed.png", clear: true },
    ],
  }
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
  {
    id: "preview",
    name: "preview.png",
    type: "PNG (RGB)",
    size: "1.1 MB",
    desc: "Quick visual preview of the reconstructed output",
  },
  {
    id: "difference",
    name: "difference.png",
    type: "PNG (RGB)",
    size: "1.1 MB",
    desc: "Before/after difference map for visual QA",
  },
]
