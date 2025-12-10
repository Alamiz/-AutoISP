"use client"

import { Account } from "@/lib/types"
import { createContext, useState, useCallback, useMemo } from "react"

type AccountContextType = {
  // Selection state
  selectedAccounts: Account[]           // Accounts currently loaded that are selected (for backward compatibility)
  isAllSelected: boolean                 // True when "select all" mode is active
  excludedIds: Set<string>               // IDs to exclude when in select-all mode
  totalCount: number                     // Total count of accounts for current provider

  // Actions
  setSelectedAccounts: (accounts: Account[]) => void
  selectAccount: (account: Account) => void
  deselectAccount: (accountId: string) => void
  selectAllAccounts: (total: number) => void
  clearSelection: () => void
  setTotalCount: (count: number) => void

  // Helpers
  isAccountSelected: (accountId: string) => boolean
  getSelectedCount: () => number
}

export const AccountContext = createContext<AccountContextType | null>(null)

export function AccountProvider({ children }: { children: React.ReactNode }) {
  const [selectedAccounts, setSelectedAccountsInternal] = useState<Account[]>([])
  const [isAllSelected, setIsAllSelected] = useState(false)
  const [excludedIds, setExcludedIds] = useState<Set<string>>(new Set())
  const [totalCount, setTotalCount] = useState(0)

  // Legacy setter for backward compatibility
  const setSelectedAccounts = useCallback((accounts: Account[]) => {
    setSelectedAccountsInternal(accounts)
    // If manually setting accounts, exit select-all mode
    if (isAllSelected && accounts.length === 0) {
      setIsAllSelected(false)
      setExcludedIds(new Set())
    }
  }, [isAllSelected])

  // Select a single account
  const selectAccount = useCallback((account: Account) => {
    if (isAllSelected) {
      // In select-all mode, remove from excluded
      setExcludedIds(prev => {
        const next = new Set(prev)
        next.delete(account.id)
        return next
      })
    }
    // Also add to selectedAccounts for components that need the full objects
    setSelectedAccountsInternal(prev => {
      if (prev.some(a => a.id === account.id)) return prev
      return [...prev, account]
    })
  }, [isAllSelected])

  // Deselect a single account
  const deselectAccount = useCallback((accountId: string) => {
    if (isAllSelected) {
      // In select-all mode, add to excluded
      setExcludedIds(prev => new Set(prev).add(accountId))
    }
    // Also remove from selectedAccounts
    setSelectedAccountsInternal(prev => prev.filter(a => a.id !== accountId))
  }, [isAllSelected])

  // Select all accounts
  const selectAllAccounts = useCallback((total: number) => {
    setIsAllSelected(true)
    setExcludedIds(new Set())
    setTotalCount(total)
  }, [])

  // Clear all selection
  const clearSelection = useCallback(() => {
    setIsAllSelected(false)
    setExcludedIds(new Set())
    setSelectedAccountsInternal([])
  }, [])

  // Check if an account is selected
  const isAccountSelected = useCallback((accountId: string) => {
    if (isAllSelected) {
      return !excludedIds.has(accountId)
    }
    return selectedAccounts.some(a => a.id === accountId)
  }, [isAllSelected, excludedIds, selectedAccounts])

  // Get the count of selected accounts
  const getSelectedCount = useCallback(() => {
    if (isAllSelected) {
      return totalCount - excludedIds.size
    }
    return selectedAccounts.length
  }, [isAllSelected, totalCount, excludedIds, selectedAccounts])

  const value = useMemo(() => ({
    selectedAccounts,
    isAllSelected,
    excludedIds,
    totalCount,
    setSelectedAccounts,
    selectAccount,
    deselectAccount,
    selectAllAccounts,
    clearSelection,
    setTotalCount,
    isAccountSelected,
    getSelectedCount,
  }), [
    selectedAccounts,
    isAllSelected,
    excludedIds,
    totalCount,
    setSelectedAccounts,
    selectAccount,
    deselectAccount,
    selectAllAccounts,
    clearSelection,
    isAccountSelected,
    getSelectedCount,
  ])

  return (
    <AccountContext.Provider value={value}>
      {children}
    </AccountContext.Provider>
  )
}
