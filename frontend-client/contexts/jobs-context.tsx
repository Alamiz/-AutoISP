"use client"

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from "react"

export interface Job {
    id: string
    account_id: string
    account_email: string
    automation_id: string
    automation_name: string
    status: "queued" | "running" | "completed" | "failed"
    queued_at: string
    started_at?: string
    completed_at?: string
    progress: number
    error?: string
}

interface JobsState {
    running: Job[]
    queued: Job[]
    completed: Job[]
}

interface JobsContextType {
    jobs: JobsState
    isConnected: boolean
    isAccountBusy: (accountId: string) => boolean
    getAccountJob: (accountId: string) => Job | undefined
    busyAccountIds: Set<string>
    onJobComplete: (callback: (job: Job) => void) => () => void
    stopJob: (jobId: string) => Promise<void>
    stopAllJobs: () => Promise<void>
}

const JobsContext = createContext<JobsContextType | undefined>(undefined)

const LOCAL_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const WS_URL = LOCAL_API_URL.replace("http", "ws") + "/jobs/ws"

export function JobsProvider({ children }: { children: React.ReactNode }) {
    const [jobs, setJobs] = useState<JobsState>({ running: [], queued: [], completed: [] })
    const [isConnected, setIsConnected] = useState(false)
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
    const jobCompleteCallbacksRef = useRef<Set<(job: Job) => void>>(new Set())

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return

        const ws = new WebSocket(WS_URL)

        ws.onopen = () => {
            console.log("[Jobs WS] Connected")
            setIsConnected(true)
        }

        ws.onclose = () => {
            console.log("[Jobs WS] Disconnected, reconnecting in 3s...")
            setIsConnected(false)
            wsRef.current = null
            // Auto-reconnect
            reconnectTimeoutRef.current = setTimeout(connect, 3000)
        }

        ws.onerror = (err) => {
            console.error("[Jobs WS] Error:", err)
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                handleMessage(data)
            } catch (e) {
                console.error("[Jobs WS] Failed to parse message:", e)
            }
        }

        wsRef.current = ws
    }, [])

    const handleMessage = useCallback((data: any) => {
        switch (data.type) {
            case "snapshot":
                setJobs({
                    running: data.running || [],
                    queued: data.queued || [],
                    completed: data.completed || [],
                })
                break

            case "job_queued":
                setJobs((prev) => ({
                    ...prev,
                    queued: [...prev.queued, data.job],
                }))
                break

            case "job_started":
                setJobs((prev) => ({
                    ...prev,
                    queued: prev.queued.filter((j) => j.id !== data.job.id),
                    running: [...prev.running, data.job],
                }))
                break

            case "job_progress":
                setJobs((prev) => ({
                    ...prev,
                    running: prev.running.map((j) =>
                        j.id === data.job.id ? { ...j, progress: data.job.progress } : j
                    ),
                }))
                break

            case "job_completed":
            case "job_failed":
                setJobs((prev) => ({
                    ...prev,
                    running: prev.running.filter((j) => j.id !== data.job.id),
                    completed: [data.job, ...prev.completed.slice(0, 9)],
                }))
                // Notify all subscribers that a job completed
                jobCompleteCallbacksRef.current.forEach((callback) => callback(data.job))
                break

            case "job_cancelled":
            case "job_stopped":
                setJobs((prev) => ({
                    ...prev,
                    running: prev.running.filter((j) => j.id !== data.job.id),
                    queued: prev.queued.filter((j) => j.id !== data.job.id),
                    completed: [data.job, ...prev.completed.slice(0, 9)],
                }))
                break
        }
    }, [])

    useEffect(() => {
        connect()

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current)
            }
            if (wsRef.current) {
                wsRef.current.close()
            }
        }
    }, [connect])

    // Compute busy account IDs
    const busyAccountIds = React.useMemo(() => {
        const ids = new Set<string>()
        jobs.running.forEach((j) => ids.add(j.account_id))
        jobs.queued.forEach((j) => ids.add(j.account_id))
        return ids
    }, [jobs.running, jobs.queued])

    const isAccountBusy = useCallback(
        (accountId: string) => busyAccountIds.has(accountId),
        [busyAccountIds]
    )

    const getAccountJob = useCallback(
        (accountId: string): Job | undefined => {
            // Check running first
            const running = jobs.running.find((j) => j.account_id === accountId)
            if (running) return running
            // Check queued
            return jobs.queued.find((j) => j.account_id === accountId)
        },
        [jobs.running, jobs.queued]
    )

    // Register callback for job completion events
    const onJobComplete = useCallback((callback: (job: Job) => void) => {
        jobCompleteCallbacksRef.current.add(callback)
        // Return unsubscribe function
        return () => {
            jobCompleteCallbacksRef.current.delete(callback)
        }
    }, [])

    // Stop a specific job
    const stopJob = useCallback(async (jobId: string) => {
        const res = await fetch(`${LOCAL_API_URL}/jobs/${jobId}/stop`, {
            method: "POST",
        })
        if (!res.ok) {
            throw new Error(`Failed to stop job: ${res.status}`)
        }
    }, [])

    // Stop all jobs
    const stopAllJobs = useCallback(async () => {
        const res = await fetch(`${LOCAL_API_URL}/jobs/stop-all`, {
            method: "POST",
        })
        if (!res.ok) {
            throw new Error(`Failed to stop all jobs: ${res.status}`)
        }
    }, [])

    return (
        <JobsContext.Provider value={{ jobs, isConnected, isAccountBusy, getAccountJob, busyAccountIds, onJobComplete, stopJob, stopAllJobs }}>
            {children}
        </JobsContext.Provider>
    )
}

export function useJobs() {
    const context = useContext(JobsContext)
    if (!context) {
        throw new Error("useJobs must be used within a JobsProvider")
    }
    return context
}
