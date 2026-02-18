"use client"

import { useSearchParams, useRouter } from "next/navigation"
import { PageBreadcrumb } from "@/components/breadcrumb-context"
import { BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from "@/components/ui/breadcrumb"
import { SquareTerminal, CheckCircle2, XCircle, Clock, ArrowLeft, RefreshCw } from "lucide-react"
import { JobSummary, JobAccount } from "@/lib/types"
import { apiGet } from "@/lib/api"
import { JobAccountStatusBadge } from "@/components/job-account-status-badge"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DataTable } from "@/components/data-table"
import { StatCard } from "@/components/stat-card"
import { ColumnDef } from "@tanstack/react-table"
import { useQuery } from "@tanstack/react-query"
import { format } from "date-fns"
import { useActiveJobs } from "@/hooks/useActiveJobs"

export default function JobDetailsView() {
    const searchParams = useSearchParams()
    const router = useRouter()
    const jobId = Number(searchParams.get("id"))
    const { activeJobs } = useActiveJobs()

    // Check if this job is currently active to determine poll rate
    const isActive = activeJobs.some(j => j.job.id === jobId)

    const { data: summary, isLoading, error } = useQuery<JobSummary>({
        queryKey: ["job", jobId],
        queryFn: () => apiGet<JobSummary>(`/jobs/${jobId}/summary`, "local"),
        enabled: !isNaN(jobId),
        refetchInterval: isActive ? 1000 : 5000
    })

    const columns: ColumnDef<JobAccount>[] = [
        {
            accessorKey: "account_email",
            header: "Account",
            cell: ({ row }) => (
                <span className="text-xs truncate max-w-[200px] block" title={row.original.account_email || ""}>
                    {row.original.account_email || `#${row.original.account_id}`}
                </span>
            )
        },
        {
            accessorKey: "status",
            header: "Status",
            cell: ({ row }) => {
                const status = row.original.status
                return <JobAccountStatusBadge status={status} />
            }
        },
        {
            accessorKey: "error_message",
            header: "Result/Error",
            cell: ({ row }) => (
                <span className="text-xs text-muted-foreground italic">
                    {row.original.error_message || (row.original.status === "completed" ? "Success" : "-")}
                </span>
            )
        }
    ]

    if (isLoading) {
        return <div className="p-8 text-center flex items-center justify-center gap-2">
            <RefreshCw className="h-4 w-4 animate-spin" />
            Loading job details...
        </div>
    }

    if (error || !summary) {
        return <div className="p-8 text-center text-destructive">Job not found</div>
    }

    const stats = {
        total: summary.job_accounts.length,
        completed: summary.job_accounts.filter(a => a.status === "completed").length,
        failed: summary.job_accounts.filter(a => a.status === "failed").length,
        running: summary.job_accounts.filter(a => a.status === "running").length,
    }

    return (
        <div className="flex h-full flex-col">
            <PageBreadcrumb>
                <BreadcrumbItem>
                    <BreadcrumbLink href="/">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                    <BreadcrumbLink href="/jobs">Jobs</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                    <BreadcrumbPage>Job #{jobId}</BreadcrumbPage>
                </BreadcrumbItem>
            </PageBreadcrumb>

            <div className="flex-1 p-6 overflow-auto">
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                        <Button variant="ghost" size="icon" onClick={() => router.back()}>
                            <ArrowLeft className="h-5 w-5" />
                        </Button>
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                                <SquareTerminal className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold tracking-tight">
                                    {summary.job.name || `Job #${jobId}`}
                                </h1>
                                <p className="text-sm text-muted-foreground flex items-center gap-2">
                                    Started {format(new Date(summary.job.created_at), "PPP p")}
                                    <JobAccountStatusBadge status={summary.job.status} className="ml-2" />
                                </p>
                            </div>
                        </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => router.refresh()} disabled={isLoading}>
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
                        Refresh
                    </Button>
                </div>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
                    <StatCard
                        title="Total Accounts"
                        value={stats.total}
                        description="Assigned to job"
                        icon={<SquareTerminal className="h-5 w-5" />}
                        variant="primary"
                    />
                    <StatCard
                        title="Completed"
                        value={stats.completed}
                        description="Successful tasks"
                        icon={<CheckCircle2 className="h-5 w-5" />}
                        variant="success"
                    />
                    <StatCard
                        title="Failed"
                        value={stats.failed}
                        description="Tasks with errors"
                        icon={<XCircle className="h-5 w-5" />}
                        variant="destructive"
                    />
                    <StatCard
                        title="Running"
                        value={stats.running}
                        description="Active processes"
                        icon={<Clock className="h-5 w-5" />}
                        variant="warning"
                    />
                </div>

                <div className="space-y-4">
                    <h2 className="text-lg font-semibold tracking-tight">Account Progress</h2>
                    <DataTable
                        columns={columns}
                        data={summary.job_accounts}
                        filterColumn="status"
                        filterPlaceholder="Filter by status..."
                    />
                </div>
            </div>
        </div>
    )
}
