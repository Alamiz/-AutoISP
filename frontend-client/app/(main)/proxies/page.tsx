"use client"

import { useState, useEffect, useMemo } from "react"
import { PageBreadcrumb } from "@/components/breadcrumb-context"
import { BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from "@/components/ui/breadcrumb"
import { Globe, Plus, RefreshCw, MoreHorizontal, Trash2, Edit } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BulkUploader } from "@/components/bulk-uploader"
import { apiGet, apiDelete } from "@/lib/api"
import { toast } from "sonner"
import { DataTable } from "@/components/data-table"
import { ColumnDef } from "@tanstack/react-table"
import { Checkbox } from "@/components/ui/checkbox"
import { useProxies } from "@/providers/proxy-provider"
import { Proxy } from "@/lib/types"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { ProxyDrawer } from "@/components/proxy-drawer"



export default function ProxiesPage() {
    const [showUploader, setShowUploader] = useState(false)
    const [showDrawer, setShowDrawer] = useState(false)
    const [editingProxy, setEditingProxy] = useState<Proxy | null>(null)
    const [proxies, setProxies] = useState<Proxy[]>([])
    const [loading, setLoading] = useState(false)
    const {
        selectedProxiesMap: rowSelection,
        setSelectedProxiesMap: setRowSelection,
        statusFilter,
        setStatusFilter,
        totalCount,
        setTotalCount,
        clearSelection
    } = useProxies()

    const fetchProxies = async () => {
        try {
            setLoading(true)
            let url = `/proxies?page_size=100`
            if (statusFilter && statusFilter !== "all") {
                url += `&status=${statusFilter}`
            }
            const res = await apiGet<any>(url, "local")
            const items = res?.items || []
            setProxies(items)
            setTotalCount(res?.total || items.length)
        } catch (err) {
            toast.error("Failed to load proxies")
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const deleteProxy = async (id: number) => {
        try {
            await apiDelete(`/proxies/${id}`, undefined, "local")
            toast.success("Proxy deleted")
            fetchProxies()
        } catch (err) {
            toast.error("Failed to delete proxy")
        }
    }

    const bulkDelete = async () => {
        const selectedIds = Object.keys(rowSelection).filter(id => rowSelection[id]).map(Number)
        if (selectedIds.length === 0) return

        try {
            await apiDelete(`/proxies/bulk`, selectedIds, "local")
            toast.success(`Deleted ${selectedIds.length} proxies`)
            clearSelection()
            fetchProxies()
        } catch (err) {
            toast.error("An error occurred during bulk deletion")
            fetchProxies()
        }
    }

    const exportToTxt = async () => {
        const selectedIds = Object.keys(rowSelection).filter(id => rowSelection[id]).map(Number)
        if (selectedIds.length === 0) return

        // We might need to fetch all selected proxies if they are not in the current page
        // For simplicity, let's assume if they are many, we fetch them
        try {
            const res = await apiGet<any>(`/proxies?page_size=10000`, "local")
            const allProxies: Proxy[] = res?.items || []
            const selected = allProxies.filter(p => rowSelection[String(p.id)])

            const content = selected
                .map(p => `${p.ip}:${p.port}${p.username ? `:${p.username}:${p.password}` : ""}`)
                .join("\n")

            const blob = new Blob([content], { type: "text/plain" })
            const url = URL.createObjectURL(blob)
            const a = document.createElement("a")
            a.href = url
            a.download = `proxies_export_${new Date().toISOString().slice(0, 10)}.txt`
            a.click()
            URL.revokeObjectURL(url)
            toast.success(`Exported ${selected.length} proxies`)
        } catch (err) {
            toast.error("Failed to export proxies")
        }
    }

    const handleSelectAll = async () => {
        try {
            let url = `/proxies?page_size=10000`
            if (statusFilter && statusFilter !== "all") {
                url += `&status=${statusFilter}`
            }
            const res = await apiGet<any>(url, "local")
            const items = res?.items || []
            const newSelection: Record<string, boolean> = {}
            items.forEach((p: Proxy) => {
                newSelection[String(p.id)] = true
            })
            setRowSelection(newSelection)
            toast.success(`Selected all ${items.length} proxies`)
        } catch (err) {
            toast.error("Failed to select all proxies")
        }
    }

    const columns: ColumnDef<Proxy>[] = useMemo(() => [
        {
            id: "select",
            header: ({ table }) => (
                <Checkbox
                    checked={table.getIsAllPageRowsSelected() || (table.getIsSomePageRowsSelected() && "indeterminate")}
                    onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
                    aria-label="Select all"
                />
            ),
            cell: ({ row }) => (
                <Checkbox
                    checked={row.getIsSelected()}
                    onCheckedChange={(value) => row.toggleSelected(!!value)}
                    aria-label="Select row"
                />
            ),
            enableSorting: false,
            enableHiding: false,
        },
        {
            accessorKey: "ip",
            header: "IP Address",
            cell: ({ row }) => <div className="font-mono font-medium text-xs truncate max-w-[150px]">{row.getValue("ip")}</div>,
        },
        {
            accessorKey: "port",
            header: "Port",
            cell: ({ row }) => <div className="font-mono text-muted-foreground text-xs">{row.getValue("port")}</div>,
        },
        {
            accessorKey: "username",
            header: "Username",
            cell: ({ row }) => <div className="text-muted-foreground text-xs truncate max-w-[100px]">{row.getValue("username") || "-"}</div>,
        },
        {
            accessorKey: "created_at",
            header: "Created",
            cell: ({ row }) => {
                return <div className="text-muted-foreground text-xs">{new Date(row.getValue("created_at")).toLocaleDateString()}</div>
            },
        },
        {
            id: "actions",
            cell: ({ row }) => {
                const proxy = row.original

                return (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                                <span className="sr-only">Open menu</span>
                                <MoreHorizontal className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => {
                                navigator.clipboard.writeText(`${proxy.ip}:${proxy.port}`)
                                toast.success("Proxy copied to clipboard")
                            }}>
                                Copy address
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => {
                                setEditingProxy(proxy)
                                setShowDrawer(true)
                            }}>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit Proxy
                            </DropdownMenuItem>

                            <AlertDialog>
                                <AlertDialogTrigger asChild>
                                    <DropdownMenuItem onSelect={(e) => e.preventDefault()} className="text-destructive focus:text-destructive">
                                        <Trash2 className="mr-2 h-4 w-4" />
                                        Delete
                                    </DropdownMenuItem>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                    <AlertDialogHeader>
                                        <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                                        <AlertDialogDescription>
                                            This will permanently delete the proxy <strong>{proxy.ip}:{proxy.port}</strong>.
                                        </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                                        <AlertDialogAction
                                            onClick={() => deleteProxy(proxy.id)}
                                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                        >
                                            Delete
                                        </AlertDialogAction>
                                    </AlertDialogFooter>
                                </AlertDialogContent>
                            </AlertDialog>
                        </DropdownMenuContent>
                    </DropdownMenu>
                )
            },
        },
    ], [])

    useEffect(() => {
        fetchProxies()
    }, [statusFilter])

    return (
        <div className="flex h-full flex-col">
            <PageBreadcrumb>
                <BreadcrumbItem>
                    <BreadcrumbLink href="/">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                    <BreadcrumbPage>Proxies</BreadcrumbPage>
                </BreadcrumbItem>
            </PageBreadcrumb>

            <div className="flex-1 p-6 space-y-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                            <Globe className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight">Proxies</h1>
                            <p className="text-sm text-muted-foreground">Manage your proxy pool</p>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={fetchProxies} disabled={loading}>
                            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                            Refresh
                        </Button>
                        <Button size="sm" onClick={() => {
                            setEditingProxy(null)
                            setShowDrawer(true)
                        }}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Proxy
                        </Button>
                        <Button size="sm" variant="secondary" onClick={() => setShowUploader(true)}>
                            <Plus className="h-4 w-4 mr-2" />
                            Bulk Upload
                        </Button>
                    </div>
                </div>

                <DataTable
                    columns={columns}
                    data={proxies}
                    filterColumn="ip"
                    filterPlaceholder="Filter by IP..."
                    onDeleteSelected={bulkDelete}
                    onExportSelected={exportToTxt}
                    enableRowSelectionOnClick={true}
                    showTopSelectionCount={true}
                    getRowId={(p) => String(p.id)}
                    rowSelection={rowSelection}
                    onRowSelectionChange={setRowSelection}
                    totalCount={totalCount}
                    selectedCount={Object.keys(rowSelection).filter(id => rowSelection[id]).length}
                    onSelectAllItems={handleSelectAll}
                    onClearSelection={clearSelection}
                    statusFilter={{
                        value: statusFilter || "all",
                        onChange: (val) => setStatusFilter(val === "all" ? null : val),
                        options: [
                            { label: "Active", value: "active" },
                            { label: "Dead", value: "dead" },
                            { label: "Unknown", value: "unknown" },
                        ]
                    }}
                />
            </div>

            <ProxyDrawer
                open={showDrawer}
                onOpenChange={setShowDrawer}
                editingProxy={editingProxy as any}
                onProxySaved={fetchProxies}
            />

            <BulkUploader
                mode="proxies"
                open={showUploader}
                onOpenChange={setShowUploader}
                onUploadSuccess={fetchProxies}
            />
        </div>
    )
}
