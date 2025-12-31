"use client"

import { providers } from "@/data/providers"
import * as React from "react"

export interface Provider {
    name: string
    slug: string
    logo: React.ElementType
    plan: string
}

interface ProviderContextType {
    selectedProvider: Provider | null
    setSelectedProvider: (provider: Provider) => void
}

const ProviderContext = React.createContext<ProviderContextType | undefined>(undefined)

export function ProviderProvider({ children }: { children: React.ReactNode }) {
    const [selectedProvider, setSelectedProvider] = React.useState<Provider | null>(providers[0])

    return (
        <ProviderContext.Provider value={{ selectedProvider, setSelectedProvider }}>
            {children}
        </ProviderContext.Provider>
    )
}

export function useProvider() {
    const context = React.useContext(ProviderContext)
    if (context === undefined) {
        throw new Error("useProvider must be used within a ProviderProvider")
    }
    return context
}
