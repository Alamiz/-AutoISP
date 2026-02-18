"use client"

import { useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"

export function RouteGuard({ children }: { children: React.ReactNode }) {
    const router = useRouter()
    const pathname = usePathname()
    const [authorized, setAuthorized] = useState(false)

    useEffect(() => {
        const checkAuth = () => {
            // Check for token in localStorage (common in our lib/auth.ts) 
            // and cookies (matches old middleware)
            const tokenLS = typeof window !== 'undefined' ? localStorage.getItem("auth_tokens") : null
            const hasToken = !!tokenLS || document.cookie.includes("auth_tokens")
            const isAuthPage = pathname.startsWith("/login")

            if (!hasToken && !isAuthPage) {
                setAuthorized(false)
                router.push("/login")
            } else if (hasToken && isAuthPage) {
                router.push("/")
            } else {
                setAuthorized(true)
            }
        }

        checkAuth()
    }, [pathname, router])

    return authorized ? <>{children}</> : <div className="h-screen w-screen bg-background" />
}
