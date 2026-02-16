"use client"

import { Account } from "@/lib/types"
import { createContext, useState, useCallback, useMemo, useContext } from "react"

type AccountContextType = {
  // Selection state
  selectedAccounts: Account[]           // Accounts that are selected
  totalCount: number                     // Total count of accounts for current provider

  // Actions
  setSelectedAccounts: (accounts: Account[]) => void
  selectedAccountsMap: Record<string, boolean>
  setSelectedAccountsMap: (updater: Record<string, boolean> | ((prev: Record<string, boolean>) => Record<string, boolean>)) => void
  selectAccount: (account: Account) => void
  deselectAccount: (accountId: number | string) => void
  selectAllAccounts: (accounts: Account[]) => void
  clearSelection: () => void
  setTotalCount: (count: number) => void

  // Helpers
  isAccountSelected: (accountId: number | string) => boolean
  getSelectedCount: () => number

  // Filtering
  statusFilter: string | null
  setStatusFilter: (status: string | null) => void
}

export const AccountContext = createContext<AccountContextType | null>(null)

export function AccountProvider({ children }: { children: React.ReactNode }) {
  const [selectedAccounts, setSelectedAccountsInternal] = useState<Account[]>([])
  const [selectedAccountsMap, setSelectedAccountsMapInternal] = useState<Record<string, boolean>>({})
  const [totalCount, setTotalCount] = useState(0)
  const [statusFilter, setStatusFilter] = useState<string | null>(null)

  // Sync selectedAccounts list when map changes
  // This is a bit tricky, but since we usually have the full objects when we select, 
  // maybe we should update the map when the list changes instead.
  // Actually, TanStack table will give us a map of IDs.

  const setSelectedAccountsMap = useCallback((updaterOrValue: any) => {
    setSelectedAccountsMapInternal(prev => {
      const nextMap = typeof updaterOrValue === 'function' ? updaterOrValue(prev) : updaterOrValue
      return nextMap
    })
  }, [])

  // Legacy setter for backward compatibility
  const setSelectedAccounts = useCallback((accounts: Account[]) => {
    setSelectedAccountsInternal(accounts)
    const newMap: Record<string, boolean> = {}
    accounts.forEach(a => {
      newMap[String(a.id)] = true
    })
    setSelectedAccountsMapInternal(newMap)
  }, [])

  // Select a single account
  const selectAccount = useCallback((account: Account) => {
    const id = String(account.id)
    setSelectedAccountsInternal(prev => {
      if (prev.some(a => String(a.id) === id)) return prev
      return [...prev, account]
    })
    setSelectedAccountsMapInternal(prev => ({ ...prev, [id]: true }))
  }, [])

  // Deselect a single account
  const deselectAccount = useCallback((accountId: number | string) => {
    const id = String(accountId)
    setSelectedAccountsInternal(prev => prev.filter(a => String(a.id) !== id))
    setSelectedAccountsMapInternal(prev => {
      const next = { ...prev }
      delete next[id]
      return next
    })
  }, [])

  // Select all accounts
  const selectAllAccounts = useCallback((accounts: Account[]) => {
    setSelectedAccountsInternal(accounts)
    const newMap: Record<string, boolean> = {}
    accounts.forEach(a => {
      newMap[String(a.id)] = true
    })
    setSelectedAccountsMapInternal(newMap)
  }, [])

  // Clear all selection
  const clearSelection = useCallback(() => {
    setSelectedAccountsInternal([])
    setSelectedAccountsMapInternal({})
  }, [])

  // Check if an account is selected
  const isAccountSelected = useCallback((accountId: number | string) => {
    const id = String(accountId)
    return selectedAccounts.some(a => String(a.id) === id)
  }, [selectedAccounts])

  // Get the count of selected accounts
  const getSelectedCount = useCallback(() => {
    return selectedAccounts.length
  }, [selectedAccounts])

  const value = useMemo(() => ({
    selectedAccounts,
    selectedAccountsMap,
    totalCount,
    statusFilter,
    setSelectedAccounts,
    setSelectedAccountsMap,
    selectAccount,
    deselectAccount,
    selectAllAccounts,
    clearSelection,
    setTotalCount,
    setStatusFilter,
    isAccountSelected,
    getSelectedCount,
  }), [
    selectedAccounts,
    selectedAccountsMap,
    totalCount,
    statusFilter,
    setSelectedAccounts,
    setSelectedAccountsMap,
    selectAccount,
    deselectAccount,
    selectAllAccounts,
    clearSelection,
    setTotalCount,
    setStatusFilter,
    isAccountSelected,
    getSelectedCount,
  ])

  return (
    <AccountContext.Provider value={value}>
      {children}
    </AccountContext.Provider>
  )
} export function useAccounts() {
  const context = useContext(AccountContext)
  if (context === null) {
    throw new Error('useAccounts must be used within an AccountProvider')
  }
  return context
}
