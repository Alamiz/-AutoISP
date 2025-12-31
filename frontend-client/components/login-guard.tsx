"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { auth } from "@/lib/auth"

export function LoginGuard({ children }: { children: React.ReactNode }) {
    const router = useRouter()

    useEffect(() => {
        if (auth.isAuthenticated()) {
            router.push("/")
        }
    }, [router])

    return <>{children}</>
}
