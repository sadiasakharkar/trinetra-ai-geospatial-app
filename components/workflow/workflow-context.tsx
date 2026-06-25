"use client"

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react"
import {
  DATASETS,
  DEFAULT_CONFIG,
  LOG_LINES,
  type Dataset,
  type ReconConfig,
} from "@/lib/mock"

export type StepId =
  | "upload"
  | "configure"
  | "run"
  | "validation"
  | "compare"
  | "download"

export const STEPS: { id: StepId; label: string; short: string }[] = [
  { id: "upload", label: "Upload Dataset", short: "Upload" },
  { id: "configure", label: "Configure", short: "Configure" },
  { id: "run", label: "Run & Progress", short: "Run" },
  { id: "validation", label: "Validation", short: "Validate" },
  { id: "compare", label: "Compare", short: "Compare" },
  { id: "download", label: "Download", short: "Export" },
]

export type LogEntry = { level: "info" | "ok" | "warn"; text: string; time: string }
export type JobStatus = "idle" | "running" | "paused" | "complete"

type WorkflowState = {
  // navigation
  step: StepId
  furthest: number
  goTo: (id: StepId) => void
  next: () => void
  back: () => void
  canAccess: (id: StepId) => boolean

  // dataset
  dataset: Dataset | null
  selectDataset: (d: Dataset) => void
  uploading: boolean
  uploadProgress: number
  simulateUpload: (d: Dataset) => void

  // config
  config: ReconConfig
  setConfig: (c: ReconConfig) => void

  // job
  status: JobStatus
  progress: number
  logs: LogEntry[]
  startJob: () => void
  pauseJob: () => void
  resetJob: () => void

  // downloads
  downloaded: string[]
  markDownloaded: (id: string) => void
}

const Ctx = createContext<WorkflowState | null>(null)

export function useWorkflow() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error("useWorkflow must be used within WorkflowProvider")
  return ctx
}

function stepIndex(id: StepId) {
  return STEPS.findIndex((s) => s.id === id)
}

export function WorkflowProvider({ children }: { children: ReactNode }) {
  const [step, setStep] = useState<StepId>("upload")
  const [furthest, setFurthest] = useState(0)

  const [dataset, setDataset] = useState<Dataset | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const [config, setConfig] = useState<ReconConfig>(DEFAULT_CONFIG)

  const [status, setStatus] = useState<JobStatus>("idle")
  const [progress, setProgress] = useState(0)
  const [logs, setLogs] = useState<LogEntry[]>([])

  const [downloaded, setDownloaded] = useState<string[]>([])

  const reachStep = useCallback((id: StepId) => {
    setFurthest((f) => Math.max(f, stepIndex(id)))
  }, [])

  const canAccess = useCallback(
    (id: StepId) => stepIndex(id) <= furthest,
    [furthest],
  )

  const goTo = useCallback(
    (id: StepId) => {
      if (stepIndex(id) <= furthest) setStep(id)
    },
    [furthest],
  )

  const next = useCallback(() => {
    const i = stepIndex(step)
    const n = STEPS[Math.min(STEPS.length - 1, i + 1)]
    reachStep(n.id)
    setStep(n.id)
  }, [step, reachStep])

  const back = useCallback(() => {
    const i = stepIndex(step)
    setStep(STEPS[Math.max(0, i - 1)].id)
  }, [step])

  // --- Upload simulation ---
  const uploadTimer = useRef<ReturnType<typeof setInterval> | null>(null)
  const simulateUpload = useCallback(
    (d: Dataset) => {
      if (uploadTimer.current) clearInterval(uploadTimer.current)
      setDataset(d)
      setUploading(true)
      setUploadProgress(0)
      uploadTimer.current = setInterval(() => {
        setUploadProgress((p) => {
          if (p >= 100) {
            if (uploadTimer.current) clearInterval(uploadTimer.current)
            setUploading(false)
            reachStep("configure")
            return 100
          }
          return Math.min(100, p + 7)
        })
      }, 90)
    },
    [reachStep],
  )

  const selectDataset = useCallback((d: Dataset) => setDataset(d), [])

  // --- Job simulation ---
  const jobTimer = useRef<ReturnType<typeof setInterval> | null>(null)
  const loggedAt = useRef<Set<number>>(new Set())

  const tickLogs = useCallback((p: number) => {
    LOG_LINES.forEach((l) => {
      if (l.at <= p && !loggedAt.current.has(l.at)) {
        loggedAt.current.add(l.at)
        const time = new Date().toLocaleTimeString("en-GB", { hour12: false })
        setLogs((prev) => [...prev, { level: l.level, text: l.text, time }])
      }
    })
  }, [])

  const startJob = useCallback(() => {
    if (jobTimer.current) clearInterval(jobTimer.current)
    setStatus("running")
    if (progress >= 100) {
      setProgress(0)
      setLogs([])
      loggedAt.current = new Set()
    }
    jobTimer.current = setInterval(() => {
      setProgress((p) => {
        const np = Math.min(100, p + 2)
        tickLogs(np)
        if (np >= 100) {
          if (jobTimer.current) clearInterval(jobTimer.current)
          setStatus("complete")
          reachStep("validation")
        }
        return np
      })
    }, 260)
  }, [progress, tickLogs, reachStep])

  const pauseJob = useCallback(() => {
    if (jobTimer.current) clearInterval(jobTimer.current)
    setStatus((s) => (s === "running" ? "paused" : s))
  }, [])

  const resetJob = useCallback(() => {
    if (jobTimer.current) clearInterval(jobTimer.current)
    loggedAt.current = new Set()
    setProgress(0)
    setLogs([])
    setStatus("idle")
  }, [])

  const markDownloaded = useCallback(
    (id: string) => setDownloaded((prev) => (prev.includes(id) ? prev : [...prev, id])),
    [],
  )

  useEffect(() => {
    return () => {
      if (jobTimer.current) clearInterval(jobTimer.current)
      if (uploadTimer.current) clearInterval(uploadTimer.current)
    }
  }, [])

  return (
    <Ctx.Provider
      value={{
        step,
        furthest,
        goTo,
        next,
        back,
        canAccess,
        dataset,
        selectDataset,
        uploading,
        uploadProgress,
        simulateUpload,
        config,
        setConfig,
        status,
        progress,
        logs,
        startJob,
        pauseJob,
        resetJob,
        downloaded,
        markDownloaded,
      }}
    >
      {children}
    </Ctx.Provider>
  )
}

export { DATASETS }
