import { AccountContext } from "@/providers/account-provider"
import { useContext } from "react"

export function useAccounts() {
  const ctx = useContext(AccountContext)
  if (!ctx) throw new Error("useAccounts must be used within an AccountProvider")
  return ctx
}
