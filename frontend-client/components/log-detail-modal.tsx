"use client"

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Copy, ExternalLink } from "lucide-react"
import type { LogEntry } from "@/lib/types"

interface LogDetailModalProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    log: LogEntry | null
}

export function LogDetailModal({ open, onOpenChange, log }: LogDetailModalProps) {
    if (!log) return null

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
    }

    const getLevelColor = (level: LogEntry["level"]) => {
        switch (level) {
            case "SUCCESS":
                return "bg-green-500/10 text-green-400 border-green-500/20"
            case "WARNING":
                return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
            case "ERROR":
                return "bg-red-500/10 text-red-400 border-red-500/20"
            default:
                return "bg-blue-500/10 text-blue-400 border-blue-500/20"
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl bg-card border-border">
                <DialogHeader>
                    <DialogTitle className="text-foreground">Log Entry Details</DialogTitle>
                    <DialogDescription className="text-muted-foreground">
                        Detailed information about this log entry and associated metadata.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6 mt-4">
                    {/* Basic Information */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <h4 className="text-sm font-medium text-foreground">Timestamp</h4>
                            <p className="text-sm text-muted-foreground font-mono">{log.timestamp}</p>
                        </div>
                        <div className="space-y-2">
                            <h4 className="text-sm font-medium text-foreground">Level</h4>
                            <Badge className={getLevelColor(log.level)}>{log.level.toUpperCase()}</Badge>
                        </div>
                        <div className="space-y-2">
                            <h4 className="text-sm font-medium text-foreground">Account</h4>
                            <p className="text-sm text-muted-foreground break-all">{log.account?.email}</p>
                        </div>
                        <div className="space-y-2">
                            <h4 className="text-sm font-medium text-foreground">Activity</h4>
                            <p className="text-sm text-muted-foreground">{log.activity_id || "N/A"}</p>
                        </div>
                    </div>

                    {/* Message */}
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <h4 className="text-sm font-medium text-foreground">Message</h4>
                            <Button variant="ghost" size="sm" onClick={() => copyToClipboard(log.message)} className="h-6 px-2">
                                <Copy className="h-3 w-3" />
                            </Button>
                        </div>
                        <div className="p-3 rounded-lg border border-border bg-accent/20 max-h-48 overflow-auto">
                            <p
                                className="text-sm text-foreground"
                                style={{
                                    wordBreak: 'break-word',
                                    overflowWrap: 'anywhere',
                                    whiteSpace: 'pre-wrap',
                                    maxWidth: '100%'
                                }}
                            >
                                {log.message}
                            </p>
                        </div>
                    </div>

                    {/* Metadata */}
                    {/* {log.metadata && Object.keys(log.metadata).length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-foreground">Metadata</h4>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(JSON.stringify(log.metadata, null, 2))}
              className="h-6 px-2"
            >
              <Copy className="h-3 w-3" />
            </Button>
          </div>
          <ScrollArea className="h-32 rounded-lg border border-border bg-accent/20">
            <pre className="p-3 text-xs text-foreground font-mono break-all whitespace-pre-wrap">
              {JSON.stringify(log.metadata, null, 2)}
            </pre>
          </ScrollArea>
        </div>
      )} */}

                    {/* Raw Log Entry */}
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <h4 className="text-sm font-medium text-foreground">Raw Log Entry</h4>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => copyToClipboard(JSON.stringify(log, null, 2))}
                                className="h-6 px-2"
                            >
                                <Copy className="h-3 w-3" />
                            </Button>
                        </div>
                        <ScrollArea className="h-32 rounded-lg border border-border bg-accent/20">
                            <pre className="p-3 text-xs text-foreground font-mono break-all whitespace-pre-wrap">
                                {JSON.stringify(log, null, 2)}
                            </pre>
                        </ScrollArea>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 pt-4">
                        <Button
                            variant="outline"
                            onClick={() => onOpenChange(false)}
                            className="flex-1 border-border hover:bg-accent"
                        >
                            Close
                        </Button>
                        {log.activity_id && (
                            <Button variant="outline" className="flex-1 border-border hover:bg-accent bg-transparent">
                                <ExternalLink className="h-4 w-4 mr-2" />
                                View Automation
                            </Button>
                        )}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    )
}
