"use client"

import {
  UploadCloud,
  CloudRain,
  MapPin,
  Calendar,
  HardDrive,
  CheckCircle2,
  Loader2,
  X,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { SafeImage } from "@/components/ui/safe-image"
import { useWorkflow } from "./workflow-context"
import { StepHeader, StepFooter, StepCard } from "./step-shell"
import { Badge, ProgressBar } from "@/components/dashboard/ui"

export function StepUpload() {
  const {
    dataset,
    selectDataset,
    uploadFile,
    clearDataset,
    availableDatasets,
    uploading,
    uploadProgress,
    next,
  } = useWorkflow()

  const ready = dataset !== null && !uploading && uploadProgress >= 100

  return (
    <div>
      <StepHeader
        eyebrow="Step 1 of 6"
        title="Upload Satellite Dataset"
        description="Select a cloud-contaminated LISS-IV scene to reconstruct. Choose a sample acquisition from the archive or upload your own raster."
        icon={<UploadCloud className="size-5 text-primary" aria-hidden="true" />}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <StepCard className="lg:col-span-1">
          <input
            type="file"
            id="real-file-upload"
            accept="image/*,.tif,.tiff,.jp2"
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                uploadFile(e.target.files[0])
              }
            }}
          />
          <label
            htmlFor="real-file-upload"
            className="flex h-full min-h-48 cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-border bg-secondary/20 p-6 text-center transition-colors hover:border-primary/50 hover:bg-secondary/40"
          >
            <div className="flex size-12 items-center justify-center rounded-full bg-primary/15 ring-1 ring-primary/30">
              <UploadCloud className="size-6 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">
                Drop GeoTIFF or image here
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                or click to browse - .tif, .tiff, .png, .jpg, .jp2
              </p>
            </div>
            <span className="rounded-md bg-primary/15 px-3 py-1.5 text-xs font-semibold text-primary">
              Upload Custom Image
            </span>
          </label>
          <p className="mt-3 text-center text-[11px] text-muted-foreground">
            FastAPI mode - uploads are ingested by the backend reconstruction pipeline
          </p>
        </StepCard>

        <div className="lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-foreground">
              Sample and Uploaded Archive
            </h2>
            <span className="text-xs text-muted-foreground">
              {availableDatasets.length} scenes available
            </span>
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {availableDatasets.map((d) => {
              const selected = dataset?.id === d.id
              return (
                <button
                  key={d.id}
                  onClick={() => selectDataset(d)}
                  className={cn(
                    "group flex flex-col overflow-hidden rounded-xl border text-left transition-all",
                    selected
                      ? "border-primary ring-1 ring-primary"
                      : "border-border hover:border-primary/50",
                  )}
                >
                  <div className="relative aspect-video w-full overflow-hidden bg-black/40">
                    <SafeImage
                      src={d.thumbnail_url || d.preview_image_url || d.thumb}
                      alt={`Preview of ${d.name}`}
                      fill
                      sizes="(max-width: 640px) 100vw, 33vw"
                      className="object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                    <span className="absolute right-2 top-2">
                      <Badge tone="accent" dot>
                        {d.cloudCover}% cloud
                      </Badge>
                    </span>
                    {selected ? (
                      <span className="absolute left-2 top-2 flex size-6 items-center justify-center rounded-full bg-primary text-primary-foreground">
                        <CheckCircle2 className="size-4" />
                      </span>
                    ) : null}
                  </div>
                  <div className="glass flex flex-1 flex-col gap-2 p-3">
                    <p className="text-sm font-semibold text-foreground">
                      {d.name}
                    </p>
                    <div className="flex flex-col gap-1 text-[11px] text-muted-foreground">
                      <span className="flex items-center gap-1.5">
                        <MapPin className="size-3" /> {d.region}
                      </span>
                      <span className="flex items-center gap-1.5">
                        <Calendar className="size-3" /> {d.acquired}
                      </span>
                      <span className="flex items-center gap-1.5">
                        <HardDrive className="size-3" /> {d.size} - {d.area}
                      </span>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {dataset ? (
        <StepCard className="mt-4">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-secondary">
              {uploading ? (
                <Loader2 className="size-5 animate-spin text-primary" />
              ) : (
                <CheckCircle2 className="size-5 text-chart-3" />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-foreground">
                  {uploading ? `Ingesting ${dataset.name}...` : `${dataset.name} ready`}
                </p>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-muted-foreground">
                    {uploadProgress}%
                  </span>
                  <button
                    onClick={(e) => {
                      e.preventDefault()
                      clearDataset()
                    }}
                    className="rounded-md p-1 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                    aria-label="Delete dataset"
                  >
                    <X className="size-4" />
                  </button>
                </div>
              </div>
              <div className="mt-2">
                <ProgressBar value={uploadProgress} tone={ready ? "green" : "primary"} />
              </div>
              <p className="mt-1.5 flex items-center gap-1.5 text-[11px] text-muted-foreground">
                <CloudRain className="size-3 text-accent" />
                {dataset.sensor} - {dataset.resolution} - {dataset.coords}
              </p>
            </div>
          </div>
        </StepCard>
      ) : null}

      <StepFooter
        hideBack
        onNext={next}
        nextDisabled={!ready}
        nextLabel="Configure Reconstruction"
        nextHint={
          !dataset
            ? "Select a dataset to continue"
            : uploading
              ? "Waiting for ingestion to finish..."
              : undefined
        }
      />
    </div>
  )
}
