"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { PageBreadcrumb } from "@/components/breadcrumb-context"
import { BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from "@/components/ui/breadcrumb"
import { SquareTerminal, CheckCircle2, XCircle, Clock, AlertCircle, ArrowLeft, RefreshCw, MoreVertical } from "lucide-react"
import { JobSummary, JobAccount } from "@/lib/types"
import { apiGet } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DataTable } from "@/components/data-table"
import { ColumnDef } from "@tanstack/react-table"
import { toast } from "sonner"
import { format } from "date-fns"

export default function JobDetailsPage() {
    const params = useParams()
    const router = useRouter()
    const jobId = params.id as string
    const [summary, setSummary] = useState<JobSummary | null>(null)
    const [loading, setLoading] = useState(true)

    const fetchSummary = async () => {
        try {
            setLoading(true)
            const data = await apiGet<JobSummary>(`/jobs/${jobId}/summary`, "local")
            setSummary(data)
        } catch (err) {
            toast.error("Failed to fetch job details")
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchSummary()
        // Poll for updates if the job is still running or queued
        const interval = setInterval(() => {
            if (summary?.job.status === "running" || summary?.job.status === "queued") {
                fetchSummary()
            }
        }, 5000)
        return () => clearInterval(interval)
    }, [jobId, summary?.job.status])

    const columns: ColumnDef<JobAccount>[] = [
        {
            accessorKey: "account_id",
            header: "Account ID",
            cell: ({ row }) => <span className="font-mono text-xs">#{row.original.account_id}</span>
        },
        {
            accessorKey: "status",
            header: "Status",
            cell: ({ row }) => {
                const status = row.original.status
                return (
                    <Badge
                        variant={
                            status === "completed" ? "success" :
                                status === "failed" ? "destructive" :
                                    status === "running" ? "warning" :
                                        "secondary"
                        }
                        className="capitalize font-normal"
                    >
                        {status}
                    </Badge>
                )
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

    if (!summary && loading) {
        return <div className="p-8 text-center">Loading job details...</div>
    }

    if (!summary) {
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
                                    <Badge variant="outline" className="ml-2 font-normal uppercase text-[10px]">
                                        {summary.job.status}
                                    </Badge>
                                </p>
                            </div>
                        </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={fetchSummary} disabled={loading}>
                        <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                        Refresh
                    </Button>
                </div>

                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
                    <Card className="bg-card/50 border-border shadow-none">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Accounts</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stats.total}</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-card/50 border-border shadow-none">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Completed</CardTitle>
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-green-500">{stats.completed}</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-card/50 border-border shadow-none">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Failed</CardTitle>
                            <XCircle className="h-4 w-4 text-red-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-red-500">{stats.failed}</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-card/50 border-border shadow-none">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Running</CardTitle>
                            <Clock className="h-4 w-4 text-yellow-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-yellow-500">{stats.running}</div>
                        </CardContent>
                    </Card>
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
