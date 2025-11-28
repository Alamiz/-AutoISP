"use client"

import React, { createContext, useContext, useEffect, useState } from "react"

interface BreadcrumbContextType {
    breadcrumb: React.ReactNode
    setBreadcrumb: (breadcrumb: React.ReactNode) => void
}

const BreadcrumbContext = createContext<BreadcrumbContextType | undefined>(undefined)

export function BreadcrumbProvider({ children }: { children: React.ReactNode }) {
    const [breadcrumb, setBreadcrumb] = useState<React.ReactNode>(null)

    return (
        <BreadcrumbContext.Provider value={{ breadcrumb, setBreadcrumb }}>
            {children}
        </BreadcrumbContext.Provider>
    )
}

export function useBreadcrumb() {
    const context = useContext(BreadcrumbContext)
    if (context === undefined) {
        throw new Error("useBreadcrumb must be used within a BreadcrumbProvider")
    }
    return context
}

export function PageBreadcrumb({ children }: { children: React.ReactNode }) {
    const { setBreadcrumb } = useBreadcrumb()

    useEffect(() => {
        setBreadcrumb(children)
    }, [children, setBreadcrumb])

    return null
}
