"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Database, CheckCircle2, AlertCircle, Loader2 } from "lucide-react"
import { Account } from "@/lib/types"
import { ApiError, apiPost } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

interface BackupModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  account: Account | null
  onBackupComplete: () => void
}

export function BackupModal({
  open,
  onOpenChange,
  account,
  onBackupComplete,
}: BackupModalProps) {
  const [isBackingUp, setIsBackingUp] = useState(false)
  const [backupProgress, setBackupProgress] = useState(0)
  const [backupStatus, setBackupStatus] = useState<"idle" | "backing-up" | "success" | "error">("idle")
  const [stepText, setStepText] = useState("")

  const backups = account?.backups ?? [];
  const lastBackupIndex = backups.length - 1
  const hasBackup = backups.length > 0 && backups[lastBackupIndex].filename;
  const lastBackup = backups[lastBackupIndex];
  const lastBackupDate = new Date(lastBackup?.created_at).toLocaleString();

  const queryClient = useQueryClient()

  // Reset state when modal closes
  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setBackupStatus("idle")
      setBackupProgress(0)
      setIsBackingUp(false)
    }
    onOpenChange(newOpen)
  }

  const startBackup = useMutation({
    mutationFn: async (accountId: string) => {
      setIsBackingUp(true)
      await apiPost(`/backups/${accountId}/start`, {}, "local")
      return accountId
    },
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["accounts"] })
      setBackupStatus("backing-up")
      setBackupProgress(0)
      return
    },
    onError: (err) => {
      setBackupStatus("error")

      if (err instanceof ApiError) {
        const errMessage = err?.data?.detail || err?.data?.message || err.message
        console.error(`Backup Error: ${errMessage}`);
        toast.error(`Backup Error: ${errMessage}`)
      } else {
        console.error(`Uknown Error: ${err}`);
        toast.error(`Uknown Error: ${err}`)
      }
    },
    onSuccess: () => {
      toast.success("Backup started successfully")
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] })
    }
  })

  const handleStartBackup = () => {
    if (account) {
      setBackupStatus("idle")
      startBackup.mutate(account.id);
    }
  }

  // 🔹 WebSocket connection for real-time progress
  // useEffect(() => {
  //   console.log("account", account)
  //   if (!account) return

  //   const ws = new WebSocket(`ws://localhost:8001/backups/${account.id}/progress`)

  //   ws.onopen = () => console.log("Backup WebSocket opened")
  //   ws.onmessage = (event) => {
  //     const data = JSON.parse(event.data)
  //     console.log("Backup Progress:", data)
  //     if (data.percent !== undefined) {
  //       console.log("Backup Progress:", data.percent)
  //       setBackupProgress(data.percent)
  //       setStepText(data.step)
  //     }
  //     if (data.status === "completed") {
  //       setBackupStatus("success")
  //       setIsBackingUp(false)
  //       onBackupComplete()
  //       toast.success("Backup completed successfully")
  //     }
  //   }

  //   ws.onclose = () => console.log("Backup WebSocket closed")
  //   ws.onerror = (err) => {
  //     setBackupStatus("error")
  //     toast.error("Backup connection failed")
  //   }

  //   return () => ws.close()
  // }, [account])

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="bg-card border-border">
        <DialogHeader>
          <DialogTitle className="text-foreground flex items-center gap-2">
            <Database className="h-5 w-5" />
            Profile Backup
          </DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Create a backup of the Gmail profile for {account?.email}.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {hasBackup && lastBackupDate && (
            <div className="p-3 bg-accent/30 rounded-lg border border-border">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle2 className="h-4 w-4 text-green-400" />
                <p className="text-sm font-medium text-foreground">Existing Backup Found</p>
              </div>
              <p className="text-xs text-muted-foreground">Last backup: {lastBackupDate}</p>
            </div>
          )}

          {backupStatus === "backing-up" && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                <p className="text-sm text-foreground">{stepText}</p>
              </div>
              <Progress value={backupProgress} className="h-2" />
              <p className="text-xs text-muted-foreground">{backupProgress}% complete</p>
            </div>
          )}

          {backupStatus === "success" && (
            <div className="p-3 bg-green-500/10 rounded-lg border border-green-500/20">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-400" />
                <p className="text-sm font-medium text-green-400">Backup completed successfully!</p>
              </div>
            </div>
          )}

          {backupStatus === "error" && (
            <div className="p-3 bg-red-500/10 rounded-lg border border-red-500/20">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-red-400" />
                <p className="text-sm font-medium text-red-400">Backup failed. Please try again.</p>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <p className="text-sm font-medium text-foreground">What will be backed up:</p>
            <ul className="text-sm text-muted-foreground space-y-1 ml-4">
              <li>• Account credentials (encrypted)</li>
              <li>• Email filters and labels</li>
              <li>• Automation history</li>
              <li>• Configuration settings</li>
            </ul>
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => handleOpenChange(false)} disabled={isBackingUp}>
            Cancel
          </Button>
          <Button onClick={handleStartBackup} disabled={isBackingUp}>
            {isBackingUp ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Backing up...
              </>
            ) : (
              <>
                <Database className="h-4 w-4 mr-2" />
                {hasBackup ? "Create New Backup" : "Create Backup"}
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
