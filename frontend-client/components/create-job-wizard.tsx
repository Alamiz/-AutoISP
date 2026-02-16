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
import { Play, Info, ArrowRight, ArrowLeft, Plus, CheckCircle2, User, Globe, Mail, Shield, Settings, Search, FlaskConical, Zap, Calendar as CalendarIcon, FileSpreadsheet, Upload } from "lucide-react"
import { automations } from "@/data/automations"
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
import { format } from "date-fns"

interface CreateJobWizardProps {
    open: boolean
    onOpenChange: (open: boolean) => void
}

type WizardStep = "accounts" | "proxies" | "automation"

export function CreateJobWizard({ open, onOpenChange }: CreateJobWizardProps) {
    const router = useRouter()
    const [step, setStep] = useState<WizardStep>("accounts")
    const [loading, setLoading] = useState(false)

    // Data State
    const [accounts, setAccounts] = useState<Account[]>([])
    const [proxies, setProxies] = useState<any[]>([])
    const [selectedAccountIds, setSelectedAccountIds] = useState<string[]>([])
    const [selectedProxyIds, setSelectedProxyIds] = useState<string[]>([])

    // Automation State
    const [jobName, setJobName] = useState("")
    const [maxConcurrent, setMaxConcurrent] = useState(5)
    // We only allow SINGLE automation selection for simplicity in this flow, or should we keep multiple?
    // User asked for "configure automations". automation-controls allows multiple. The wizard previously allowed multiple.
    // Let's keep multiple but effectively manage them.
    const [selectedAutomationIds, setSelectedAutomationIds] = useState<string[]>([])
    const [automationParams, setAutomationParams] = useState<Record<string, Record<string, any>>>({})
    const [configuringAutomationId, setConfiguringAutomationId] = useState<string | null>(null)

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
        if (open) {
            fetchAccounts()
            fetchProxies()
            setStep("accounts")
            setSelectedAccountIds([])
            setSelectedAutomationIds([])
            setAutomationParams({})
            setJobName("")
        }
    }, [open])

    const fetchAccounts = async () => {
        try {
            const res = await apiGet<any>("/accounts?page_size=10000", "local")
            setAccounts(res?.items || [])
        } catch (err) {
            console.error(err)
            toast.error("Failed to load accounts")
        }
    }

    const fetchProxies = async () => {
        try {
            const res = await apiGet<any>("/proxies?page_size=10000", "local")
            const items = res?.items || []
            setProxies(items)
            // Select all by default
            setSelectedProxyIds(items.map((p: any) => String(p.id)))
        } catch (err) {
            console.error(err)
            toast.error("Failed to load proxies")
        }
    }

    // Selection Handlers
    const handleImportSuccess = (ids: number[]) => {
        if (importDialog.mode === "accounts") {
            fetchAccounts().then(() => {
                const newIds = ids.map(String)
                setSelectedAccountIds(prev => [...Array.from(new Set([...prev, ...newIds]))])
            })
        } else {
            fetchProxies().then(() => {
                const newIds = ids.map(String)
                setSelectedProxyIds(prev => [...Array.from(new Set([...prev, ...newIds]))])
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

    const toggleAllAccounts = () => {
        if (selectedAccountIds.length === accounts.length && accounts.length > 0) {
            setSelectedAccountIds([])
        } else {
            setSelectedAccountIds(accounts.map(a => String(a.id)))
        }
    }

    const toggleAllProxies = () => {
        if (selectedProxyIds.length === proxies.length && proxies.length > 0) {
            setSelectedProxyIds([])
        } else {
            setSelectedProxyIds(proxies.map(p => String(p.id)))
        }
    }

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
        const selectedAccs = accounts.filter(a => selectedAccountIds.includes(String(a.id)))
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
        } else {
            setSelectedAutomationIds(prev => prev.filter(i => i !== id))
            const newParams = { ...automationParams }
            delete newParams[id]
            setAutomationParams(newParams)
        }
    }

    // Launch Handler
    const handleLaunch = async () => {
        if (selectedAccountIds.length === 0) {
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

            const selectedAccs = accounts.filter(a => selectedAccountIds.includes(String(a.id)))

            const payload = {
                name: jobName || `Job ${new Date().toLocaleString()}`,
                max_concurrent: maxConcurrent,
                accounts: selectedAccs.map(acc => ({
                    email: acc.email,
                    password: acc.credentials?.password || "",
                    provider: acc.provider,
                    recovery_email: acc.credentials?.recovery_email || undefined,
                    phone_number: acc.credentials?.number || undefined,
                    status: acc.status
                })),
                proxy_ids: selectedProxyIds.map(Number),
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
                            className={`flex-1 flex flex-col p-6 h-full overflow-hidden transition-colors ${dragActive ? "bg-primary/5" : ""}`}
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
                                            <p className="text-lg font-medium text-primary">Drop files to import accounts</p>
                                        </div>
                                    </div>
                                )}
                                <div className="flex items-center justify-between p-2 px-3 border-b bg-muted/40 z-20">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                                            <Badge variant="secondary" className="text-[10px] h-5 px-1.5 font-mono">{selectedAccountIds.length}</Badge> Selected
                                        </span>
                                        <div className="h-3 w-px bg-border mx-1" />
                                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                                            <Badge variant="outline" className="text-[10px] h-5 px-1.5 font-mono">{accounts.length}</Badge> Available
                                        </span>
                                    </div>
                                    <div className="flex gap-1">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-7 text-xs gap-1"
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
                                </div>
                                <div className="flex-1 overflow-auto">
                                    <Table>
                                        <TableHeader className="sticky top-0 z-10 bg-muted">
                                            <TableRow>
                                                <TableHead className="w-[50px] pl-4">
                                                    <Checkbox
                                                        checked={selectedAccountIds.length === accounts.length && accounts.length > 0}
                                                        onCheckedChange={toggleAllAccounts}
                                                    />
                                                </TableHead>
                                                <TableHead>Email</TableHead>
                                                <TableHead>Provider</TableHead>
                                                <TableHead className="text-right pr-4">Status</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {accounts.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                                                        No accounts found. Drag & drop a file or paste text to import.
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                            {accounts.map((acc) => {
                                                const isSelected = selectedAccountIds.includes(String(acc.id))
                                                return (
                                                    <TableRow
                                                        key={acc.id}
                                                        className="cursor-pointer hover:bg-muted/50 select-none"
                                                        onClick={() => {
                                                            const id = String(acc.id)
                                                            setSelectedAccountIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id])
                                                        }}
                                                        data-state={isSelected ? "selected" : undefined}
                                                    >
                                                        <TableCell className="pl-4 py-2" onClick={(e) => e.stopPropagation()}>
                                                            <Checkbox
                                                                checked={isSelected}
                                                                onCheckedChange={() => {
                                                                    const id = String(acc.id)
                                                                    setSelectedAccountIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id])
                                                                }}
                                                            />
                                                        </TableCell>
                                                        <TableCell className="py-2 font-medium">{acc.email}</TableCell>
                                                        <TableCell className="py-2 text-muted-foreground">{acc.provider}</TableCell>
                                                        <TableCell className="py-2 text-right pr-4">
                                                            <span className={`text-xs ${acc.status === 'active' ? 'text-green-500' : 'text-muted-foreground'}`}>{acc.status}</span>
                                                        </TableCell>
                                                    </TableRow>
                                                )
                                            })}
                                        </TableBody>
                                    </Table>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* STEP 2: PROXIES */}
                    {step === "proxies" && (
                        <div
                            className={`flex-1 flex flex-col p-6 h-full overflow-hidden transition-colors ${dragActive ? "bg-primary/5" : ""}`}
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
                                <div className="flex items-center justify-between p-2 px-3 border-b bg-muted/40 z-20">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                                            <Badge variant="secondary" className="text-[10px] h-5 px-1.5 font-mono">{selectedProxyIds.length}</Badge> Selected
                                        </span>
                                        <div className="h-3 w-px bg-border mx-1" />
                                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                                            <Badge variant="outline" className="text-[10px] h-5 px-1.5 font-mono">{proxies.length}</Badge> Available
                                        </span>
                                    </div>
                                    <div className="flex gap-1">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-7 text-xs gap-1"
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
                                </div>
                                <div className="flex-1 overflow-auto">
                                    <Table>
                                        <TableHeader className="sticky top-0 z-10 bg-muted">
                                            <TableRow>
                                                <TableHead className="w-[50px] pl-4">
                                                    <Checkbox
                                                        checked={selectedProxyIds.length === proxies.length && proxies.length > 0}
                                                        onCheckedChange={toggleAllProxies}
                                                    />
                                                </TableHead>
                                                <TableHead>Address</TableHead>
                                                <TableHead>Port</TableHead>
                                                <TableHead className="text-right pr-4">Auth</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {proxies.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                                                        No proxies found. Drag & drop a file or paste text to import.
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                            {proxies.map((proxy) => {
                                                const isSelected = selectedProxyIds.includes(String(proxy.id))
                                                return (
                                                    <TableRow
                                                        key={proxy.id}
                                                        className="cursor-pointer hover:bg-muted/50 select-none"
                                                        onClick={() => {
                                                            const id = String(proxy.id)
                                                            setSelectedProxyIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id])
                                                        }}
                                                        data-state={isSelected ? "selected" : undefined}
                                                    >
                                                        <TableCell className="pl-4 py-2" onClick={(e) => e.stopPropagation()}>
                                                            <Checkbox
                                                                checked={isSelected}
                                                                onCheckedChange={() => {
                                                                    const id = String(proxy.id)
                                                                    setSelectedProxyIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id])
                                                                }}
                                                            />
                                                        </TableCell>
                                                        <TableCell className="py-2 font-medium font-mono text-xs">{proxy.ip}</TableCell>
                                                        <TableCell className="py-2 font-mono text-xs">{proxy.port}</TableCell>
                                                        <TableCell className="py-2 text-right pr-4 text-xs text-muted-foreground">
                                                            {proxy.username ? "Enabled" : "None"}
                                                        </TableCell>
                                                    </TableRow>
                                                )
                                            })}
                                        </TableBody>
                                    </Table>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* STEP 3: AUTOMATION */}
                    {step === "automation" && (
                        <div className="flex-1 flex flex-col h-full p-6 overflow-hidden">
                            <ScrollArea className="h-full pr-4">
                                <div className="space-y-6">
                                    <div className="space-y-4">
                                        <div className="space-y-2">
                                            <Label htmlFor="jobName">Job Name (Optional)</Label>
                                            <Input
                                                id="jobName"
                                                placeholder="Morning Warmup Run"
                                                value={jobName}
                                                onChange={(e) => setJobName(e.target.value)}
                                                className="bg-input border-border"
                                            />
                                        </div>

                                        <div className="space-y-2">
                                            <Label htmlFor="concurrency">Max Concurrent Threads</Label>
                                            <Input
                                                id="concurrency"
                                                type="number"
                                                min={1}
                                                max={50}
                                                value={maxConcurrent}
                                                onChange={(e) => setMaxConcurrent(parseInt(e.target.value))}
                                                className="bg-input border-border"
                                            />
                                            <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                                                <Info className="h-3 w-3" />
                                                Higher values require more system resources.
                                            </p>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2">
                                            <Label className="text-base">Select Automation</Label>
                                            <Badge variant="outline">{selectedAutomationIds.length} selected</Badge>
                                        </div>

                                        <div className="space-y-3">
                                            {filteredAutomations.map((auto) => {
                                                const isSelected = selectedAutomationIds.includes(auto.id)
                                                const hasParams = auto.params && auto.params.length > 0
                                                const isExpanded = configuringAutomationId === auto.id

                                                // Check if valid config
                                                const isValid = !hasParams || (auto.params || []).every(p => !p.required || (automationParams[auto.id]?.[p.name] && automationParams[auto.id]?.[p.name].toString().trim() !== ""))

                                                return (
                                                    <div key={auto.id} className={`rounded-lg border transition-all ${isSelected ? "border-primary/50 bg-primary/5" : "border-border bg-card hover:border-primary/20"}`}>
                                                        <div className="p-3 flex items-start gap-3">
                                                            <Checkbox
                                                                checked={isSelected}
                                                                onCheckedChange={(c) => handleToggleAutomation(auto.id, !!c)}
                                                                className="mt-1"
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
                                                                            onClick={() => setConfiguringAutomationId(isExpanded ? null : auto.id)}
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
                                                            <div className="border-t border-border/50 p-4 bg-background/50 space-y-3 animate-in fade-in slide-in-from-top-1">
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
                                </div>
                            </ScrollArea>
                        </div>
                    )}
                </div>

                <div className="p-6 border-t border-border bg-card mt-auto gap-3 flex">
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
                        <Button className="flex-1" onClick={nextStep} disabled={step === "accounts" && selectedAccountIds.length === 0}>
                            Next <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    )}
                </div>
            </SheetContent >
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
        </Sheet >
    )
}
