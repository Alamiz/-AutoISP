"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { auth } from "@/lib/auth"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { useUser } from "@/contexts/user-context"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import "./styles.css"

export default function LoginPage() {
    const [isLoading, setIsLoading] = useState(false)
    const router = useRouter()
    const { fetchUser } = useUser()

    useEffect(() => {
        // Resize window to smaller size for login screen
        if (typeof window !== 'undefined' && window.electronAPI) {
            window.electronAPI.resize(700, 850);
        }
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)

        const formData = new FormData(e.target as HTMLFormElement)
        const username = formData.get("username") as string
        const password = formData.get("password") as string

        try {
            await auth.login(username, password)
            await fetchUser()
            toast.success("Logged in successfully")
            router.push("/")
        } catch (error: any) {
            if (error && error.status === 401) {
                toast.error("Invalid credentials")
            } else {
                toast.error("An unexpected error occurred. Please contact support.")
                console.error(error)
            }
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="relative h-screen w-full flex items-center justify-center overflow-hidden bg-background">
            {/* Animated Background */}
            <div className="grid-overlay"></div>
            <div className="bg-shape shape1"></div>
            <div className="bg-shape shape2"></div>
            <div className="bg-shape shape3"></div>

            {/* Login Card */}
            <div className="relative z-10 w-full max-w-[480px] animate-in fade-in zoom-in duration-300 p-4">
                <Card className="border-border/50 bg-card/95 backdrop-blur-sm shadow-xl">
                    <CardHeader className="text-center space-y-2">
                        <CardTitle className="text-2xl font-bold">Welcome back!</CardTitle>
                        <CardDescription>
                            We're so excited to see you again!
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="username" className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
                                    Email or Phone Number <span className="text-destructive">*</span>
                                </Label>
                                <Input
                                    id="username"
                                    name="username"
                                    type="text"
                                    className="bg-background"
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="password" className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
                                    Password <span className="text-destructive">*</span>
                                </Label>
                                <Input
                                    id="password"
                                    name="password"
                                    type="password"
                                    className="bg-background"
                                    required
                                />
                                <div className="flex justify-start">
                                    <Link
                                        href="/forgot-password"
                                        className="text-sm text-primary hover:underline font-medium"
                                    >
                                        Forgot your password?
                                    </Link>
                                </div>
                            </div>

                            <Button
                                type="submit"
                                disabled={isLoading}
                                className="w-full font-semibold"
                                size="lg"
                            >
                                {isLoading ? (
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                                        Logging in...
                                    </div>
                                ) : (
                                    "Log In"
                                )}
                            </Button>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
