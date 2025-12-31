"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { auth } from "@/lib/auth"

export function AuthGuard({ children }: { children: React.ReactNode }) {
    const router = useRouter()
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [isChecking, setIsChecking] = useState(true)

    useEffect(() => {
        const checkAuth = () => {
            if (!auth.isAuthenticated()) {
                router.push("/login")
            } else {
                setIsAuthenticated(true)
            }
            setIsChecking(false)
        }

        checkAuth()
    }, [router])

    if (isChecking || !isAuthenticated) {
        return null
    }

    return <>{children}</>
}
