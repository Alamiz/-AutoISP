"use client"

import React, { createContext, useContext, useState, useCallback, useMemo } from 'react'
import { Proxy } from '@/lib/types'

interface ProxyContextType {
    selectedProxies: Proxy[]
    selectedProxiesMap: Record<string, boolean>
    totalCount: number
    statusFilter: string | null
    setSelectedProxies: (proxies: Proxy[]) => void
    setSelectedProxiesMap: (updater: Record<string, boolean> | ((prev: Record<string, boolean>) => Record<string, boolean>)) => void
    selectProxy: (proxy: Proxy) => void
    deselectProxy: (proxyId: number | string) => void
    selectAllProxies: (proxies: Proxy[]) => void
    clearSelection: () => void
    setTotalCount: (count: number) => void
    setStatusFilter: (status: string | null) => void
    isProxySelected: (proxyId: number | string) => boolean
    getSelectedCount: () => number
}

const ProxyContext = createContext<ProxyContextType | undefined>(undefined)

export function ProxyProvider({ children }: { children: React.ReactNode }) {
    const [selectedProxies, setSelectedProxiesInternal] = useState<Proxy[]>([])
    const [selectedProxiesMap, setSelectedProxiesMapInternal] = useState<Record<string, boolean>>({})
    const [totalCount, setTotalCount] = useState(0)
    const [statusFilter, setStatusFilter] = useState<string | null>(null)

    const setSelectedProxiesMap = useCallback((updaterOrValue: any) => {
        setSelectedProxiesMapInternal(prev => {
            const nextMap = typeof updaterOrValue === 'function' ? updaterOrValue(prev) : updaterOrValue
            return nextMap
        })
    }, [])

    const setSelectedProxies = useCallback((proxies: Proxy[]) => {
        setSelectedProxiesInternal(proxies)
        const newMap: Record<string, boolean> = {}
        proxies.forEach(p => {
            newMap[String(p.id)] = true
        })
        setSelectedProxiesMapInternal(newMap)
    }, [])

    const selectProxy = useCallback((proxy: Proxy) => {
        setSelectedProxiesInternal(prev => {
            if (prev.some(p => p.id === proxy.id)) return prev
            return [...prev, proxy]
        })
        setSelectedProxiesMapInternal(prev => ({
            ...prev,
            [String(proxy.id)]: true
        }))
    }, [])

    const deselectProxy = useCallback((proxyId: number | string) => {
        setSelectedProxiesInternal(prev => prev.filter(p => String(p.id) !== String(proxyId)))
        setSelectedProxiesMapInternal(prev => {
            const next = { ...prev }
            delete next[String(proxyId)]
            return next
        })
    }, [])

    const selectAllProxies = useCallback((proxies: Proxy[]) => {
        setSelectedProxiesInternal(proxies)
        const newMap: Record<string, boolean> = {}
        proxies.forEach(p => {
            newMap[String(p.id)] = true
        })
        setSelectedProxiesMapInternal(newMap)
    }, [])

    const clearSelection = useCallback(() => {
        setSelectedProxiesInternal([])
        setSelectedProxiesMapInternal({})
    }, [])

    const isProxySelected = useCallback((proxyId: number | string) => {
        return !!selectedProxiesMap[String(proxyId)]
    }, [selectedProxiesMap])

    const getSelectedCount = useCallback(() => {
        return Object.keys(selectedProxiesMap).filter(id => selectedProxiesMap[id]).length
    }, [selectedProxiesMap])

    const value = useMemo(() => ({
        selectedProxies,
        selectedProxiesMap,
        totalCount,
        statusFilter,
        setSelectedProxies,
        setSelectedProxiesMap,
        selectProxy,
        deselectProxy,
        selectAllProxies,
        clearSelection,
        setTotalCount,
        setStatusFilter,
        isProxySelected,
        getSelectedCount,
    }), [
        selectedProxies,
        selectedProxiesMap,
        totalCount,
        statusFilter,
        setSelectedProxies,
        setSelectedProxiesMap,
        selectProxy,
        deselectProxy,
        selectAllProxies,
        clearSelection,
        setTotalCount,
        setStatusFilter,
        isProxySelected,
        getSelectedCount,
    ])

    return (
        <ProxyContext.Provider value={value}>
            {children}
        </ProxyContext.Provider>
    )
}

export function useProxies() {
    const context = useContext(ProxyContext)
    if (context === undefined) {
        throw new Error('useProxies must be used within a ProxyProvider')
    }
    return context
}
