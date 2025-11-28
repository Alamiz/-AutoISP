"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { apiGet } from "@/lib/api"
import { auth } from "@/lib/auth"

interface User {
    id: number
    email: string
    username: string
    first_name: string
    last_name: string
    is_staff: boolean
}

interface UserContextType {
    user: User | null
    isLoading: boolean
    fetchUser: () => Promise<void>
    clearUser: () => void
}

const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    const fetchUser = async () => {
        if (!auth.isAuthenticated()) {
            setIsLoading(false)
            return
        }

        try {
            setIsLoading(true)
            const userData = await apiGet<User>("/api/me", "master")
            setUser(userData)
        } catch (error) {
            console.error("Failed to fetch user:", error)
            setUser(null)
        } finally {
            setIsLoading(false)
        }
    }

    const clearUser = () => {
        setUser(null)
    }

    useEffect(() => {
        fetchUser()
    }, [])

    return (
        <UserContext.Provider value={{ user, isLoading, fetchUser, clearUser }}>
            {children}
        </UserContext.Provider>
    )
}

export function useUser() {
    const context = useContext(UserContext)
    if (context === undefined) {
        throw new Error("useUser must be used within a UserProvider")
    }
    return context
}
