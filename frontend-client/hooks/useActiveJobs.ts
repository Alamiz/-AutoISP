import { useQuery, useQueryClient } from "@tanstack/react-query"
import { apiGet, apiPost } from "@/lib/api"
import { Job, JobAccount } from "@/lib/types" // Ensure types exist or redefine
import { useCallback, useMemo } from "react"
import { toast } from "sonner"

// We need an extended interface for JobSummary if not in types
interface JobAccountStatus {
    id: number
    account_id: number
    status: string
    error_message?: string
}

interface JobSummary {
    job: Job
    job_accounts: JobAccountStatus[]
}

export function useActiveJobs() {
    const queryClient = useQueryClient()

    const { data: activeJobs = [], isLoading } = useQuery<JobSummary[]>({
        queryKey: ["active-jobs"],
        queryFn: async () => {
            return await apiGet<JobSummary[]>("/jobs/active", "local")
        },
        refetchInterval: 5000, // Fallback polling
    })

    const isAccountBusy = useCallback((accountId: string | number) => {
        const accId = Number(accountId)
        return activeJobs.some(summary =>
            summary.job_accounts.some(ja => ja.account_id === accId && (ja.status === "running" || ja.status === "queued"))
        )
    }, [activeJobs])

    const getAccountJob = useCallback((accountId: string | number) => {
        const accId = Number(accountId)
        for (const summary of activeJobs) {
            const ja = summary.job_accounts.find(ja => ja.account_id === accId)
            if (ja) {
                // Return a combined object or just the job, mapping status
                return { ...summary.job, status: ja.status as "queued" | "running" | "completed" | "failed" }
            }
        }
        return undefined
    }, [activeJobs])

    const stopJob = async (jobId: number) => {
        try {
            // We need an endpoint for stopping a job.
            // Currently not implemented in backend routers/jobs.py
            // await apiPost(`/jobs/${jobId}/stop`, {}, "local")
            toast.info("Stopping job is not yet implemented backend-side")
        } catch (e) {
            toast.error("Failed to stop job")
        }
    }

    const stopAllJobs = async () => {
        toast.info("Stopping all jobs is not yet implemented backend-side")
    }

    return {
        activeJobs,
        isLoading,
        isAccountBusy,
        getAccountJob,
        stopJob,
        stopAllJobs
    }
}
