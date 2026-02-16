"use client"

import JobDetailsView from "@/components/job-details-view"
import { Suspense } from "react"
import { RefreshCw } from "lucide-react"

export default function Page() {
    return (
        <Suspense fallback={
            <div className="p-8 text-center flex items-center justify-center gap-2">
                <RefreshCw className="h-4 w-4 animate-spin" />
                Loading...
            </div>
        }>
            <JobDetailsView />
        </Suspense>
    )
}
