"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import Link from "next/link"
import { PageBreadcrumb } from "@/components/breadcrumb-context"
import { BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from "@/components/ui/breadcrumb"
import { SquareTerminal, Play, CheckCircle2, XCircle, Clock, MoreHorizontal, Eye, Trash2, StopCircle } from "lucide-react"
import { DataTable } from "@/components/data-table"
import { ColumnDef } from "@tanstack/react-table"
import { Job } from "@/lib/types"
import { apiGet, apiDelete } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
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

    const stats = {
        total: response?.total || jobs.length,
        running: jobs.filter(j => j.status === "running" || j.status === "queued").length,
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
                <div className="flex flex-col">
                    <span className="font-medium text-sm">{row.original.name || `Job #${row.original.id}`}</span>
                </div>
            )
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
                        {status === "running" && <Clock className="mr-1 h-3 w-3 animate-pulse" />}
                        {status}
                    </Badge>
                )
            }
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
                        <Button variant="ghost" size="sm" asChild>
                            <Link href={`/jobs/detail?id=${job.id}`}>
                                View Details
                            </Link>
                        </Button>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" className="h-8 w-8 p-0">
                                    <span className="sr-only">Open menu</span>
                                    <MoreHorizontal className="h-4 w-4" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuLabel>Actions</DropdownMenuLabel>
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

                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
                    <Card className="bg-card/50 border-border shadow-none">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
                            <SquareTerminal className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stats.total}</div>
                            <p className="text-xs text-muted-foreground">Lifetime runs</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-card/50 border-border shadow-none">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Running</CardTitle>
                            <Clock className="h-4 w-4 text-yellow-500 animate-pulse" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-yellow-500">{stats.running}</div>
                            <p className="text-xs text-muted-foreground">Active processes</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-card/50 border-border shadow-none">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Completed</CardTitle>
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-green-500">{stats.completed}</div>
                            <p className="text-xs text-muted-foreground">Successful jobs</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-card/50 border-border shadow-none">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Failed</CardTitle>
                            <XCircle className="h-4 w-4 text-red-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-red-500">{stats.failed}</div>
                            <p className="text-xs text-muted-foreground">Jobs with errors</p>
                        </CardContent>
                    </Card>
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
