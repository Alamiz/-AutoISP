"use client"

import { useState, useEffect, useMemo } from "react"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { AccountStatusBadge } from "@/components/account-status-badge"
import { Play, Info, ArrowRight, ArrowLeft, Plus, CheckCircle2, User, Globe, Mail, Shield, Settings, Search, FlaskConical, Zap, Calendar as CalendarIcon, FileSpreadsheet, Upload } from "lucide-react"
import { automations } from "@/data/automations"
import { useAccounts } from "@/providers/account-provider"
import { useProxies } from "@/providers/proxy-provider"
import { Account, Automation } from "@/lib/types"
import { apiPost, apiGet, ApiError } from "@/lib/api"
import { toast } from "sonner"
import { useRouter } from "next/navigation"
import { BulkImportForm } from "@/components/bulk-import-form"
import { cn } from "@/lib/utils"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Calendar } from "@/components/ui/calendar"
import { format, subDays } from "date-fns"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { DataTable } from "@/components/data-table"
import { ColumnDef } from "@tanstack/react-table"
import { Filter, Loader2, Clock } from "lucide-react"

interface CreateJobWizardProps {
    open: boolean
    onOpenChange: (open: boolean) => void
}

type WizardStep = "accounts" | "proxies" | "automation"

export function CreateJobWizard({ open, onOpenChange }: CreateJobWizardProps) {
    const router = useRouter()
    const [step, setStep] = useState<WizardStep>("accounts")
    const [loading, setLoading] = useState(false)
    const {
        selectedAccountsMap: selectedAccountIds,
        setSelectedAccountsMap: setSelectedAccountIds,
        totalCount: totalAccountsCount,
        setTotalCount: setTotalAccountsCount,
    } = useAccounts()
    const {
        selectedProxiesMap: selectedProxyIds,
        setSelectedProxiesMap: setSelectedProxyIds,
        totalCount: totalProxiesCount,
        setTotalCount: setTotalProxiesCount,
    } = useProxies()

    // Data State
    const [accounts, setAccounts] = useState<Account[]>([])
    const [proxies, setProxies] = useState<any[]>([])

    // Automation State
    const [jobName, setJobName] = useState("")
    const [maxConcurrent, setMaxConcurrent] = useState(5)
    // We only allow SINGLE automation selection for simplicity in this flow, or should we keep multiple?
    // User asked for "configure automations". automation-controls allows multiple. The wizard previously allowed multiple.
    // Let's keep multiple but effectively manage them.
    const [selectedAutomationIds, setSelectedAutomationIds] = useState<string[]>([])
    const [automationParams, setAutomationParams] = useState<Record<string, Record<string, any>>>({})
    const [configuringAutomationId, setConfiguringAutomationId] = useState<string | null>(null)
    const [automationSearch, setAutomationSearch] = useState("")

    // Import Dialog State
    const [importDialog, setImportDialog] = useState<{
        open: boolean
        mode: "accounts" | "proxies"
        file?: File | null
        text?: string
    }>({ open: false, mode: "accounts" })
    const [dragActive, setDragActive] = useState(false)

    // Steps Logic
    const steps: WizardStep[] = ["accounts", "proxies", "automation"]
    const currentStepIndex = steps.indexOf(step)

    const nextStep = () => {
        if (currentStepIndex < steps.length - 1) {
            setStep(steps[currentStepIndex + 1])
        }
    }

    const prevStep = () => {
        if (currentStepIndex > 0) {
            setStep(steps[currentStepIndex - 1])
        }
    }

    // Fetch Data on Open
    useEffect(() => {
        if (open && step === "accounts") {
            fetchAccounts()
        }
    }, [open, step])

    useEffect(() => {
        if (open && step === "proxies") {
            fetchProxies()
        }
    }, [open, step])

    useEffect(() => {
        if (open) {
            setStep("accounts")
            setSelectedAutomationIds([])
            setAutomationParams({})
            setJobName("")
        }
    }, [open])



    const isCurrentPageAccountsSelected = useMemo(() => {
        if (accounts.length === 0) return false
        return accounts.every(a => !!selectedAccountIds[String(a.id)])
    }, [accounts, selectedAccountIds])

    const isCurrentPageProxiesSelected = useMemo(() => {
        if (proxies.length === 0) return false
        return proxies.every(p => !!selectedProxyIds[String(p.id)])
    }, [proxies, selectedProxyIds])

    const fetchAccounts = async () => {
        try {
            setLoading(true)
            const res = await apiGet<any>(`/accounts?page_size=500`, "local")
            setAccounts(res?.items || [])
            setTotalAccountsCount(res?.total || 0)
        } catch (err) {
            console.error(err)
            toast.error("Failed to load accounts")
        }
    }

    const fetchProxies = async () => {
        try {
            setLoading(true)
            const res = await apiGet<any>(`/proxies?page_size=500`, "local")
            const items = res?.items || []
            setProxies(items)
            setTotalProxiesCount(res?.total || 0)

            // Select all by default if none are selected
            setSelectedProxyIds((prev: Record<string, boolean>) => {
                if (Object.keys(prev).length === 0) {
                    const next: Record<string, boolean> = {}
                    items.forEach((p: any) => next[String(p.id)] = true)
                    return next
                }
                return prev
            })
        } catch (err) {
            console.error(err)
            toast.error("Failed to load proxies")
        } finally {
            setLoading(false)
        }
    }

    // Selection Handlers
    const handleImportSuccess = (ids: number[]) => {
        if (importDialog.mode === "accounts") {
            fetchAccounts().then(() => {
                setSelectedAccountIds((prev: Record<string, boolean>) => {
                    const next = { ...prev }
                    ids.forEach(id => next[String(id)] = true)
                    return next
                })
            })
        } else {
            fetchProxies().then(() => {
                setSelectedProxyIds((prev: Record<string, boolean>) => {
                    const next = { ...prev }
                    ids.forEach(id => next[String(id)] = true)
                    return next
                })
            })
        }
        setImportDialog({ ...importDialog, open: false, file: null, text: undefined })
    }

    // Drag & Drop / Paste Handlers
    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const mode = step === "proxies" ? "proxies" : "accounts"
            setImportDialog({
                open: true,
                mode,
                file: e.dataTransfer.files[0]
            })
        }
    }

    useEffect(() => {
        const handlePaste = (e: ClipboardEvent) => {
            if (!open) return
            if (step !== "accounts" && step !== "proxies") return
            // Don't intercept if pasting into an input
            if ((e.target as HTMLElement).tagName === "INPUT" || (e.target as HTMLElement).tagName === "TEXTAREA") return

            const text = e.clipboardData?.getData("text")
            if (text) {
                const mode = step === "proxies" ? "proxies" : "accounts"
                setImportDialog({
                    open: true,
                    mode,
                    text
                })
            }
        }

        window.addEventListener("paste", handlePaste)
        return () => window.removeEventListener("paste", handlePaste)
    }, [open, step])

    const accountColumns: ColumnDef<Account>[] = useMemo(() => [
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
            cell: ({ row }) => (
                <div className="flex items-center gap-2">
                    <Mail className="h-3 w-3 text-muted-foreground" />
                    <span className="font-medium truncate max-w-[150px]">{row.getValue("email")}</span>
                </div>
            )
        },

        {
            accessorKey: "status",
            header: "Status",
            cell: ({ row }) => {
                const status = row.getValue("status") as string
                return <AccountStatusBadge status={status} />
            }
        },
    ], [])

    const proxyColumns: ColumnDef<any>[] = useMemo(() => [
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
            header: "Host",
            cell: ({ row }) => (
                <div className="flex items-center gap-2">
                    <Globe className="h-3 w-3 text-muted-foreground" />
                    <span className="font-medium">{row.getValue("ip")}:{row.original.port}</span>
                </div>
            )
        }
    ], [])

    // Automation Helpers (from automation-controls.tsx)
    const getCategoryIcon = (category: Automation["category"]) => {
        switch (category) {
            case "Email": return <Mail className="h-4 w-4" />
            case "Auth": return <Shield className="h-4 w-4" />
            case "Maintenance": return <Settings className="h-4 w-4" />
            case "Browsing": return <Search className="h-4 w-4" />
            case "Test": return <FlaskConical className="h-4 w-4" />
            default: return <Zap className="h-4 w-4" />
        }
    }

    const getCategoryColor = (category: Automation["category"]) => {
        switch (category) {
            case "Email": return "bg-blue-500/10 text-blue-400 border-blue-500/20"
            case "Auth": return "bg-green-500/10 text-green-400 border-green-500/20"
            case "Maintenance": return "bg-orange-500/10 text-orange-400 border-orange-500/20"
            case "Browsing": return "bg-sky-500/10 text-sky-400 border-sky-500/20"
            case "Test": return "bg-pink-500/10 text-pink-400 border-pink-500/20"
            default: return "bg-gray-500/10 text-gray-400 border-gray-500/20"
        }
    }

    const handleParameterChange = (automationId: string, paramKey: string, value: any) => {
        setAutomationParams((prev) => ({
            ...prev,
            [automationId]: {
                ...prev[automationId],
                [paramKey]: value,
            },
        }))
    }

    // Automation filtering
    const filteredAutomations = useMemo(() => {
        const selectedAccs = accounts.filter(a => !!selectedAccountIds[String(a.id)])
        // Fix: Use "webde" and "gmx" instead of "Web.de" / "GMX" if needed, but assuming data is consistent
        // The automation provider logic in automation-controls uses "webde" for "Web.de".
        // Let's normalize.
        return automations.filter(a =>
            selectedAccs.every(acc => {
                const p = acc.provider.toLowerCase().includes("web") ? "webde" : "gmx"
                return a.provider === "all" || a.provider === p
            })
        )
    }, [accounts, selectedAccountIds])


    const handleToggleAutomation = (id: string, checked: boolean) => {
        if (checked) {
            setSelectedAutomationIds(prev => [...prev, id])
            setConfiguringAutomationId(id)

            // Set default parameters
            const auto = automations.find(a => a.id === id)
            if (auto && auto.params) {
                const defaults: Record<string, any> = {}
                if (id === "report_not_spam") {
                    defaults.start_date = format(subDays(new Date(), 7), "yyyy-MM-dd")
                    defaults.end_date = format(new Date(), "yyyy-MM-dd")
                } else if (id === "open_profile") {
                    defaults.duration = "10"
                }

                if (Object.keys(defaults).length > 0) {
                    setAutomationParams(prev => ({
                        ...prev,
                        [id]: { ...prev[id], ...defaults }
                    }))
                }
            }
        } else {
            setSelectedAutomationIds(prev => prev.filter(i => i !== id))
            if (configuringAutomationId === id) setConfiguringAutomationId(null)
            const newParams = { ...automationParams }
            delete newParams[id]
            setAutomationParams(newParams)
        }
    }

    // Launch Handler
    const handleLaunch = async () => {
        const accountIds = Object.keys(selectedAccountIds).filter(id => selectedAccountIds[id])
        if (accountIds.length === 0) {
            toast.error("Please select at least one account")
            setStep("accounts")
            return
        }
        if (selectedAutomationIds.length === 0) {
            toast.error("Please select an automation")
            return
        }

        // Validate Params
        for (const autoId of selectedAutomationIds) {
            const automation = automations.find(a => a.id === autoId)
            if (!automation) continue;
            const params = automation.params || []
            const userParams = automationParams[autoId] || {}

            for (const param of params) {
                if (param.required && (!userParams[param.name] || userParams[param.name].toString().trim() === "")) {
                    toast.error(`Missing required parameter "${param.label}" for ${automation.name}`)
                    return
                }
            }
        }

        try {
            setLoading(true)

            const payload = {
                name: jobName || `Job ${new Date().toLocaleString()}`,
                max_concurrent: maxConcurrent,
                account_ids: accountIds.map(Number),
                proxy_ids: Object.keys(selectedProxyIds).filter(id => selectedProxyIds[id]).map(Number),
                automations: selectedAutomationIds.map((id, index) => ({
                    automation_name: id,
                    run_order: index,
                    settings: automationParams[id] || {},
                    enabled: true
                }))
            }

            await apiPost("/jobs/run", payload, "local")
            toast.success("Job launched successfully")
            onOpenChange(false)
            router.push("/jobs")
        } catch (error: any) {
            toast.error(error.message || "Failed to launch job")
        } finally {
            setLoading(false)
        }
    }

    return (
        <>
            <Sheet open={open} onOpenChange={onOpenChange}>
                <SheetContent className="bg-card border-border p-0 sm:max-w-2xl w-full flex flex-col h-full">
                    <SheetHeader className="px-6 py-4 border-b border-border">
                        <div className="flex items-center justify-between pr-8">
                            <div className="flex items-center gap-4">
                                <div className={`flex h-8 w-8 items-center justify-center rounded-full border text-xs font-medium ${step === "accounts" ? "bg-primary text-primary-foreground border-primary" : "bg-muted text-muted-foreground"}`}>1</div>
                                <ArrowRight className="h-4 w-4 text-muted-foreground" />
                                <div className={`flex h-8 w-8 items-center justify-center rounded-full border text-xs font-medium ${step === "proxies" ? "bg-primary text-primary-foreground border-primary" : "bg-muted text-muted-foreground"}`}>2</div>
                                <ArrowRight className="h-4 w-4 text-muted-foreground" />
                                <div className={`flex h-8 w-8 items-center justify-center rounded-full border text-xs font-medium ${step === "automation" ? "bg-primary text-primary-foreground border-primary" : "bg-muted text-muted-foreground"}`}>3</div>
                            </div>
                            <div>
                                <SheetTitle className="text-right">Create Job</SheetTitle>
                                <SheetDescription className="text-right">
                                    {step === "accounts" && "Select or Import Accounts"}
                                    {step === "proxies" && "Select or Import Proxies (Optional)"}
                                    {step === "automation" && "Configure Automation"}
                                </SheetDescription>
                            </div>
                        </div>
                    </SheetHeader>

                    <div className="flex-1 overflow-hidden flex flex-col bg-muted/10">
                        {/* STEP 1: ACCOUNTS */}
                        {step === "accounts" && (
                            <div
                                className={`flex-1 flex flex-col p-4 h-full overflow-hidden transition-colors ${dragActive ? "bg-primary/5" : ""}`}
                                onDragEnter={handleDrag}
                                onDragLeave={handleDrag}
                                onDragOver={handleDrag}
                                onDrop={handleDrop}
                            >
                                <div className="flex-1 border rounded-md bg-card overflow-hidden flex flex-col relative">
                                    <div className="flex items-center justify-between p-3 border-b bg-muted/30">
                                        <div className="flex-1 flex items-center gap-2">
                                            <h3 className="text-sm font-medium">Select accounts to use</h3>
                                            {Object.keys(selectedAccountIds).length > 0 && (
                                                <Badge variant="secondary" className="px-1.5 h-5 text-[10px] bg-primary/10 text-primary border-primary/20">
                                                    {Object.keys(selectedAccountIds).length}
                                                </Badge>
                                            )}
                                        </div>
                                        <Button
                                            variant="secondary"
                                            size="sm"
                                            className="h-8 gap-2 px-4 shadow-sm"
                                            onClick={() => {
                                                const input = document.createElement("input")
                                                input.type = "file"
                                                input.accept = ".csv,.txt"
                                                input.onchange = (e) => {
                                                    const file = (e.target as HTMLInputElement).files?.[0]
                                                    if (file) {
                                                        setImportDialog({ open: true, mode: "accounts", file })
                                                    }
                                                }
                                                input.click()
                                            }}
                                        >
                                            <Upload className="h-3.5 w-3.5" /> Import
                                        </Button>
                                    </div>
                                    {dragActive && (
                                        <div className="absolute inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center border-2 border-primary border-dashed m-2 rounded-lg pointer-events-none">
                                            <div className="text-center">
                                                <Plus className="h-10 w-10 mx-auto text-primary mb-2" />
                                                <p className="text-lg font-medium text-primary">Drop files to import accounts</p>
                                            </div>
                                        </div>
                                    )}
                                    <DataTable
                                        columns={accountColumns}
                                        data={accounts}
                                        totalCount={totalAccountsCount}
                                        selectedCount={Object.keys(selectedAccountIds).length}
                                        rowSelection={selectedAccountIds}
                                        onRowSelectionChange={setSelectedAccountIds}
                                        onSelectAllItems={async () => {
                                            try {
                                                const res = await apiGet<any>('/accounts?page_size=10000', "local")
                                                const items = res?.items || []
                                                const newSelection: Record<string, boolean> = {}
                                                items.forEach((a: any) => newSelection[String(a.id)] = true)
                                                setSelectedAccountIds(newSelection)
                                                toast.success(`Selected all ${items.length} accounts`)
                                            } catch (err) {
                                                toast.error("Failed to fetch all accounts")
                                            }
                                        }}
                                        onClearSelection={() => setSelectedAccountIds({})}
                                        getRowId={(row: any) => String(row.id)}
                                        showViewDropdown={false}
                                        className="flex-1 min-h-0"
                                        containerClassName="flex-1"
                                        hidePagination={true}
                                        hideBanners={true}
                                        hideBorder={true}
                                        hideRounding={true}
                                        showTopSelectionCount={false}
                                        enableRowSelectionOnClick={true}
                                    />
                                </div>
                            </div>
                        )}

                        {/* STEP 2: PROXIES */}
                        {step === "proxies" && (
                            <div
                                className={`flex-1 flex flex-col p-4 h-full overflow-hidden transition-colors ${dragActive ? "bg-primary/5" : ""}`}
                                onDragEnter={handleDrag}
                                onDragLeave={handleDrag}
                                onDragOver={handleDrag}
                                onDrop={handleDrop}
                            >
                                <div className="flex-1 border rounded-md bg-card overflow-hidden flex flex-col relative">
                                    {dragActive && (
                                        <div className="absolute inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center border-2 border-primary border-dashed m-2 rounded-lg pointer-events-none">
                                            <div className="text-center">
                                                <Plus className="h-10 w-10 mx-auto text-primary mb-2" />
                                                <p className="text-lg font-medium text-primary">Drop files to import proxies</p>
                                            </div>
                                        </div>
                                    )}
                                    <div className="flex items-center justify-between p-3 border-b bg-muted/30">
                                        <div className="flex-1 flex items-center gap-2">
                                            <h3 className="text-sm font-medium">Select proxies to use (Optional)</h3>
                                            {Object.keys(selectedProxyIds).length > 0 && (
                                                <Badge variant="secondary" className="px-1.5 h-5 text-[10px] bg-primary/10 text-primary border-primary/20">
                                                    {Object.keys(selectedProxyIds).length}
                                                </Badge>
                                            )}
                                        </div>
                                        <Button
                                            variant="secondary"
                                            size="sm"
                                            className="h-8 gap-2 px-4 shadow-sm"
                                            onClick={() => {
                                                const input = document.createElement("input")
                                                input.type = "file"
                                                input.accept = ".csv,.txt"
                                                input.onchange = (e) => {
                                                    const file = (e.target as HTMLInputElement).files?.[0]
                                                    if (file) {
                                                        setImportDialog({ open: true, mode: "proxies", file })
                                                    }
                                                }
                                                input.click()
                                            }}
                                        >
                                            <Upload className="h-3.5 w-3.5" /> Import
                                        </Button>
                                    </div>
                                    {dragActive && (
                                        <div className="absolute inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center border-2 border-primary border-dashed m-2 rounded-lg pointer-events-none">
                                            <div className="text-center">
                                                <Plus className="h-10 w-10 mx-auto text-primary mb-2" />
                                                <p className="text-lg font-medium text-primary">Drop files to import proxies</p>
                                            </div>
                                        </div>
                                    )}
                                    <DataTable
                                        columns={proxyColumns}
                                        data={proxies}
                                        totalCount={totalProxiesCount}
                                        selectedCount={Object.keys(selectedProxyIds).length}
                                        rowSelection={selectedProxyIds}
                                        onRowSelectionChange={setSelectedProxyIds}
                                        onSelectAllItems={async () => {
                                            try {
                                                const res = await apiGet<any>('/proxies?page_size=10000', "local")
                                                const items = res?.items || []
                                                const newSelection: Record<string, boolean> = {}
                                                items.forEach((p: any) => newSelection[String(p.id)] = true)
                                                setSelectedProxyIds(newSelection)
                                                toast.success(`Selected all ${items.length} proxies`)
                                            } catch (err) {
                                                toast.error("Failed to fetch all proxies")
                                            }
                                        }}
                                        onClearSelection={() => setSelectedProxyIds({})}
                                        getRowId={(row: any) => String(row.id)}
                                        showViewDropdown={false}
                                        className="flex-1 min-h-0"
                                        containerClassName="flex-1"
                                        hidePagination={true}
                                        hideBanners={true}
                                        hideBorder={true}
                                        hideRounding={true}
                                        showTopSelectionCount={false}
                                        enableRowSelectionOnClick={true}
                                    />
                                </div>
                            </div>
                        )}

                        {/* STEP 3: AUTOMATION */}
                        {step === "automation" && (
                            <div className="flex-1 flex flex-col h-full p-4 overflow-hidden">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                                            <Zap className="h-4 w-4 text-primary" />
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <h3 className="text-sm font-bold">Available Automations</h3>
                                                {selectedAutomationIds.length > 0 && (
                                                    <Badge variant="secondary" className="px-1.5 h-5 text-[10px] bg-primary/10 text-primary border-primary/20">
                                                        {selectedAutomationIds.length}
                                                    </Badge>
                                                )}
                                            </div>
                                            <p className="text-[10px] text-muted-foreground">Select and configure automations to run</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Input
                                            placeholder="Search automations..."
                                            value={automationSearch}
                                            onChange={(e) => setAutomationSearch(e.target.value)}
                                            className="h-7 text-xs w-[180px] bg-card"
                                        />
                                    </div>
                                </div>
                                <ScrollArea className="flex-1">
                                    <div className="p-4 space-y-4">
                                        {Object.entries(
                                            filteredAutomations
                                                .filter(a => a.name.toLowerCase().includes(automationSearch.toLowerCase()))
                                                .reduce((acc, auto) => {
                                                    const cat = auto.category || "Other"
                                                    if (!acc[cat]) acc[cat] = []
                                                    acc[cat].push(auto)
                                                    return acc
                                                }, {} as Record<string, Automation[]>)
                                        ).map(([category, items]) => (
                                            <div key={category} className="space-y-3">
                                                <h3 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/70 px-1">{category}</h3>
                                                <div className="grid grid-cols-1 gap-2">
                                                    {items.map((auto) => {
                                                        const isSelected = selectedAutomationIds.includes(auto.id)
                                                        const hasParams = auto.params && auto.params.length > 0
                                                        const isExpanded = configuringAutomationId === auto.id

                                                        // Check if valid config
                                                        const isValid = !hasParams || (auto.params || []).every(p => !p.required || (automationParams[auto.id]?.[p.name] && automationParams[auto.id]?.[p.name].toString().trim() !== ""))

                                                        return (
                                                            <div
                                                                key={auto.id}
                                                                className={`rounded-lg border transition-all cursor-pointer select-none ${isSelected ? "border-primary/50 bg-primary/5" : "border-border bg-card hover:border-primary/20"}`}
                                                                onClick={() => handleToggleAutomation(auto.id, !isSelected)}
                                                            >
                                                                <div className="p-3 flex items-start gap-3">
                                                                    <Checkbox
                                                                        checked={isSelected}
                                                                        onCheckedChange={(c) => handleToggleAutomation(auto.id, !!c)}
                                                                        className="mt-1"
                                                                        onClick={(e) => e.stopPropagation()}
                                                                    />
                                                                    <div className="flex-1 min-w-0">
                                                                        <div className="flex items-center justify-between mb-1">
                                                                            <div className="flex items-center gap-2">
                                                                                {getCategoryIcon(auto.category)}
                                                                                <span className="font-medium text-sm">{auto.name}</span>
                                                                            </div>
                                                                            <Badge className={getCategoryColor(auto.category)}>{auto.category}</Badge>
                                                                        </div>
                                                                        <p className="text-xs text-muted-foreground mb-2">{auto.description}</p>

                                                                        <div className="flex items-center justify-between gap-2">
                                                                            <div className="flex gap-2">
                                                                                <Badge variant="outline" className="text-[10px] font-normal uppercase">
                                                                                    {auto.provider}
                                                                                </Badge>
                                                                                <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                                                                                    <Info className="h-3 w-3" /> {auto.estimatedDuration}
                                                                                </span>
                                                                            </div>

                                                                            {hasParams && isSelected && (
                                                                                <Button
                                                                                    variant="ghost"
                                                                                    size="sm"
                                                                                    onClick={(e) => {
                                                                                        e.stopPropagation()
                                                                                        setConfiguringAutomationId(isExpanded ? null : auto.id)
                                                                                    }}
                                                                                    className={`h-7 px-2 text-xs gap-1 ${isValid ? 'text-primary' : 'text-orange-500'}`}
                                                                                >
                                                                                    <Settings className="h-3 w-3" />
                                                                                    Configure
                                                                                </Button>
                                                                            )}
                                                                        </div>
                                                                    </div>
                                                                </div>

                                                                {/* Configuration Panel */}
                                                                {isExpanded && isSelected && hasParams && (
                                                                    <div
                                                                        className="border-t border-border/50 p-4 bg-background/50 space-y-3 animate-in fade-in slide-in-from-top-1"
                                                                        onClick={(e) => e.stopPropagation()}
                                                                    >
                                                                        {auto.params?.map(param => (
                                                                            <div key={param.name} className="space-y-1">
                                                                                <Label className="text-xs">
                                                                                    {param.label} {param.required && <span className="text-red-400">*</span>}
                                                                                </Label>
                                                                                {param.type === "date" ? (
                                                                                    <Popover>
                                                                                        <PopoverTrigger asChild>
                                                                                            <Button
                                                                                                variant={"outline"}
                                                                                                className={cn(
                                                                                                    "w-full justify-start text-left font-normal h-8 text-xs",
                                                                                                    !automationParams[auto.id]?.[param.name] && "text-muted-foreground"
                                                                                                )}
                                                                                            >
                                                                                                <CalendarIcon className="mr-2 h-3 w-3" />
                                                                                                {automationParams[auto.id]?.[param.name] ? (
                                                                                                    format(new Date(automationParams[auto.id]?.[param.name]), "PPP")
                                                                                                ) : (
                                                                                                    <span>Pick a date</span>
                                                                                                )}
                                                                                            </Button>
                                                                                        </PopoverTrigger>
                                                                                        <PopoverContent className="w-auto p-0" align="start">
                                                                                            <Calendar
                                                                                                mode="single"
                                                                                                selected={automationParams[auto.id]?.[param.name] ? new Date(automationParams[auto.id]?.[param.name]) : undefined}
                                                                                                onSelect={(date) => handleParameterChange(auto.id, param.name, date ? format(date, "yyyy-MM-dd") : "")}
                                                                                                initialFocus
                                                                                            />
                                                                                        </PopoverContent>
                                                                                    </Popover>
                                                                                ) : param.type === "file" ? (
                                                                                    <Input
                                                                                        type="file"
                                                                                        className="h-8 text-xs"
                                                                                        onChange={(e) => {
                                                                                            // Simple file path handling for local app
                                                                                            const file = e.target.files?.[0];
                                                                                            if (file) {
                                                                                                // @ts-ignore
                                                                                                const path = file.path || file.name
                                                                                                handleParameterChange(auto.id, param.name, path)
                                                                                            }
                                                                                        }}
                                                                                    />
                                                                                ) : (
                                                                                    <Input
                                                                                        value={automationParams[auto.id]?.[param.name] || ""}
                                                                                        onChange={(e) => handleParameterChange(auto.id, param.name, e.target.value)}
                                                                                        placeholder={param.placeholder}
                                                                                        className="h-8 text-xs"
                                                                                    />
                                                                                )}
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        )
                                                    })}
                                                    {filteredAutomations.length === 0 && (
                                                        <div className="p-8 text-center text-muted-foreground text-sm border border-dashed rounded-lg">
                                                            No compatible automations found for the selected account providers.
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </ScrollArea>
                            </div>
                        )}
                    </div>

                    <div className="p-4 border-t border-border bg-card mt-auto gap-3 flex">
                        {step === "accounts" ? (
                            <Button variant="outline" onClick={() => onOpenChange(false)} className="flex-1">Cancel</Button>
                        ) : (
                            <Button variant="outline" onClick={prevStep} className="flex-1">
                                <ArrowLeft className="mr-2 h-4 w-4" /> Back
                            </Button>
                        )}

                        {step === "automation" ? (
                            <Button className="flex-1" onClick={handleLaunch} disabled={loading || selectedAutomationIds.length === 0}>
                                {loading ? "Launching..." : "Launch Job"} <Play className="ml-2 h-4 w-4 fill-current" />
                            </Button>
                        ) : (
                            <Button className="flex-1" onClick={nextStep} disabled={(step === "accounts" && Object.keys(selectedAccountIds).length === 0) || (step === "proxies" && Object.keys(selectedProxyIds).length === 0)}>
                                Next <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        )}
                    </div>
                </SheetContent>

                <Dialog open={importDialog.open} onOpenChange={(open) => !open && setImportDialog({ ...importDialog, open: false, file: null, text: undefined })}>
                    <DialogContent className="max-w-3xl h-[80vh] flex flex-col p-0 gap-0 bg-card">
                        <DialogHeader className="p-6 border-b border-border">
                            <DialogTitle>Import {importDialog.mode === "accounts" ? "Accounts" : "Proxies"}</DialogTitle>
                            <DialogDescription>
                                Review the items found in your {importDialog.file ? "file" : "text paste"}.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="flex-1 overflow-hidden p-6">
                            {/* @ts-ignore */}
                            <BulkImportForm
                                mode={importDialog.mode}
                                onCancel={() => setImportDialog({ ...importDialog, open: false, file: null, text: undefined })}
                                onSuccess={handleImportSuccess}
                                initialFile={importDialog.file}
                                initialText={importDialog.text}
                            />
                        </div>
                    </DialogContent>
                </Dialog>
            </Sheet>
        </>
    )
}
