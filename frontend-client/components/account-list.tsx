"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSub, DropdownMenuSubContent, DropdownMenuSubTrigger, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Plus, Upload, MoreHorizontal, History, Edit, Trash2, CircleSlashIcon, CheckCircle, Trash, Database, RotateCcw, Smartphone, Monitor, ShieldCheck, ShieldAlert, ChevronLeft, ChevronRight, Check, Square, Filter } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
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
  const {
    selectedAccounts,
    selectedAccountsMap,
    setSelectedAccounts,
    setSelectedAccountsMap,
    selectAllAccounts,
    clearSelection,
    selectAccount,
    deselectAccount,
    isAccountSelected,
    getSelectedCount,
    setTotalCount,
    statusFilter,
    setStatusFilter
  } = useAccounts();
  const [backupAccount, setBackupAccount] = useState<Account | null>(null)
  const [restoreAccount, setRestoreAccount] = useState<Account | null>(null)
  const { selectedProvider } = useProvider()
  const { getAccountJob, isAccountBusy, onJobComplete, stopJob, stopAllJobs, jobs } = useJobs()

  // Check if any jobs are running or queued
  const hasActiveJobs = jobs.running.length > 0 || jobs.queued.length > 0

  // Pagination State
  const [page, setPage] = useState(1)
  const pageSize = 10 // Assuming default page size

  const queryClient = useQueryClient()

  // Refetch accounts when a job completes (to get updated activities)
  useEffect(() => {
    let timeoutId: NodeJS.Timeout
    const unsubscribe = onJobComplete(() => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["accounts"] })
      }, 2000) // Debounce for 2 seconds to batch rapid updates
    })
    return () => {
      unsubscribe()
      clearTimeout(timeoutId)
    }
  }, [onJobComplete, queryClient])

  useEffect(() => {
    clearSelection()
    setPage(1)
  }, [selectedProvider, clearSelection])

  const { data: paginatedData, isLoading } = useQuery<PaginatedResponse<Account>>({
    queryKey: ["accounts", page, selectedProvider?.slug, statusFilter],
    queryFn: async () => {
      if (!selectedProvider) return { count: 0, next: null, previous: null, results: [] };
      let url = `/api/accounts?page=${page}&provider=${selectedProvider.slug}`;
      if (statusFilter && statusFilter !== "all") {
        url += `&status=${statusFilter}`;
      }
      return await apiGet<PaginatedResponse<Account>>(url);
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
      case "suspended":
        return "bg-red-600/10 text-red-500 border-red-600/20"
      case "phone_verification":
        return "bg-orange-500/10 text-orange-400 border-orange-500/20"
      case "captcha":
        return "bg-purple-500/10 text-purple-400 border-purple-500/20"
      case "wrong_password":
        return "bg-pink-500/10 text-pink-400 border-pink-500/20"
      case "wrong_username":
        return "bg-pink-600/10 text-pink-500 border-pink-600/20"
      default:
        return "bg-slate-500/10 text-slate-400 border-slate-500/20"
    }
  }

  const handleSelectAccount = (account: Account, checked: boolean) => {
    if (checked) {
      selectAccount(account)
    } else {
      deselectAccount(account.id)
    }
  }

  // Check if all accounts on current page are selected
  const isCurrentPageFullySelected = accounts.length > 0 && accounts.every(acc => isAccountSelected(acc.id))

  // Check if all accounts globally are selected
  const isAllSelectedGlobal = totalCount > 0 && selectedAccounts.length === totalCount

  // Check if we should show the "select all" banner
  const showSelectAllBanner = isCurrentPageFullySelected && !isAllSelectedGlobal && totalCount > accounts.length

  const handleSelectAllGlobal = async () => {
    if (!selectedProvider) return;
    try {
      let url = `/api/accounts?provider=${selectedProvider.slug}&page_size=10000`;
      if (statusFilter && statusFilter !== "all") {
        url += `&status=${statusFilter}`;
      }
      const res = await apiGet<PaginatedResponse<Account>>(url);
      selectAllAccounts(res.results);
      toast.success(`Selected all ${res.count} accounts`);
    } catch (err) {
      toast.error("Failed to select all accounts");
    }
  };

  const handleEditAccount = (account: Account) => {
    setEditingAccount(account)
    setShowAddAccount(true)
  }

  const handleShowhistory = (account: Account) => {
    setShowHistory(account.email)
    setCurrentHistory([...(account.activities || [])].reverse())
  }

  const deleteAccount = useMutation({
    mutationFn: async (accountId: number | string) => {
      await apiDelete(`/api/accounts/${accountId}/`)
      return accountId
    },

    onMutate: async (accountId: number | string) => {
      await queryClient.cancelQueries({ queryKey: ["accounts"] })
      const previousData = queryClient.getQueryData(["accounts", page, selectedProvider?.slug])

      queryClient.setQueryData(["accounts", page, selectedProvider?.slug], (old: PaginatedResponse<Account> | undefined) => {
        if (!old) return old;
        return {
          ...old,
          results: old.results.filter(acc => String(acc.id) !== String(accountId))
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
    mutationFn: async (payload: { account_ids?: string[], select_all?: boolean, provider?: string, excluded_ids?: string[], status?: string }) => {
      await apiDelete('/api/accounts/bulk-delete/', payload)
      return payload
    },
    onMutate: async (payload) => {
      await queryClient.cancelQueries({ queryKey: ["accounts"] })
      const previousData = queryClient.getQueryData(["accounts", page, selectedProvider?.slug])

      queryClient.setQueryData(["accounts", page, selectedProvider?.slug], (old: PaginatedResponse<Account> | undefined) => {
        if (!old) return old;

        // Optimistic update logic
        let newResults = old.results;

        if (payload.select_all) {
          // If select all is used, we can't easily know which accounts to keep without refetching, 
          // but we can remove the ones we know are NOT excluded if they are in the current page.
          // However, for simplicity and correctness with select_all, it's safer to rely on invalidation.
          // We'll just try to remove non-excluded ones from current view if possible, 
          // but mostly we rely on the refetch.
          if (payload.excluded_ids && payload.excluded_ids.length > 0) {
            // If we have exclusions, we keep them.
            newResults = old.results.filter(acc => payload.excluded_ids?.includes(String(acc.id)));
          } else {
            // If select all and no exclusions, everything goes.
            newResults = [];
          }
        } else if (payload.account_ids) {
          newResults = old.results.filter(acc => !payload.account_ids?.includes(String(acc.id)))
        }

        return {
          ...old,
          results: newResults
        }
      })
      return { previousData }
    },
    onError: (err, payload, context) => {
      queryClient.setQueryData(["accounts", page, selectedProvider?.slug], context?.previousData)
      toast.error("Failed to delete accounts")
    },
    onSuccess: () => {
      setSelectedAccounts([])
      toast.success("Accounts deleted successfully")
      // Force a refetch to ensure everything is in sync, especially for select_all
      queryClient.invalidateQueries({ queryKey: ["accounts"] })
    }
  })


  const handleBulkDelete = () => {
    if (selectedAccounts.length > 0) {
      const selectedAccountIds = selectedAccounts.map(acc => String(acc.id));
      bulkDeleteAccounts.mutate({ account_ids: selectedAccountIds });
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
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-foreground flex items-center gap-3">
              <Checkbox
                checked={isCurrentPageFullySelected}
                onCheckedChange={(checked) => {
                  if (checked) {
                    // Add all accounts on current page
                    accounts.forEach(acc => selectAccount(acc))
                  } else {
                    // Remove all accounts on current page
                    accounts.forEach(acc => deselectAccount(acc.id))
                  }
                }}
              />
              Accounts
              {getSelectedCount() > 0 && (
                <span className="text-sm font-normal text-muted-foreground">
                  ({getSelectedCount()}{isAllSelectedGlobal ? ` of ${totalCount}` : ''} selected)
                </span>
              )}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Select value={statusFilter || "all"} onValueChange={(val) => setStatusFilter(val === "all" ? null : val)}>
                <SelectTrigger className="w-[150px] h-8 text-xs border-border bg-card">
                  <div className="flex items-center gap-2">
                    <Filter className="h-3.5 w-3.5 text-muted-foreground" />
                    <SelectValue placeholder="Filter Status" />
                  </div>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                  <SelectItem value="disabled">Disabled</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                  <SelectItem value="suspended">Suspended</SelectItem>
                  <SelectItem value="phone_verification">Phone Verification</SelectItem>
                  <SelectItem value="captcha">Captcha</SelectItem>
                  <SelectItem value="wrong_password">Wrong Password</SelectItem>
                  <SelectItem value="wrong_username">Wrong Username</SelectItem>
                </SelectContent>
              </Select>
              {/* Stop All Button */}
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="outline"
                      size="icon"
                      disabled={!hasActiveJobs}
                      onClick={() => stopAllJobs()}
                      className="border-border hover:bg-red-500/10 text-red-400 hover:text-red-300 h-8 w-8"
                    >
                      <Square className="h-4 w-4 fill-current" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Stop all jobs ({jobs.running.length + jobs.queued.length})</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
              <Button
                variant="outline"
                size="icon"
                disabled={getSelectedCount() === 0}
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


          {/* Select All Banner */}
          {showSelectAllBanner && (
            <div className="mt-3 p-3 bg-primary/10 border border-primary/20 rounded-lg flex items-center justify-between animate-in fade-in slide-in-from-top-1 duration-200">
              <span className="text-sm text-foreground">
                All {accounts.length} accounts on this page are selected.
              </span>
              <Button
                variant="link"
                size="sm"
                className="text-primary h-auto p-0 font-semibold"
                onClick={handleSelectAllGlobal}
              >
                Select all {totalCount} accounts
              </Button>
            </div>
          )}

          {/* Select All Active Banner */}
          {isAllSelectedGlobal && (
            <div className="mt-3 p-3 bg-green-500/10 border border-green-500/20 rounded-lg flex items-center justify-between animate-in fade-in slide-in-from-top-1 duration-200">
              <span className="text-sm text-foreground">
                All {getSelectedCount()} accounts are selected.
              </span>
              <Button
                variant="link"
                size="sm"
                className="text-muted-foreground h-auto p-0"
                onClick={clearSelection}
              >
                Clear selection
              </Button>
            </div>
          )}
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
                      checked={isAccountSelected(String(account.id))}
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
                        <Badge className={getStatusColor(account.status)}>{account.status.replace('_', ' ')}</Badge>
                        {/* Job Status Indicator */}
                        {(() => {
                          const job = getAccountJob(String(account.id));
                          if (job?.status === "running") {
                            return (
                              <div className="flex items-center gap-1">
                                <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 flex items-center gap-1">
                                  <Loader2 className="h-3 w-3 animate-spin" />
                                  Running
                                </Badge>
                                <TooltipProvider>
                                  <Tooltip>
                                    <TooltipTrigger asChild>
                                      <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-6 w-6 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                                        onClick={() => stopJob(job.id)}
                                      >
                                        <Square className="h-3 w-3 fill-current" />
                                      </Button>
                                    </TooltipTrigger>
                                    <TooltipContent>
                                      <p>Stop job</p>
                                    </TooltipContent>
                                  </Tooltip>
                                </TooltipProvider>
                              </div>
                            );
                          }
                          if (job?.status === "queued") {
                            return (
                              <div className="flex items-center gap-1">
                                <Badge className="bg-orange-500/10 text-orange-400 border-orange-500/20 flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  Queued
                                </Badge>
                                <TooltipProvider>
                                  <Tooltip>
                                    <TooltipTrigger asChild>
                                      <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-6 w-6 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                                        onClick={() => stopJob(job.id)}
                                      >
                                        <Square className="h-3 w-3 fill-current" />
                                      </Button>
                                    </TooltipTrigger>
                                    <TooltipContent>
                                      <p>Cancel job</p>
                                    </TooltipContent>
                                  </Tooltip>
                                </TooltipProvider>
                              </div>
                            );
                          }
                          // return (
                          //   <Badge className="bg-green-500/10 text-green-400 border-green-500/20 flex items-center gap-1">
                          //     <Check className="h-3 w-3" />
                          //     Idle
                          //   </Badge>
                          // );
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
                        <DropdownMenuSub>
                          <DropdownMenuSubTrigger>
                            <Database className="h-4 w-4 mr-2 text-muted-foreground" />
                            Backup & Restore
                          </DropdownMenuSubTrigger>
                          <DropdownMenuSubContent className="bg-popover border-border">
                            {account.backups && account.backups.length > 0 ? (
                              account.backups.map((backup) => (
                                <DropdownMenuItem key={backup.id} onClick={() => setRestoreAccount(account)}>
                                  Restore {formatBytes(backup.file_size || 0)}
                                </DropdownMenuItem>
                              ))
                            ) : (
                              <DropdownMenuItem disabled>No backups</DropdownMenuItem>
                            )}
                            <DropdownMenuItem onClick={() => setBackupAccount(account)}>
                              Create New Backup
                            </DropdownMenuItem>
                          </DropdownMenuSubContent>
                        </DropdownMenuSub>
                        <DropdownMenuItem onClick={() => handleEditAccount(account)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit Account
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleDeleteAccount(String(account.id))}
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
      </Card >

      <AccountDrawer
        open={showAddAccount}
        onOpenChange={(open) => {
          setShowAddAccount(open)
          if (!open) setEditingAccount(null)
        }}
        editingAccount={editingAccount}
        onAccountSaved={handleAccountUpdated}
      />

      <BulkUploader open={showBulkUpload} onOpenChange={setShowBulkUpload} onUploadSuccess={handleAccountUpdated} mode="accounts" />

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
        backup={restoreAccount?.backups ? restoreAccount.backups[restoreAccount.backups.length - 1] : undefined}
        onRestoreComplete={handleRestoreComplete}
      />
    </>
  )
}
