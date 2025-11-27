"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSub, DropdownMenuSubContent, DropdownMenuSubTrigger, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Plus, Upload, MoreHorizontal, History, Edit, Trash2, CircleSlashIcon, CheckCircle, Trash, Database, RotateCcw } from "lucide-react"
import { AccountDrawer } from "./account-drawer"
import { BulkUploader } from "./bulk-uploader"
import { AccountHistoryModal } from "./account-history-modal"
import { apiDelete, apiGet } from "@/lib/api"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Account, HistoryEntry } from "@/lib/types"
import { BackupModal } from "./backup-modal"
import { RestoreModal } from "./restore-modal"
import { formatBytes } from "@/utils/formatters"
import { useAccounts } from "@/hooks/useAccounts"

export function AccountList() {
  const [showAddAccount, setShowAddAccount] = useState(false)
  const [showBulkUpload, setShowBulkUpload] = useState(false)
  const [showHistory, setShowHistory] = useState<string | null>(null)
  const [editingAccount, setEditingAccount] = useState<Account | null>(null)
  const [currentHistory, setCurrentHistory] = useState<HistoryEntry[]>([])
  const { selectedAccounts, setSelectedAccounts } = useAccounts();
  const [backupAccount, setBackupAccount] = useState<Account | null>(null)
  const [restoreAccount, setRestoreAccount] = useState<Account | null>(null)

  const queryClient = useQueryClient()

  const { data: accounts } = useQuery<Account[]>({
    queryKey: ["accounts"],
    queryFn: async () => {
      const data = await apiGet<Account[]>("/accounts");
      return data;
    }
  })

  const handleAccountUpdated = () => {
    queryClient.invalidateQueries({ queryKey: ["accounts"] })
  }

  const getStatusColor = (status: Account["status"]) => {
    switch (status) {
      case "running":
        return "bg-green-500/10 text-green-400 border-green-500/20"
      case "error":
        return "bg-red-500/10 text-red-400 border-red-500/20"
      case "disabled":
        return "bg-gray-600/10 text-gray-400 border-gray-500/20"
      case "idle":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
      case "new":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20"
      default:
        return "bg-slate-500/10 text-slate-400 border-slate-500/20"
    }
  }

  const handleSelectAccount = (account: Account, checked: boolean) => {
    if (checked) {
      setSelectedAccounts([...selectedAccounts, account])
    } else {
      setSelectedAccounts(selectedAccounts.filter((acc) => acc.id !== account.id))
    }
  }

  const handleEditAccount = (account: Account) => {
    setEditingAccount(account)
    setShowAddAccount(true)
  }

  const handleShowhistory = (account: Account) => {
    setShowHistory(account.email)
    setCurrentHistory(account.activities.reverse())
  }

  const deleteAccount = useMutation({
    mutationFn: async (accountId: string) => {
      await apiDelete(`/accounts/${accountId}`)
      return accountId
    },

    onMutate: async (accountId: string) => {
      // Cancel any outgoing refetches (so they don't overwrite our optimistic update)
      await queryClient.cancelQueries({ queryKey: ["accounts"] })

      // Snapshot the previous value
      const previousAccounts = queryClient.getQueryData(["accounts"])

      // Optimistically update to the new value
      queryClient.setQueryData(["accounts"], (old: Account[]) =>
        old ? old.filter(acc => acc.id !== accountId) : []
      )

      return { previousAccounts }
    },
    onError: (err, accountId, context) => {
      queryClient.setQueryData(["accounts"], context?.previousAccounts)
    }
  })

  const handleDeleteAccount = (accountId: string) => {
    deleteAccount.mutate(accountId)
  }

  const bulkDeleteAccounts = useMutation({
    mutationFn: async (accountIds: string[]) => {
      await apiDelete('/accounts/bulk', accountIds)
      return accountIds
    },
    onMutate: async (accountIds: string[]) => {
      await queryClient.cancelQueries({ queryKey: ["accounts"] })
      const previousAccounts = queryClient.getQueryData(["accounts"])
      queryClient.setQueryData(["accounts"], (old: Account[]) =>
        old ? old.filter(acc => !accountIds.includes(acc.id)) : []
      )
      return { previousAccounts }
    },
    onError: (err, accountIds, context) => {
      queryClient.setQueryData(["accounts"], context?.previousAccounts)
    },
    onSuccess: () => {
      setSelectedAccounts([])
    }
  })


  const handleBulkDelete = () => {
    if (selectedAccounts.length > 0) {
      const selectedAccountIds = selectedAccounts.map(acc => acc.id);
      bulkDeleteAccounts.mutate(selectedAccountIds);
    }
  }

  const handleBackupComplete = () => {
    if (backupAccount) {
      queryClient.setQueryData(["accounts"], (old: Account[]) =>
        old.map((account) =>
          account.id === backupAccount.id
            ? {
              ...account,
              hasBackup: true,
              lastBackupDate: "Just now",
              backupSize: "2.1 MB",
            }
            : account,
        ),
      )
    }
  }

  const handleRestoreComplete = () => {
    if (restoreAccount) {
      console.log("[v0] Restore completed for account:", restoreAccount.email)
      // Optionally refresh account data here
    }
  }

  const handleToggleStatus = (accountId: string) => {
    console.log("Toggle status for account:", accountId)
    // setAccounts(
    //   accounts.map((account) =>
    //     account.id === accountId
    //       ? { ...account, status: account.status === "disabled" ? "idle" : "disabled" }
    //       : account,
    //   ),
    // )
  }

  return (
    <>
      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-foreground">Accounts</CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="icon"
                disabled={selectedAccounts.length === 0}
                onClick={handleBulkDelete}
                className="border-border hover:bg-accent text-destructive hover:text-destructive h-8 w-8"
              >
                <Trash className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowBulkUpload(true)}
                className="border-border hover:bg-accent"
              >
                <Upload className="h-4 w-4 mr-2" />
                Bulk Upload
              </Button>
              <Button
                size="sm"
                onClick={() => setShowAddAccount(true)}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Account
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {accounts?.map((account) => {
              const lastBackup = account.backups[account.backups.length - 1];
              const hasBackup = lastBackup && lastBackup.filename;

              return (
                <div
                  key={account.id}
                  className="flex items-center gap-3 p-3 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                >
                  <Checkbox
                    checked={selectedAccounts.includes(account)}
                    onCheckedChange={(checked) => handleSelectAccount(account, !!checked)}
                  />

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium text-foreground truncate">{account.email}</p>
                      <Badge variant="secondary" className="text-xs">
                        {account.label}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>Last: {new Date(account.activities[account.activities.length - 1].executed_at).toLocaleString() ?? "Nan"}</span>
                      <Badge className={getStatusColor(account.status)}>{account.status}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1 truncate">{account.latestAutomation}</p>
                    <div className="flex flex-wrap items-center mt-2 gap-2 text-xs">
                      <Database
                        className={`h-3 w-3 ${hasBackup ? "text-green-400" : "text-muted-foreground"}`}
                      />
                      <span className={`text-xs ${hasBackup ? "text-green-400" : "text-muted-foreground"}`}>
                        {hasBackup ? (
                          <>
                            Backup: {lastBackup.filename}{" "}
                            <span className="text-muted-foreground">
                              ({formatBytes(lastBackup.file_size)})
                            </span>
                          </>
                        ) : (
                          "No backup"
                        )}
                      </span>
                    </div>
                  </div>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="bg-popover border-border">
                      <DropdownMenuItem onClick={() => handleShowhistory(account)}>
                        <History className="h-4 w-4 mr-2" />
                        View History
                      </DropdownMenuItem>
                      <DropdownMenuSub>
                        <DropdownMenuSubTrigger>
                          <Database className="h-4 w-4 mr-4 text-muted-foreground" />
                          Backup & Restore
                        </DropdownMenuSubTrigger>
                        <DropdownMenuSubContent className="bg-popover border-border">
                          <DropdownMenuItem onClick={() => setBackupAccount(account)}>
                            <Database className="h-4 w-4 mr-2" />
                            {account.backups.length > 0 ? "Update Backup" : "Create Backup"}
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => setRestoreAccount(account)} disabled={!account.backups[account.backups.length - 1]?.filename}>
                            <RotateCcw className="h-4 w-4 mr-2" />
                            Restore Backup
                          </DropdownMenuItem>
                        </DropdownMenuSubContent>
                      </DropdownMenuSub>
                      <DropdownMenuItem onClick={() => handleEditAccount(account)}>
                        <Edit className="h-4 w-4 mr-2" />
                        Edit Account
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleToggleStatus(account.id)}>
                        {account.status === "disabled" ? <CheckCircle className="h-4 w-4 mr-2" /> : <CircleSlashIcon className="h-4 w-4 mr-2" />}
                        {account.status === "disabled" ? "Enable" : "Disable"}
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => handleDeleteAccount(account?.id)}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="h-4 w-4 mr-2 text-destructive" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              )
            })}
          </div>

          {selectedAccounts.length > 0 && (
            <div className="mt-4 p-3 bg-accent/30 rounded-lg border border-border">
              <p className="text-sm text-foreground">
                {selectedAccounts.length} account{selectedAccounts.length > 1 ? "s" : ""} selected
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <AccountDrawer
        open={showAddAccount}
        onOpenChange={(open) => {
          setShowAddAccount(open)
          if (!open) setEditingAccount(null)
        }}
        editingAccount={editingAccount}
        onAccountSaved={handleAccountUpdated}
      />

      <BulkUploader open={showBulkUpload} onOpenChange={setShowBulkUpload} onAccountSaved={handleAccountUpdated} />

      <AccountHistoryModal
        open={!!showHistory}
        onOpenChange={(open) => !open && setShowHistory(null)}
        accountEmail={showHistory || ""}
        history={currentHistory}
      />

      <BackupModal
        open={!!backupAccount}
        onOpenChange={(open) => !open && setBackupAccount(null)}
        account={backupAccount}
        onBackupComplete={handleBackupComplete}
      />

      <RestoreModal
        open={!!restoreAccount}
        onOpenChange={(open) => !open && setRestoreAccount(null)}
        accountEmail={restoreAccount?.email || ""}
        backup={restoreAccount?.backups[restoreAccount.backups.length - 1]}
        onRestoreComplete={handleRestoreComplete}
      />
    </>
  )
}
