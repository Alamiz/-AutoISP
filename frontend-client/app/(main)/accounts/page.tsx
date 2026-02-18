"use client"

import { useState, useEffect, useMemo } from "react"
import { PageBreadcrumb } from "@/components/breadcrumb-context"
import { BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from "@/components/ui/breadcrumb"
import { User, Plus, RefreshCw, MoreHorizontal, Trash2, Edit, Copy } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BulkUploader } from "@/components/bulk-uploader"
import { apiGet, apiDelete } from "@/lib/api"
import { toast } from "sonner"
import { StatCard } from "@/components/stat-card"
import { DataTable } from "@/components/data-table"
import { ColumnDef } from "@tanstack/react-table"
import { Checkbox } from "@/components/ui/checkbox"
import { useAccounts } from "@/providers/account-provider"
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
import { Badge } from "@/components/ui/badge"
import { AccountStatusBadge } from "@/components/account-status-badge"
import { AccountDrawer } from "@/components/account-drawer"
import { useProvider } from "@/contexts/provider-context"
import { Play } from "lucide-react"
import { Account } from "@/lib/types"

export default function AccountsPage() {
    const { selectedProvider } = useProvider()
    const [accounts, setAccounts] = useState<Account[]>([])
    const [loading, setLoading] = useState(false)
    const [showUploader, setShowUploader] = useState(false)
    const [showDrawer, setShowDrawer] = useState(false)
    const [editingAccount, setEditingAccount] = useState<Account | null>(null)
    const {
        selectedAccountsMap: rowSelection,
        setSelectedAccountsMap: setRowSelection,
        setSelectedAccounts,
        statusFilter,
        setStatusFilter,
        totalCount,
        setTotalCount,
        clearSelection
    } = useAccounts()

    const fetchAccounts = async () => {
        try {
            setLoading(true)
            let url = `/accounts?page_size=100&provider=${selectedProvider?.slug || ""}`
            if (statusFilter && statusFilter !== "all") {
                url += `&status=${statusFilter}`
            }
            const res = await apiGet<any>(url, "local")

            // Ensure we have items, fallback to []
            // Map credentials field for drawer compatibility if needed
            const mapped: Account[] = (res?.items || []).map((acc: any) => ({
                ...acc,
                provider: acc.provider as Account["provider"],
                credentials: {
                    password: acc.password,
                    recovery_email: acc.recovery_email,
                    number: acc.phone_number
                }
            }))
            setAccounts(mapped)
            setTotalCount(res?.total || mapped.length)
        } catch (err) {
            toast.error("Failed to load accounts")
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchAccounts()
    }, [selectedProvider?.slug, statusFilter])

    const accountStats = useMemo(() => {
        return {
            total: accounts.length,
            active: accounts.filter(a => a.status === "active").length,
            failed: accounts.filter(a => a.status === "failed").length,
            issues: accounts.filter(a => ["locked", "suspended", "wrong_password"].includes(a.status)).length
        }
    }, [accounts])

    const deleteAccount = async (id: number) => {
        try {
            await apiDelete(`/accounts/${id}/`, undefined, "local")
            toast.success("Account deleted")
            fetchAccounts()
        } catch (err) {
            toast.error("Failed to delete account")
        }
    }

    const bulkDelete = async (selected: Account[]) => {
        // Bulk delete is now handled by AlertDialog inside DataTable
        try {
            const ids = selected.map(acc => acc.id)
            await apiDelete(`/accounts/bulk/`, ids, "local")
            toast.success(`Deleted ${selected.length} accounts`)
            clearSelection()
            fetchAccounts()
        } catch (err) {
            toast.error("An error occurred during bulk deletion")
            fetchAccounts()
        }
    }

    const exportToTxt = (selected: Account[]) => {
        const content = selected
            .map(acc => `${acc.email},${acc.password}${acc.recovery_email ? `,${acc.recovery_email}` : ""}${acc.phone_number ? `,${acc.phone_number}` : ""}`)
            .join("\n")

        const blob = new Blob([content], { type: "text/plain" })
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `accounts_export_${new Date().toISOString().slice(0, 10)}.txt`
        a.click()
        URL.revokeObjectURL(url)
        toast.success(`Exported ${selected.length} accounts`)
    }

    const handleSelectAll = async () => {
        try {
            let url = `/accounts?page_size=10000`
            if (statusFilter && statusFilter !== "all") {
                url += `&status=${statusFilter}`
            }
            const res = await apiGet<any>(url, "local")
            const items = res?.items || []
            setSelectedAccounts(items)
            const newSelection: Record<string, boolean> = {}
            items.forEach((acc: Account) => {
                newSelection[String(acc.id)] = true
            })
            setRowSelection(newSelection)
            toast.success(`Selected all ${items.length} accounts`)
        } catch (err) {
            toast.error("Failed to select all accounts")
        }
    }

    const columns: ColumnDef<Account>[] = useMemo(() => [
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
            accessorKey: "email",
            header: "Email",
            cell: ({ row }) => <div className="font-medium truncate max-w-[200px]" title={row.getValue("email")}>{row.getValue("email")}</div>,
        },
        {
            accessorKey: "provider",
            header: "Provider",
            cell: ({ row }) => <Badge variant="outline" className="capitalize py-0">{row.getValue("provider")}</Badge>,
        },
        {
            accessorKey: "status",
            header: "Status",
            cell: ({ row }) => {
                const status = row.getValue("status") as string
                return <AccountStatusBadge status={status} />
            },
        },
        {
            accessorKey: "created_at",
            header: "Created",
            cell: ({ row }) => {
                return <div className="text-muted-foreground">{new Date(row.getValue("created_at")).toLocaleDateString()}</div>
            },
        },
        {
            id: "actions",
            cell: ({ row }) => {
                const account = row.original

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
                                navigator.clipboard.writeText(account.email)
                                toast.success("Email copied to clipboard")
                            }}>
                                <Copy className="mr-2 h-4 w-4" />
                                Copy email
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => {
                                setEditingAccount(account)
                                setShowDrawer(true)
                            }}>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit Account
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
                                            This will permanently delete the account <strong>{account.email}</strong>.
                                        </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                                        <AlertDialogAction
                                            onClick={() => deleteAccount(account.id)}
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
        fetchAccounts()
    }, [statusFilter])

    return (
        <div className="flex h-full flex-col">
            <PageBreadcrumb>
                <BreadcrumbItem>
                    <BreadcrumbLink href="/">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                    <BreadcrumbPage>Accounts</BreadcrumbPage>
                </BreadcrumbItem>
            </PageBreadcrumb>

            <div className="flex-1 p-6 space-y-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                            <User className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight">Accounts</h1>
                            <p className="text-sm text-muted-foreground">Manage your email accounts</p>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={fetchAccounts} disabled={loading}>
                            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                            Refresh
                        </Button>
                        <Button size="sm" onClick={() => {
                            setEditingAccount(null)
                            setShowDrawer(true)
                        }}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Account
                        </Button>
                        <Button size="sm" variant="secondary" onClick={() => setShowUploader(true)}>
                            <Plus className="h-4 w-4 mr-2" />
                            Bulk Upload
                        </Button>
                    </div>
                </div>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                    <StatCard
                        title="Total Accounts"
                        value={accountStats.total}
                        description="Currently registered"
                        icon={<User className="h-5 w-5" />}
                        variant="primary"
                    />
                    <StatCard
                        title="Active"
                        value={accountStats.active}
                        description="Ready for use"
                        icon={<Plus className="h-5 w-5" />}
                        variant="success"
                    />
                    <StatCard
                        title="Failed"
                        value={accountStats.failed}
                        description="General failures"
                        icon={<Trash2 className="h-5 w-5" />}
                        variant="destructive"
                    />
                    <StatCard
                        title="Account Issues"
                        value={accountStats.issues}
                        description="Locked/Suspended"
                        icon={<MoreHorizontal className="h-5 w-5" />}
                        variant="warning"
                    />
                </div>

                <DataTable
                    columns={columns}
                    data={accounts}
                    filterColumn="email"
                    filterPlaceholder="Filter by email..."
                    onDeleteSelected={bulkDelete}
                    onExportSelected={exportToTxt}
                    enableRowSelectionOnClick={true}
                    showTopSelectionCount={false}
                    totalCount={totalCount}
                    selectedCount={Object.keys(rowSelection).filter(id => rowSelection[id]).length}
                    rowSelection={rowSelection}
                    onRowSelectionChange={setRowSelection}
                    onSelectAllItems={handleSelectAll}
                    onClearSelection={clearSelection}
                    statusFilter={{
                        value: statusFilter || "all",
                        onChange: (val) => setStatusFilter(val === "all" ? null : val),
                        options: [
                            { label: "Active", value: "active" },
                            { label: "Failed", value: "failed" },
                            { label: "Locked", value: "locked" },
                            { label: "Wrong Password", value: "wrong_password" },
                            { label: "Wrong Email", value: "wrong_email" },
                            { label: "Suspended", value: "suspended" },
                            { label: "Phone Verification", value: "phone_verification" },
                            { label: "Captcha", value: "captcha" },
                            { label: "Unknown", value: "unknown" },
                        ]
                    }}

                />
            </div>

            <AccountDrawer
                open={showDrawer}
                onOpenChange={setShowDrawer}
                editingAccount={editingAccount as any}
                onAccountSaved={fetchAccounts}
            />

            <BulkUploader
                mode="accounts"
                open={showUploader}
                onOpenChange={setShowUploader}
                onUploadSuccess={fetchAccounts}
            />


        </div>
    )
}