"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
    Maximize2,
    Minimize2,
    Play,
    Pause,
    Download,
    Search,
    AlertCircle,
    CheckCircle,
    Info,
    AlertTriangle,
} from "lucide-react"
import { LogDetailModal } from "./log-detail-modal"
import type { LogEntry, RunningJob } from "@/lib/types"
import { useLogs } from "@/hooks/useLogs"

export function LiveLogPanel() {
    // const [logs, setLogs] = useState<LogEntry[]>([])
    const [runningJobs, setRunningJobs] = useState<RunningJob[]>([])
    const [isExpanded, setIsExpanded] = useState(false)
    const [isPaused, setIsPaused] = useState(false)
    const [searchTerm, setSearchTerm] = useState("")
    const [levelFilter, setLevelFilter] = useState<string>("all")
    const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null)
    const scrollAreaRef = useRef<HTMLDivElement>(null)
    const [autoScroll, setAutoScroll] = useState(true)

    const logs = useLogs();

    // Auto-scroll to bottom when new logs arrive
    useEffect(() => {
        if (autoScroll && scrollAreaRef.current) {
            const scrollElement = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]")
            if (scrollElement) {
                scrollElement.scrollTop = scrollElement.scrollHeight
            }
        }
    }, [logs, autoScroll])

    const getLevelIcon = (level: LogEntry["level"]) => {
        switch (level) {
            case "SUCCESS":
                return <CheckCircle className="h-3 w-3 text-green-400" />
            case "WARNING":
                return <AlertTriangle className="h-3 w-3 text-yellow-400" />
            case "ERROR":
                return <AlertCircle className="h-3 w-3 text-red-400" />
            default:
                return <Info className="h-3 w-3 text-blue-400" />
        }
    }

    const getLevelColor = (level: LogEntry["level"]) => {
        switch (level) {
            case "SUCCESS":
                return "text-green-400"
            case "WARNING":
                return "text-yellow-400"
            case "ERROR":
                return "text-red-400"
            default:
                return "text-blue-400"
        }
    }

    const getStatusColor = (status: RunningJob["status"]) => {
        switch (status) {
            case "running":
                return "bg-green-500/10 text-green-400 border-green-500/20"
            case "completed":
                return "bg-blue-500/10 text-blue-400 border-blue-500/20"
            case "failed":
                return "bg-red-500/10 text-red-400 border-red-500/20"
            default:
                return "bg-gray-500/10 text-gray-400 border-gray-500/20"
        }
    }

    const filteredLogs = logs.filter((log) => {
        const matchesSearch = searchTerm === "" || log.message.toLowerCase().includes(searchTerm.toLowerCase())
        const matchesLevel = levelFilter === "all" || log.level === levelFilter
        return matchesSearch && matchesLevel
    })

    const exportLogs = () => {
        const logData = filteredLogs
            .map((log) => `${log.timestamp} [${log.level.toUpperCase()}] ${log.account?.email}: ${log.message}`)
            .join("\n")

        const blob = new Blob([logData], { type: "text/plain" })
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `gmail-automation-logs-${new Date().toISOString().split("T")[0]}.txt`
        a.click()
        URL.revokeObjectURL(url)
    }

    const getAccountEmail = (accountId: string): string => {
        // Mock account lookup
        const accountMap: Record<string, string> = {
            "1": "user1@gmail.com",
            "2": "user2@gmail.com",
            "3": "user3@gmail.com",
        }
        return accountMap[accountId] || "unknown@gmail.com"
    }

    const getAutomationName = (automationId: string): string => {
        const automationMap: Record<string, string> = {
            "send-template": "Send templated email",
            "archive-promotional": "Archive promotional",
            "check-session": "Check login/session",
        }
        return automationMap[automationId] || automationId
    }

    return (
        <>
            <Card className="bg-card border-border h-full flex flex-col">
                <CardHeader className="flex-shrink-0">
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-foreground">Live Activity</CardTitle>
                        <div className="flex items-center gap-2">
                            {/* <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsPaused(!isPaused)}
                className={isPaused ? "text-yellow-400" : "text-green-400"}
              >
                {isPaused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
              </Button> */}
                            <Button variant="ghost" size="sm" onClick={exportLogs}>
                                <Download className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" onClick={() => setIsExpanded(!isExpanded)}>
                                {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                            </Button>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="space-y-4 flex-1 flex flex-col min-h-0">
                    {/* Running Jobs */}
                    {/* {runningJobs.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-foreground">Running Jobs</h4>
              {runningJobs.map((job) => (
                <div key={job.id} className="p-3 rounded-lg border border-border bg-accent/20">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-foreground truncate">
                        {getAccountEmail(job.accountId)}
                      </span>
                      <Badge className={getStatusColor(job.status)}>{job.status}</Badge>
                    </div>
                    <span className="text-xs text-muted-foreground">{job.progress}%</span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">{getAutomationName(job.automationId)}</p>
                  <Progress value={job.progress} className="h-1" />
                  {job.result && <p className="text-xs text-muted-foreground mt-2">{job.result.summary}</p>}
                </div>
              ))}
            </div>
          )} */}

                    {/* Log Filters */}
                    <div className="flex gap-2 flex-shrink-0">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Search logs..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10 bg-input border-border"
                            />
                        </div>
                        <Select value={levelFilter} onValueChange={setLevelFilter}>
                            <SelectTrigger className="w-32 bg-input border-border">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Levels</SelectItem>
                                <SelectItem value="INFO">Info</SelectItem>
                                <SelectItem value="SUCCESS">Success</SelectItem>
                                <SelectItem value="WARNING">Warning</SelectItem>
                                <SelectItem value="ERROR">Error</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Live Logs */}
                    <div className="space-y-3 flex-1 flex flex-col min-h-0">
                        <div className="flex items-center justify-between flex-shrink-0">
                            <h4 className="text-sm font-medium text-foreground">
                                Live Logs ({filteredLogs.length})
                                {/* {isPaused && <Badge className="ml-2 bg-yellow-500/10 text-yellow-400">Paused</Badge>} */}
                            </h4>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setAutoScroll(!autoScroll)}
                                className={autoScroll ? "text-green-400" : "text-muted-foreground"}
                            >
                                Auto-scroll
                            </Button>
                        </div>
                        <ScrollArea
                            ref={scrollAreaRef}
                            className="flex-1 rounded-lg border border-border bg-accent/10"
                        >
                            <div className="p-3 space-y-1">
                                {filteredLogs.map((log, index) => (
                                    <div
                                        key={index}
                                        className="flex flex-col gap-2 text-xs font-mono hover:bg-accent/30 p-1 rounded cursor-pointer transition-colors"
                                        onClick={() => setSelectedLog(log)}
                                    >
                                        <div className="flex gap-2 items-center">
                                            <div className="shrink-0 flex items-center w-16">
                                                {getLevelIcon(log.level)}
                                                <span className={`ml-1 uppercase font-bold ${getLevelColor(log.level)}`}>{log.level}</span>
                                            </div>
                                            <span className="text-muted-foreground shrink-0 w-20">{new Date(log.timestamp).toLocaleTimeString()}</span>
                                        </div>
                                        {/* <span className="text-muted-foreground shrink-0 w-32 truncate">{log.account_email}</span> */}
                                        <span className="text-foreground line-clamp-1" style={{ maxWidth: "calc(100vw - 2rem - 4px)" }}>
                                            {log.message}
                                        </span>
                                    </div>
                                ))}
                                {filteredLogs.length === 0 && (
                                    <div className="text-center py-8 text-muted-foreground">
                                        {searchTerm || levelFilter !== "all" ? "No logs match your filters" : "No logs available"}
                                    </div>
                                )}
                            </div>
                        </ScrollArea>
                    </div>
                </CardContent>
            </Card>

            <LogDetailModal open={!!selectedLog} onOpenChange={() => setSelectedLog(null)} log={selectedLog} />
        </>
    )
}
