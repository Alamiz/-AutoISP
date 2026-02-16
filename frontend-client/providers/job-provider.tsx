"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

interface JobContextType {
    isConnected: boolean
}

const JobContext = createContext<JobContextType>({ isConnected: false })

export function JobProvider({ children }: { children: React.ReactNode }) {
    const [isConnected, setIsConnected] = useState(false)
    const queryClient = useQueryClient()

    useEffect(() => {
        // Safe access to window/env
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        // Replace http/https with ws/wss
        const wsUrl = apiUrl.replace(/^http/, "ws") + "/ws/jobs"

        let ws: WebSocket | null = null;
        let retryTimeout: NodeJS.Timeout;

        const connect = () => {
            if (ws) {
                ws.close()
            }

            console.log("Connecting to WS:", wsUrl)
            ws = new WebSocket(wsUrl)

            ws.onopen = () => {
                setIsConnected(true)
                console.log("WS Connected")
            }

            ws.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data)
                    const { type, data } = msg
                    // console.log("WS Event", type, data)

                    if (type === "job_queued") {
                        queryClient.invalidateQueries({ queryKey: ["jobs"] })
                        queryClient.invalidateQueries({ queryKey: ["active-jobs"] })
                        toast.info(`Job #${data.job_id} queued`)
                    }
                    else if (type === "job_started") {
                        queryClient.invalidateQueries({ queryKey: ["jobs"] })
                        queryClient.invalidateQueries({ queryKey: ["active-jobs"] })
                        queryClient.invalidateQueries({ queryKey: ["job", data.job_id] })
                        toast.info(`Job #${data.job_id} started`)
                    }
                    else if (type === "job_completed") {
                        queryClient.invalidateQueries({ queryKey: ["jobs"] })
                        queryClient.invalidateQueries({ queryKey: ["active-jobs"] })
                        queryClient.invalidateQueries({ queryKey: ["job", data.job_id] })
                        queryClient.invalidateQueries({ queryKey: ["accounts"] })
                        toast.success(`Job #${data.job_id} completed`)
                    }
                    else if (type === "account_update") {
                        // Debounce or just invalidate?
                        // For detailed view, we need to invalidate specific job
                        queryClient.invalidateQueries({ queryKey: ["job", data.job_id] })
                        // Also active jobs might change status
                        queryClient.invalidateQueries({ queryKey: ["active-jobs"] })
                        // And accounts status changes
                        queryClient.invalidateQueries({ queryKey: ["accounts"] })
                    }
                } catch (err) {
                    console.error("WS Parse Error", err)
                }
            }

            ws.onclose = () => {
                setIsConnected(false)
                retryTimeout = setTimeout(connect, 3000)
            }

            ws.onerror = (err) => {
                console.error("WS Error", err)
            }
        }

        connect()

        return () => {
            clearTimeout(retryTimeout)
            ws?.close()
        }
    }, [queryClient])

    return (
        <JobContext.Provider value={{ isConnected }}>
            {children}
        </JobContext.Provider>
    )
}

export const useJobContext = () => useContext(JobContext)
