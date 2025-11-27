"use client"

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { CheckCircle, XCircle, Clock } from "lucide-react"
import { HistoryEntry } from "@/lib/types"

interface AccountHistoryModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  accountEmail: string
  history: HistoryEntry[]
}

export function AccountHistoryModal({ open, onOpenChange, accountEmail, history }: AccountHistoryModalProps) {

  const getResultIcon = (result: HistoryEntry["status"]) => {
    switch (result) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-400" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-400" />
      case "running":
        return <Clock className="h-4 w-4 text-blue-400" />
    }
  }

  const getResultColor = (result: HistoryEntry["status"]) => {
    switch (result) {
      case "success":
        return "bg-green-500/10 text-green-400 border-green-500/20"
      case "failed":
        return "bg-red-500/10 text-red-400 border-red-500/20"
      case "running":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20"
    }
  }

  const formatDuration = (executedAt: string, completedAt: string) => {
    if (!completedAt) return "In progress..."
    
    const start = new Date(executedAt).getTime()
    const end = new Date(completedAt).getTime()
    const diff = end - start

    if (diff < 1000) return `${diff}ms`
    if (diff < 60000) return `${Math.floor(diff / 1000)}s`
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ${Math.floor((diff % 60000) / 1000)}s`
    return `${Math.floor(diff / 3600000)}h ${Math.floor((diff % 3600000) / 60000)}m`
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl bg-card border-border">
        <DialogHeader>
          <DialogTitle className="text-foreground">Account History</DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Last 10 automation runs for {accountEmail}
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="h-96 mt-4">
          <div className="space-y-3">
            {history.map((entry) => (
              <div key={entry.id} className="p-4 rounded-lg border border-border bg-accent/20">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getResultIcon(entry.status)}
                    <span className="font-medium text-foreground">{entry.action}</span>
                    <Badge className={getResultColor(entry.status)}>{entry.status}</Badge>
                  </div>
                  <span className="text-xs text-muted-foreground">{formatDuration(entry.executed_at, entry.completed_at)}</span>
                </div>
                <p className="text-sm text-muted-foreground mb-2 line-clamp-2" style={{ 
                      wordBreak: 'break-word',
                      overflowWrap: 'anywhere',
                      whiteSpace: 'pre-wrap',
                      maxWidth: '100%'
                    }}>
                    {entry.details}
                  </p>
                <p className="text-xs text-muted-foreground">{new Date(entry.executed_at).toLocaleString()}</p>
              </div>
            ))}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
