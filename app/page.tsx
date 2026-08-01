"use client"

import { TopNav } from "@/components/dashboard/top-nav"
import {
  WorkflowProvider,
  useWorkflow,
} from "@/components/workflow/workflow-context"
import { Stepper } from "@/components/workflow/stepper"
import { StepUpload } from "@/components/workflow/step-upload"
import { StepConfigure } from "@/components/workflow/step-configure"
import { StepRun } from "@/components/workflow/step-run"
import { StepValidation } from "@/components/workflow/step-validation"
import { StepCompare } from "@/components/workflow/step-compare"
import { StepDownload } from "@/components/workflow/step-download"

function ActiveStep() {
  const { step } = useWorkflow()
  switch (step) {
    case "upload":
      return <StepUpload />
    case "configure":
      return <StepConfigure />
    case "run":
      return <StepRun />
    case "validation":
      return <StepValidation />
    case "compare":
      return <StepCompare />
    case "download":
      return <StepDownload />
    default:
      return <StepUpload />
  }
}

export default function Page() {
  return (
    <WorkflowProvider>
      <div className="min-h-screen bg-background">
        {/* Ambient grid backdrop */}
        <div className="grid-bg pointer-events-none fixed inset-0 opacity-30" />

        <div className="relative">
          <TopNav />
          <Stepper />

          <main className="mx-auto max-w-[1800px] px-4 py-6 md:px-6">
            <ActiveStep />
            <div className="h-10" />
          </main>
        </div>
      </div>
    </WorkflowProvider>
  )
}
