"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import Link from "next/link"
import { PageBreadcrumb } from "@/components/breadcrumb-context"
import { BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from "@/components/ui/breadcrumb"
import { SquareTerminal, Play, CheckCircle2, XCircle, Clock, MoreHorizontal, Eye, Trash2, StopCircle, Loader2 } from "lucide-react"
import { DataTable } from "@/components/data-table"
import { ColumnDef } from "@tanstack/react-table"
import { Job } from "@/lib/types"
import { apiGet, apiDelete } from "@/lib/api"
import { JobAccountStatusBadge } from "@/components/job-account-status-badge"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { toast } from "sonner"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CreateJobWizard } from "@/components/create-job-wizard"
import { StatCard } from "@/components/stat-card"
import { format } from "date-fns"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog"

export default function JobsPage() {
    const [wizardOpen, setWizardOpen] = useState(false)
    const [deleteId, setDeleteId] = useState<number | null>(null)

    const { data: response, isLoading: loading, refetch: fetchJobs } = useQuery<{ items: Job[], total: number }>({
        queryKey: ["jobs"],
        queryFn: () => apiGet<{ items: Job[], total: number }>("/jobs?page_size=100", "local"),
        refetchInterval: 10000 // Backup polling
    })

    const jobs = response?.items || []
    const runningJob = jobs.find(j => j.status === "running")
    const queuedJobs = jobs.filter(j => j.status === "queued")

    const stats = {
        total: response?.total || jobs.length,
        queued: queuedJobs.length,
        completed: jobs.filter(j => j.status === "completed").length,
        failed: jobs.filter(j => j.status === "failed").length
    }

    const deleteJob = async (id: number) => {
        try {
            await apiDelete(`/jobs/${id}`, undefined, "local")
            toast.success("Job deleted")
            fetchJobs()
        } catch (error) {
            toast.error("Failed to delete job")
        } finally {
            setDeleteId(null)
        }
    }

    const columns: ColumnDef<Job>[] = [
        {
            accessorKey: "id",
            header: "ID",
            cell: ({ row }) => <span className="font-mono text-xs"># {row.original.id}</span>
        },
        {
            accessorKey: "name",
            header: "Job Name",
            cell: ({ row }) => (
                <Link
                    href={`/jobs/detail?id=${row.original.id}`}
                    className="font-medium text-sm hover:underline"
                >
                    {row.original.name || `Job #${row.original.id}`}
                </Link>
            )
        },
        {
            accessorKey: "status",
            header: "Status",
            cell: ({ row }) => (
                <JobAccountStatusBadge status={row.original.status} />
            )
        },
        {
            accessorKey: "max_concurrent",
            header: "Concurrency",
            cell: ({ row }) => <span className="text-xs">{row.original.max_concurrent} threads</span>
        },
        {
            accessorKey: "created_at",
            header: "Created",
            cell: ({ row }) => (
                <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {format(new Date(row.original.created_at), "PPP p")}
                </span>
            )
        },
        {
            id: "actions",
            cell: ({ row }) => {
                const job = row.original
                return (
                    <div className="flex items-center gap-2">
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" className="h-8 w-8 p-0">
                                    <span className="sr-only">Open menu</span>
                                    <MoreHorizontal className="h-4 w-4" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                <DropdownMenuItem asChild>
                                    <Link href={`/jobs/detail?id=${job.id}`}>
                                        <Eye className="mr-2 h-4 w-4" />
                                        View Details
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={() => setDeleteId(job.id)} className="text-destructive focus:text-destructive">
                                    <Trash2 className="mr-2 h-4 w-4" />
                                    Delete Job
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                )
            }
        }
    ]

    return (
        <div className="flex h-full flex-col">
            <PageBreadcrumb>
                <BreadcrumbItem>
                    <BreadcrumbLink href="/">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                    <BreadcrumbPage>Jobs</BreadcrumbPage>
                </BreadcrumbItem>
            </PageBreadcrumb>

            <div className="flex-1 p-6 overflow-auto">
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                            <SquareTerminal className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight">Jobs</h1>
                            <p className="text-sm text-muted-foreground">Manage and monitor automation jobs</p>
                        </div>
                    </div>
                    <Button onClick={() => setWizardOpen(true)}>
                        <Play className="mr-2 h-4 w-4 fill-current" />
                        New Job
                    </Button>
                </div>

                {runningJob && (
                    <div className="mb-8 p-4 bg-blue-500/5 border border-blue-500/20 rounded-xl flex items-center justify-between animate-in fade-in slide-in-from-top-4 duration-500">
                        <div className="flex items-center gap-4">
                            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/10 relative">
                                <div className="absolute inset-0 rounded-full bg-blue-500/20 animate-ping" />
                                <Loader2 className="h-6 w-6 text-blue-500 animate-spin relative z-10" />
                            </div>
                            <div>
                                <div className="flex items-center gap-2">
                                    <h2 className="text-lg font-bold">Currently Running</h2>
                                    <Badge className="bg-blue-400/10 text-blue-400 border-blue-400/20 animate-pulse">Active</Badge>
                                </div>
                                <p className="text-sm text-muted-foreground">
                                    <span className="font-semibold text-foreground">{runningJob.name || `Job #${runningJob.id}`}</span> is currently executing...
                                </p>
                            </div>
                        </div>
                        <Button variant="outline" size="sm" asChild>
                            <Link href={`/jobs/detail?id=${runningJob.id}`}>
                                <Eye className="mr-2 h-4 w-4" />
                                View Progress
                            </Link>
                        </Button>
                    </div>
                )}

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
                    <StatCard
                        title="Total Jobs"
                        value={stats.total}
                        description="Lifetime runs"
                        icon={<SquareTerminal className="h-5 w-5" />}
                        variant="primary"
                    />
                    <StatCard
                        title="Queued"
                        value={stats.queued}
                        description="Waiting to run"
                        icon={<Clock className="h-5 w-5" />}
                        variant="warning"
                    />
                    <StatCard
                        title="Completed"
                        value={stats.completed}
                        description="Successful jobs"
                        icon={<CheckCircle2 className="h-5 w-5" />}
                        variant="success"
                    />
                    <StatCard
                        title="Failed"
                        value={stats.failed}
                        description="Jobs with errors"
                        icon={<XCircle className="h-5 w-5" />}
                        variant="destructive"
                    />
                </div>

                <DataTable
                    columns={columns}
                    data={jobs}
                    filterColumn="name"
                    filterPlaceholder="Filter by name..."
                />
            </div>

            <CreateJobWizard open={wizardOpen} onOpenChange={setWizardOpen} />

            <AlertDialog open={!!deleteId} onOpenChange={(open) => !open && setDeleteId(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This action cannot be undone. This will permanently delete the job run and all its execution history.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={() => deleteId && deleteJob(deleteId)}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                            Delete
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    )
}

