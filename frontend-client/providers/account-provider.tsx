"use client"

import { Account } from "@/lib/types"
import { createContext, useState } from "react"

type AccountContextType = {
  selectedAccounts: Account[]
  setSelectedAccounts: (accounts: Account[]) => void
}

export const AccountContext = createContext<AccountContextType | null>(null)

export function AccountProvider({ children }: { children: React.ReactNode }) {
  const [selectedAccounts, setSelectedAccounts] = useState<Account[]>([])
  return (
    <AccountContext.Provider value={{ selectedAccounts, setSelectedAccounts }}>
      {children}
    </AccountContext.Provider>
  )
}
