"use client"

import * as React from "react"
import {
    RefreshCw,
    Download,
    ArrowUpCircle,
    Loader2,
} from "lucide-react"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { Progress } from "@/components/ui/progress"
import {
    SidebarMenu,
    SidebarMenuItem,
    SidebarMenuButton,
    useSidebar,
} from "@/components/ui/sidebar"
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
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from "@/components/ui/tooltip"

// ── Types ──────────────────────────────────────────────────────────────────
type UpdateStatus =
    | "idle"
    | "checking"
    | "available"
    | "not-available"
    | "downloading"
    | "downloaded"
    | "error"

interface UpdateProgress {
    percent: number
    bytesPerSecond: number
    transferred: number
    total: number
}

interface UpdateEvent {
    type: string
    version?: string
    percent?: number
    bytesPerSecond?: number
    transferred?: number
    total?: number
    message?: string
}

// Extend Window for the updater preload API
declare global {
    interface Window {
        updater?: {
            checkForUpdates: () => Promise<void>
            downloadUpdate: () => Promise<void>
            installUpdate: () => Promise<void>
            onUpdateEvent: (callback: (event: UpdateEvent) => void) => () => void
        }
    }
}

// ── Component ──────────────────────────────────────────────────────────────
export function UpdateStatus() {
    const { state: sidebarState } = useSidebar()
    const isCollapsed = sidebarState === "collapsed"

    const [status, setStatus] = React.useState<UpdateStatus>("idle")
    const [progress, setProgress] = React.useState<UpdateProgress>({
        percent: 0,
        bytesPerSecond: 0,
        transferred: 0,
        total: 0,
    })
    const [latestVersion, setLatestVersion] = React.useState<string>("")
    const [confirmOpen, setConfirmOpen] = React.useState(false)

    // Subscribe to update events from main process
    React.useEffect(() => {
        if (!window.updater) return

        const unsubscribe = window.updater.onUpdateEvent((event: UpdateEvent) => {
            switch (event.type) {
                case "checking":
                    setStatus("checking")
                    break

                case "available":
                    setStatus("available")
                    setLatestVersion(event.version || "")
                    toast.info(`Update available: v${event.version}`, {
                        description: "Click \"Download update\" in the sidebar.",
                        duration: 6000,
                    })
                    break

                case "not-available":
                    setStatus("not-available")
                    toast.success("You're up to date!", { duration: 3000 })
                    // Reset to idle after a few seconds
                    setTimeout(() => setStatus("idle"), 4000)
                    break

                case "progress":
                    setStatus("downloading")
                    setProgress({
                        percent: event.percent ?? 0,
                        bytesPerSecond: event.bytesPerSecond ?? 0,
                        transferred: event.transferred ?? 0,
                        total: event.total ?? 0,
                    })
                    break

                case "downloaded":
                    setStatus("downloaded")
                    setLatestVersion(event.version || "")
                    toast.success("Download complete — ready to install", {
                        duration: 5000,
                    })
                    break

                case "error":
                    setStatus("error")
                    toast.error(`Update error: ${event.message || "Unknown error"}`, {
                        duration: 5000,
                    })
                    // Reset to idle after a few seconds
                    setTimeout(() => setStatus("idle"), 5000)
                    break
            }
        })

        return () => {
            unsubscribe()
        }
    }, [])

    // ── Handlers ───────────────────────────────────────────────────────────
    const handleCheckForUpdates = async () => {
        if (!window.updater) return
        try {
            setStatus("checking")
            await window.updater.checkForUpdates()
        } catch {
            setStatus("error")
            toast.error("Failed to check for updates")
            setTimeout(() => setStatus("idle"), 4000)
        }
    }

    const handleDownloadUpdate = async () => {
        if (!window.updater) return
        try {
            setStatus("downloading")
            setProgress({ percent: 0, bytesPerSecond: 0, transferred: 0, total: 0 })
            await window.updater.downloadUpdate()
        } catch {
            setStatus("error")
            toast.error("Failed to download update")
            setTimeout(() => setStatus("idle"), 4000)
        }
    }

    const handleInstallUpdate = () => {
        setConfirmOpen(true)
    }

    const handleConfirmInstall = async () => {
        setConfirmOpen(false)
        if (!window.updater) return
        try {
            await window.updater.installUpdate()
        } catch {
            toast.error("Failed to install update")
        }
    }

    // ── Badge visibility ───────────────────────────────────────────────────
    const showBadge = status === "available" || status === "downloaded"

    // ── Render helpers ─────────────────────────────────────────────────────
    const renderButton = () => {
        switch (status) {
            case "checking":
                return (
                    <SidebarMenuButton
                        size="sm"
                        disabled
                        className="text-muted-foreground cursor-not-allowed"
                        tooltip="Checking for updates…"
                    >
                        <Loader2 className="size-4 animate-spin" />
                        {!isCollapsed && (
                            <span className="truncate text-xs">Checking…</span>
                        )}
                    </SidebarMenuButton>
                )

            case "available":
                return (
                    <SidebarMenuButton
                        size="sm"
                        onClick={handleDownloadUpdate}
                        className="text-emerald-500 hover:text-emerald-400 cursor-pointer"
                        tooltip={`Download update v${latestVersion}`}
                    >
                        <div className="relative">
                            <Download className="size-4" />
                            {showBadge && (
                                <span className="absolute -top-1 -right-1 size-2 rounded-full bg-emerald-500" />
                            )}
                        </div>
                        {!isCollapsed && (
                            <span className="truncate text-xs font-medium">
                                Download update
                            </span>
                        )}
                    </SidebarMenuButton>
                )

            case "downloading":
                return (
                    <div className="flex flex-col gap-1.5 px-2 py-1.5 w-full">
                        {!isCollapsed ? (
                            <>
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-muted-foreground">Downloading…</span>
                                    <span className="text-xs font-medium tabular-nums">
                                        {Math.round(progress.percent)}%
                                    </span>
                                </div>
                                <Progress value={progress.percent} className="h-1.5" />
                            </>
                        ) : (
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <div className="flex items-center justify-center">
                                        <Loader2 className="size-4 animate-spin text-muted-foreground" />
                                    </div>
                                </TooltipTrigger>
                                <TooltipContent side="right">
                                    Downloading… {Math.round(progress.percent)}%
                                </TooltipContent>
                            </Tooltip>
                        )}
                    </div>
                )

            case "downloaded":
                return (
                    <SidebarMenuButton
                        size="sm"
                        onClick={handleInstallUpdate}
                        className="text-emerald-500 hover:text-emerald-400 cursor-pointer"
                        tooltip="Install update and restart"
                    >
                        <div className="relative">
                            <ArrowUpCircle className="size-4" />
                            {showBadge && (
                                <span className="absolute -top-1 -right-1 size-2 rounded-full bg-emerald-500 animate-pulse" />
                            )}
                        </div>
                        {!isCollapsed && (
                            <span className="truncate text-xs font-medium">
                                Install update
                            </span>
                        )}
                    </SidebarMenuButton>
                )

            // idle, not-available, error — all show "Check for updates"
            default:
                return (
                    <SidebarMenuButton
                        size="sm"
                        onClick={handleCheckForUpdates}
                        className="text-muted-foreground hover:text-foreground cursor-pointer"
                        tooltip="Check for updates"
                    >
                        <RefreshCw className="size-4" />
                        {!isCollapsed && (
                            <span className="truncate text-xs">Check for updates</span>
                        )}
                    </SidebarMenuButton>
                )
        }
    }

    return (
        <>
            <SidebarMenu>
                <SidebarMenuItem>{renderButton()}</SidebarMenuItem>
            </SidebarMenu>

            {/* Confirm dialog for install */}
            <AlertDialog open={confirmOpen} onOpenChange={setConfirmOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Install Update?</AlertDialogTitle>
                        <AlertDialogDescription>
                            The app will close and any running automations will be stopped.
                            {latestVersion && (
                                <>
                                    {" "}
                                    You are installing <strong>v{latestVersion}</strong>.
                                </>
                            )}
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleConfirmInstall}>
                            Install & Restart
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </>
    )
}
