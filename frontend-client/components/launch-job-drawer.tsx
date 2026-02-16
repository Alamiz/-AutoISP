"use client"

import { useState } from "react"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Play, Settings2, Info } from "lucide-react"
import { automations } from "@/data/automations"
import { Account } from "@/lib/types"
import { apiPost } from "@/lib/api"
import { toast } from "sonner"
import { useRouter } from "next/navigation"

interface LaunchJobDrawerProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    selectedAccounts: Account[]
}

export function LaunchJobDrawer({ open, onOpenChange, selectedAccounts }: LaunchJobDrawerProps) {
    const router = useRouter()
    const [loading, setLoading] = useState(false)
    const [jobName, setJobName] = useState("")
    const [maxConcurrent, setMaxConcurrent] = useState(5)
    const [selectedAutomationIds, setSelectedAutomationIds] = useState<string[]>([])

    const filteredAutomations = automations.filter(a =>
        selectedAccounts.every(acc => a.provider === "all" || a.provider === acc.provider)
    )

    const handleToggleAutomation = (id: string) => {
        setSelectedAutomationIds(prev =>
            prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
        )
    }

    const handleLaunch = async () => {
        try {
            setLoading(true)

            const payload = {
                name: jobName || `Job ${new Date().toLocaleString()}`,
                max_concurrent: maxConcurrent,
                accounts: selectedAccounts.map(acc => ({
                    email: acc.email,
                    password: acc.credentials?.password || "", // Fallback
                    provider: acc.provider,
                    recovery_email: acc.credentials?.recovery_email || undefined,
                    phone_number: acc.credentials?.number || undefined,
                    status: acc.status
                })),
                proxy_ids: [], // TODO: Add proxy selection if needed
                automations: selectedAutomationIds.map((id, index) => ({
                    automation_name: id,
                    run_order: index,
                    settings: {},
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
            <SheetContent className="bg-card border-border p-0 sm:max-w-md w-full">
                <div className="p-6 pb-2">
                    <SheetHeader>
                        <SheetTitle className="text-foreground">Launch Automation</SheetTitle>
                        <SheetDescription className="text-muted-foreground">
                            Configure and start a new job for {selectedAccounts.length} selected accounts.
                        </SheetDescription>
                    </SheetHeader>
                </div>

                <ScrollArea className="h-[calc(100vh-140px)] px-4">
                    <div className="space-y-8 pb-6 p-2">
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
                                <Label>Select Automations</Label>
                                <Badge variant="outline">{selectedAutomationIds.length} selected</Badge>
                            </div>

                            <div className="space-y-3">
                                {filteredAutomations.map((auto) => (
                                    <Card
                                        key={auto.id}
                                        className={`border-border transition-colors cursor-pointer ${selectedAutomationIds.includes(auto.id)
                                                ? "bg-primary/5 ring-1 ring-primary/20"
                                                : "bg-background hover:bg-accent/50"
                                            }`}
                                        onClick={() => handleToggleAutomation(auto.id)}
                                    >
                                        <CardContent className="p-4 flex items-start gap-4">
                                            <Checkbox
                                                checked={selectedAutomationIds.includes(auto.id)}
                                                onCheckedChange={() => handleToggleAutomation(auto.id)}
                                                className="mt-1"
                                            />
                                            <div className="flex-1 space-y-1">
                                                <div className="flex items-center justify-between">
                                                    <span className="font-medium text-sm">{auto.name}</span>
                                                    <span className="text-[10px] text-muted-foreground">{auto.estimatedDuration}</span>
                                                </div>
                                                <p className="text-xs text-muted-foreground leading-relaxed">
                                                    {auto.description}
                                                </p>
                                                <div className="flex gap-2 pt-1">
                                                    <Badge variant="secondary" className="text-[10px] font-normal uppercase">
                                                        {auto.category}
                                                    </Badge>
                                                    <Badge variant="outline" className="text-[10px] font-normal uppercase">
                                                        {auto.provider}
                                                    </Badge>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </div>

                        <div className="flex gap-3 pt-4">
                            <Button
                                variant="outline"
                                onClick={() => onOpenChange(false)}
                                className="flex-1 border-border"
                            >
                                Cancel
                            </Button>
                            <Button
                                className="flex-1"
                                disabled={loading || selectedAutomationIds.length === 0}
                                onClick={handleLaunch}
                            >
                                <Play className="mr-2 h-4 w-4 fill-current" />
                                {loading ? "Launching..." : "Launch Job"}
                            </Button>
                        </div>
                    </div>
                </ScrollArea>
            </SheetContent>
        </Sheet>
    )
}
