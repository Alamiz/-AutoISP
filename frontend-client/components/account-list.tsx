"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSub, DropdownMenuSubContent, DropdownMenuSubTrigger, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Plus, Upload, MoreHorizontal, History, Edit, Trash2, CircleSlashIcon, CheckCircle, Trash, Database, RotateCcw, Smartphone, Monitor, ShieldCheck, ShieldAlert, ChevronLeft, ChevronRight, Check } from "lucide-react"
import { AccountDrawer } from "./account-drawer"
import { BulkUploader } from "./bulk-uploader"
import { AccountHistoryModal } from "./account-history-modal"
import { apiDelete, apiGet, apiPatch } from "@/lib/api"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Account, HistoryEntry, PaginatedResponse } from "@/lib/types"
import { BackupModal } from "./backup-modal"
import { RestoreModal } from "./restore-modal"
import { formatBytes } from "@/utils/formatters"
import { useAccounts } from "@/hooks/useAccounts"
import { useProvider } from "@/contexts/provider-context"
import { toast } from "sonner"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useJobs } from "@/contexts/jobs-context"
import { Loader2, Clock } from "lucide-react"
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
export function AccountList() {
  const [showAddAccount, setShowAddAccount] = useState(false)
  const [showBulkUpload, setShowBulkUpload] = useState(false)
  const [showHistory, setShowHistory] = useState<string | null>(null)
  const [editingAccount, setEditingAccount] = useState<Account | null>(null)
  const [currentHistory, setCurrentHistory] = useState<HistoryEntry[]>([])
  const { selectedAccounts, setSelectedAccounts } = useAccounts();
  const [backupAccount, setBackupAccount] = useState<Account | null>(null)
  const [restoreAccount, setRestoreAccount] = useState<Account | null>(null)
  const { selectedProvider } = useProvider()
  const { getAccountJob, isAccountBusy, onJobComplete } = useJobs()

  // Pagination State
  const [page, setPage] = useState(1)
  const pageSize = 10 // Assuming default page size

  const queryClient = useQueryClient()

  // Refetch accounts when a job completes (to get updated activities)
  useEffect(() => {
    const unsubscribe = onJobComplete(() => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] })
    })
    return unsubscribe
  }, [onJobComplete, queryClient])

  useEffect(() => {
    setSelectedAccounts([])
  }, [selectedProvider])

  const { data: paginatedData, isLoading } = useQuery<PaginatedResponse<Account>>({
    queryKey: ["accounts", page, selectedProvider?.slug],
    queryFn: async () => {
      if (!selectedProvider) return { count: 0, next: null, previous: null, results: [] };
      return await apiGet<PaginatedResponse<Account>>(`/api/accounts?page=${page}&provider=${selectedProvider.slug}`);
    },
    enabled: !!selectedProvider,
    placeholderData: (previousData) => previousData, // Keep previous data while fetching new page
  })

  const accounts = paginatedData?.results || []
  const totalCount = paginatedData?.count || 0
  const totalPages = Math.ceil(totalCount / pageSize)

  const handleAccountUpdated = () => {
    queryClient.invalidateQueries({ queryKey: ["accounts"] })
  }

  const getStatusColor = (status: Account["status"]) => {
    switch (status) {
      case "active":
        return "bg-green-500/10 text-green-400 border-green-500/20"
      case "inactive":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
      case "disabled":
        return "bg-gray-600/10 text-gray-400 border-gray-500/20"
      case "error":
        return "bg-red-500/10 text-red-400 border-red-500/20"
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
      await apiDelete(`/api/accounts/${accountId}/`)
      return accountId
    },

    onMutate: async (accountId: string) => {
      await queryClient.cancelQueries({ queryKey: ["accounts"] })
      const previousData = queryClient.getQueryData(["accounts", page, selectedProvider?.slug])

      queryClient.setQueryData(["accounts", page, selectedProvider?.slug], (old: PaginatedResponse<Account> | undefined) => {
        if (!old) return old;
        return {
          ...old,
          results: old.results.filter(acc => acc.id !== accountId)
        }
      })

      return { previousData }
    },
    onError: (err, accountId, context) => {
      queryClient.setQueryData(["accounts", page, selectedProvider?.slug], context?.previousData)
    }
  })

  const handleDeleteAccount = (accountId: string) => {
    deleteAccount.mutate(accountId)
  }

  const bulkDeleteAccounts = useMutation({
    mutationFn: async (accountIds: string[]) => {
      await apiDelete('/api/accounts/bulk-delete/', accountIds)
      return accountIds
    },
    onMutate: async (accountIds: string[]) => {
      await queryClient.cancelQueries({ queryKey: ["accounts"] })
      const previousData = queryClient.getQueryData(["accounts", page, selectedProvider?.slug])

      queryClient.setQueryData(["accounts", page, selectedProvider?.slug], (old: PaginatedResponse<Account> | undefined) => {
        if (!old) return old;
        return {
          ...old,
          results: old.results.filter(acc => !accountIds.includes(acc.id))
        }
      })
      return { previousData }
    },
    onError: (err, accountIds, context) => {
      queryClient.setQueryData(["accounts", page, selectedProvider?.slug], context?.previousData)
      toast.error("Failed to delete accounts")
    },
    onSuccess: () => {
      setSelectedAccounts([])
      toast.success("Accounts deleted successfully")
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
      // Invalidate to refresh backup status
      queryClient.invalidateQueries({ queryKey: ["accounts"] })
    }
  }

  const handleRestoreComplete = () => {
    if (restoreAccount) {
      console.log("[v0] Restore completed for account:", restoreAccount.email)
      queryClient.invalidateQueries({ queryKey: ["accounts"] })
    }
  }

  const toggleDeviceType = useMutation({
    mutationFn: async (account: Account) => {
      const newType = account.type === "mobile" ? "desktop" : "mobile"
      await apiPatch(`/api/accounts/${account.id}/`, { type: newType })
      return { accountId: account.id, newType }
    },
    onMutate: async (account) => {
      await queryClient.cancelQueries({ queryKey: ["accounts"] })
      const previousData = queryClient.getQueryData(["accounts", page, selectedProvider?.slug])

      const newType = account.type === "mobile" ? "desktop" : "mobile"

      queryClient.setQueryData(["accounts", page, selectedProvider?.slug], (old: PaginatedResponse<Account> | undefined) => {
        if (!old) return old;
        return {
          ...old,
          results: old.results.map(acc => acc.id === account.id ? { ...acc, type: newType } : acc)
        }
      })

      return { previousData }
    },
    onError: (err, account, context) => {
      queryClient.setQueryData(["accounts", page, selectedProvider?.slug], context?.previousData)
      toast.error("Failed to update device type")
    },
    onSuccess: (data) => {
      toast.success(`Device type updated to ${data.newType}`)
    }
  })

  // Helper to generate pagination items
  const renderPaginationItems = () => {
    const items = []
    const maxVisiblePages = 5

    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink
              href="#"
              isActive={page === i}
              onClick={(e) => {
                e.preventDefault()
                setPage(i)
              }}
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        )
      }
    } else {
      // Logic for ellipsis
      let startPage = Math.max(1, page - 2)
      let endPage = Math.min(totalPages, page + 2)

      if (page <= 3) {
        endPage = 5
      } else if (page >= totalPages - 2) {
        startPage = totalPages - 4
      }

      if (startPage > 1) {
        items.push(
          <PaginationItem key={1}>
            <PaginationLink
              href="#"
              onClick={(e) => {
                e.preventDefault()
                setPage(1)
              }}
            >
              1
            </PaginationLink>
          </PaginationItem>
        )
        if (startPage > 2) {
          items.push(
            <PaginationItem key="ellipsis-start">
              <PaginationEllipsis />
            </PaginationItem>
          )
        }
      }

      for (let i = startPage; i <= endPage; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink
              href="#"
              isActive={page === i}
              onClick={(e) => {
                e.preventDefault()
                setPage(i)
              }}
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        )
      }

      if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
          items.push(
            <PaginationItem key="ellipsis-end">
              <PaginationEllipsis />
            </PaginationItem>
          )
        }
        items.push(
          <PaginationItem key={totalPages}>
            <PaginationLink
              href="#"
              onClick={(e) => {
                e.preventDefault()
                setPage(totalPages)
              }}
            >
              {totalPages}
            </PaginationLink>
          </PaginationItem>
        )
      }
    }

    return items
  }

  return (
    <>
      <Card className="bg-card border-border flex flex-col h-full min-h-0">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-foreground flex items-center gap-3">
              <Checkbox
                checked={accounts.length > 0 && accounts.every(acc => selectedAccounts.some(s => s.id === acc.id))}
                onCheckedChange={(checked) => {
                  if (checked) {
                    // Add all accounts on current page that aren't already selected
                    const newSelections = accounts.filter(acc => !selectedAccounts.some(s => s.id === acc.id));
                    setSelectedAccounts([...selectedAccounts, ...newSelections]);
                  } else {
                    // Remove all accounts on current page from selection
                    setSelectedAccounts(selectedAccounts.filter(s => !accounts.some(acc => acc.id === s.id)));
                  }
                }}
              />
              Accounts
              {selectedAccounts.length > 0 && (
                <span className="text-sm font-normal text-muted-foreground">
                  ({selectedAccounts.length} selected)
                </span>
              )}
            </CardTitle>
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
        <CardContent className="flex-1 overflow-hidden p-0">
          <div className="h-full overflow-y-auto p-6 space-y-3">
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading accounts...</div>
            ) : accounts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">No accounts found.</div>
            ) : (
              accounts.map((account) => {
                const hasProxy = account.proxy_settings && account.proxy_settings.host;
                const proxyText = hasProxy ? `${account.proxy_settings?.host}:${account.proxy_settings?.port}` : "No Proxy";

                return (
                  <div
                    key={account.id}
                    className="flex items-center gap-3 p-3 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                  >
                    <Checkbox
                      checked={selectedAccounts.some(acc => acc.id === account.id)}
                      onCheckedChange={(checked) => handleSelectAccount(account, !!checked)}
                    />

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium text-foreground truncate">{account.email}</p>
                        {account.label && <Badge variant="secondary" className="text-xs">
                          {account.label}
                        </Badge>}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        {/* <Badge className={getStatusColor(account.status)}>{account.status}</Badge> */}
                        {/* Job Status Indicator */}
                        {(() => {
                          const job = getAccountJob(account.id);
                          if (job?.status === "running") {
                            return (
                              <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 flex items-center gap-1">
                                <Loader2 className="h-3 w-3 animate-spin" />
                                Running
                              </Badge>
                            );
                          }
                          if (job?.status === "queued") {
                            return (
                              <Badge className="bg-orange-500/10 text-orange-400 border-orange-500/20 flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                Queued
                              </Badge>
                            );
                          }
                          return (
                            <Badge className="bg-green-500/10 text-green-400 border-green-500/20 flex items-center gap-1">
                              <Check className="h-3 w-3" />
                              Idle
                            </Badge>
                          );
                        })()}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1 truncate">{account.latest_automation}</p>
                      <div className="flex flex-wrap items-center mt-2 gap-2 text-xs">
                        {/* Device Switcher */}
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-6 w-6"
                                onClick={() => toggleDeviceType.mutate(account)}
                              >
                                {account.type === "mobile" ? (
                                  <Smartphone className="h-4 w-4 text-blue-400" />
                                ) : (
                                  <Monitor className="h-4 w-4 text-purple-400" />
                                )}
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Switch to {account.type === "mobile" ? "Desktop" : "Mobile"}</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>

                        {/* Proxy Status */}
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <div className="flex items-center">
                                {hasProxy ? (
                                  <ShieldCheck className="h-4 w-4 text-green-400" />
                                ) : (
                                  <ShieldAlert className="h-4 w-4 text-muted-foreground/50" />
                                )}
                              </div>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>{proxyText}</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
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
                        {/* <DropdownMenuSub>
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
                        </DropdownMenuSub> */}
                        <DropdownMenuItem onClick={() => handleEditAccount(account)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit Account
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
              })
            )}
          </div>
        </CardContent>

        {/* Pagination Footer */}
        <CardFooter className="border-t border-border p-4 flex items-center justify-between bg-card">
          <div className="text-sm text-muted-foreground">
            {totalCount > 0 ? (
              <>Total: {totalCount} accounts</>
            ) : (
              <>Page {page}</>
            )}
          </div>

          {totalPages > 1 && (
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    href="#"
                    onClick={(e) => {
                      e.preventDefault()
                      if (paginatedData?.previous) setPage(p => Math.max(1, p - 1))
                    }}
                    className={!paginatedData?.previous ? "pointer-events-none opacity-50" : ""}
                  />
                </PaginationItem>

                {renderPaginationItems()}

                <PaginationItem>
                  <PaginationNext
                    href="#"
                    onClick={(e) => {
                      e.preventDefault()
                      if (paginatedData?.next) setPage(p => p + 1)
                    }}
                    className={!paginatedData?.next ? "pointer-events-none opacity-50" : ""}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          )}
        </CardFooter>
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
