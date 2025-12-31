"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Checkbox } from "@/components/ui/checkbox"
import { Upload, CheckCircle2, AlertTriangle, Loader2, AlertCircle } from "lucide-react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { ApiError, apiPost } from "@/lib/api"
import { toast } from "sonner"
import { Backup } from "@/lib/types"
import { formatBytes } from "@/utils/formatters"

interface RestoreModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  accountEmail: string
  backup?: Backup | null
  onRestoreComplete: () => void
}

export function RestoreModal({
  open,
  onOpenChange,
  accountEmail,
  backup,
  onRestoreComplete,
}: RestoreModalProps) {
  const [isRestoring, setIsRestoring] = useState(false)
  const [restoreProgress, setRestoreProgress] = useState(0)
  const [restoreStatus, setRestoreStatus] = useState<"idle" | "restoring" | "success" | "error">("idle")
  const [confirmRestore, setConfirmRestore] = useState(false)
  const [currentStep, setCurrentStep] = useState("")

  const queryClient = useQueryClient();


  const startRestore = useMutation({
    mutationFn: async (backupId: string) => {
      setIsRestoring(true);
      await apiPost(`/backups/${backupId}/restore`, {});
      return backupId;
    },
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["accounts"] });
      setRestoreStatus("restoring");
      setRestoreProgress(0);
      setCurrentStep("Starting restore...");
    },
    onError: (err) => {
      setRestoreStatus("error");
      setIsRestoring(false);

      if (err instanceof ApiError) {
        const errMessage = err?.data?.detail || err?.data?.message || err.message;
        console.error(`Restore Error: ${errMessage}`);
        toast.error(`Restore Error: ${errMessage}`);
      } else {
        console.error(`Unknown Error: ${err}`);
        toast.error(`Unknown Error: ${err}`);
      }
    },
    onSuccess: () => {
      onRestoreComplete();
      onOpenChange(false);
      setRestoreStatus("success");
      setRestoreProgress(100);
      setCurrentStep("Restore completed successfully.");
      toast.success("Restore completed successfully");
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      setIsRestoring(false);
      setConfirmRestore(false);
      setTimeout(() => {
        setRestoreStatus("idle");
        setRestoreProgress(0);
        setCurrentStep("");
      }, 1500);
    },
  });

  const handleStartRestore = () => {
    if (confirmRestore && backup) {
      setRestoreStatus("idle");
      startRestore.mutate(backup.id); // assumes you have a `backup` object with an `id`
    }
  };

  const handleCancel = () => {
    if (!isRestoring) {
      onOpenChange(false)
      setConfirmRestore(false)
      setRestoreStatus("idle")
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleCancel}>
      <DialogContent className="bg-card border-border max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-foreground flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Restore Profile Backup
          </DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Restore Gmail profile for {accountEmail} from backup
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Warning Alert */}
          <div className="p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
            <div className="flex gap-3">
              <AlertTriangle className="h-5 w-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <div className="space-y-2">
                <p className="text-sm font-medium text-yellow-400">Warning: This action will overwrite current data</p>
                <p className="text-xs text-muted-foreground">
                  Restoring this backup will replace all current account settings, filters, and configurations with the
                  data from the selected backup. This action cannot be undone.
                </p>
              </div>
            </div>
          </div>

          {/* Backup Info */}
          <div className="p-3 bg-accent/30 rounded-lg border border-border space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Backup Date:</span>
              <span className="text-foreground font-medium">{new Date(backup?.created_at ?? 0).toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Backup Size:</span>
              <span className="text-foreground font-medium">{formatBytes(backup?.file_size)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Backup ID:</span>
              <span className="text-foreground font-mono text-xs">{backup?.id}</span>
            </div>
          </div>

          {/* Restore Progress */}
          {restoreStatus === "restoring" && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                <p className="text-sm text-foreground">{currentStep}</p>
              </div>
              <Progress value={restoreProgress} className="h-2" />
              <p className="text-xs text-muted-foreground">{restoreProgress}% complete</p>
            </div>
          )}

          {/* Success Message */}
          {restoreStatus === "success" && (
            <div className="p-3 bg-green-500/10 rounded-lg border border-green-500/20">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-400" />
                <p className="text-sm font-medium text-green-400">Restore completed successfully!</p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {restoreStatus === "error" && (
            <div className="p-3 bg-red-500/10 rounded-lg border border-red-500/20">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-red-400" />
                <p className="text-sm font-medium text-red-400">Restore failed. Please try again.</p>
              </div>
            </div>
          )}

          {/* What will be restored */}
          {restoreStatus === "idle" && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-foreground">What will be restored:</p>
              <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                <li>• Account credentials (encrypted)</li>
                <li>• Email filters and labels</li>
                <li>• Automation history and logs</li>
                <li>• Configuration settings</li>
                <li>• Custom templates</li>
              </ul>
            </div>
          )}

          {/* Confirmation Checkbox */}
          {restoreStatus === "idle" && (
            <div className="flex items-start gap-3 p-3 bg-accent/20 rounded-lg border border-border">
              <Checkbox
                id="confirm-restore"
                checked={confirmRestore}
                onCheckedChange={(checked) => setConfirmRestore(checked as boolean)}
                className="mt-0.5"
              />
              <label htmlFor="confirm-restore" className="text-sm text-foreground cursor-pointer leading-tight">
                I understand that this will overwrite all current account data and this action cannot be undone.
              </label>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={handleCancel} disabled={isRestoring}>
            Cancel
          </Button>
          <Button
            onClick={handleStartRestore}
            disabled={!confirmRestore || isRestoring || restoreStatus === "success"}
            className="bg-primary text-primary-foreground hover:bg-primary/90"
          >
            {isRestoring ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Restoring...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Restore Backup
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
