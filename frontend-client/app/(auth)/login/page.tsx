"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { auth } from "@/lib/auth"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { useUser } from "@/contexts/user-context"

export default function LoginPage() {
    const [showPassword, setShowPassword] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const router = useRouter()
    const { fetchUser } = useUser()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)

        const formData = new FormData(e.target as HTMLFormElement)
        const username = formData.get("username") as string
        const password = formData.get("password") as string

        try {
            await auth.login(username, password)
            await fetchUser() // Fetch user data immediately after login
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
        <div className="h-screen flex">
            {/* Left Side - Branding */}
            <div className="hidden lg:flex lg:w-1/2 bg-linear-to-br from-primary via-primary/90 to-primary/80 text-white flex-col justify-between p-12">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                            <span className="text-primary font-bold text-xl">A</span>
                        </div>
                        <span className="text-2xl font-bold">Auto ISP</span>
                    </div>
                    <p className="text-primary-foreground/80 text-sm">Manage your email automation workflows</p>
                </div>

                <div className="space-y-8">
                    <div>
                        <h2 className="text-4xl font-bold mb-4">Automate Your ISP Workflow</h2>
                        <p className="text-lg text-primary-foreground/80">
                            Manage multiple ISP accounts, run automations, and monitor everything in one powerful dashboard.
                        </p>
                    </div>

                    <div className="space-y-4">
                        <div className="flex gap-3">
                            <div className="shrink-0 w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
                                <span className="text-sm">✓</span>
                            </div>
                            <div>
                                <p className="font-semibold">Multi-account Management</p>
                                <p className="text-sm text-primary-foreground/70">Handle unlimited ISP accounts</p>
                            </div>
                        </div>
                        <div className="flex gap-3">
                            <div className="shrink-0 w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
                                <span className="text-sm">✓</span>
                            </div>
                            <div>
                                <p className="font-semibold">Advanced Scheduling</p>
                                <p className="text-sm text-primary-foreground/70">Schedule one-time and recurring automations</p>
                            </div>
                        </div>
                        <div className="flex gap-3">
                            <div className="shrink-0 w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
                                <span className="text-sm">✓</span>
                            </div>
                            <div>
                                <p className="font-semibold">Real-time Monitoring</p>
                                <p className="text-sm text-primary-foreground/70">Track execution and logs in real-time</p>
                            </div>
                        </div>
                    </div>
                </div>

                <p className="text-sm text-primary-foreground/60">© 2025 AutoISP. All rights reserved.</p>
            </div>

            {/* Right Side - Login Form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12">
                <div className="w-full max-w-md space-y-8">
                    {/* Mobile Logo */}
                    <div className="lg:hidden flex items-center gap-3 mb-8">
                        <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-xl">A</span>
                        </div>
                        <span className="text-xl font-bold text-foreground">AutoISP</span>
                    </div>

                    {/* Header */}
                    <div>
                        <h1 className="text-3xl font-bold text-foreground">Welcome back</h1>
                        <p className="text-muted-foreground mt-2">Sign in to your account to continue</p>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Email */}
                        <div className="space-y-2">
                            <label htmlFor="username" className="text-sm font-medium text-foreground">
                                Username
                            </label>
                            <div className="relative">
                                <svg
                                    className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                                    />
                                </svg>
                                <Input id="username" name="username" type="text" placeholder="you@example.com" className="pl-10 h-11" required />
                            </div>
                        </div>

                        {/* Password */}
                        <div className="space-y-2">
                            <label htmlFor="password" className="text-sm font-medium text-foreground">
                                Password
                            </label>
                            <div className="relative">
                                <svg
                                    className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                                    />
                                </svg>
                                <Input
                                    id="password"
                                    name="password"
                                    type={showPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    className="pl-10 pr-10 h-11"
                                    required
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                                >
                                    {showPassword ? (
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                            />
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                                            />
                                        </svg>
                                    ) : (
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-4.803m5.596-3.856a3.375 3.375 0 11-4.753 4.753m4.753-4.753L3.596 3.596"
                                            />
                                        </svg>
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Remember & Forgot */}
                        <div className="flex items-center justify-between text-sm">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="checkbox" className="w-4 h-4 rounded border-border" defaultChecked />
                                <span className="text-muted-foreground">Remember me</span>
                            </label>
                            <Link href="/forgot-password" className="text-primary hover:underline font-medium">
                                Forgot password?
                            </Link>
                        </div>

                        {/* Submit Button */}
                        <Button
                            type="submit"
                            disabled={isLoading}
                            className="w-full h-11 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold rounded-lg gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                <>
                                    Sign in
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                    </svg>
                                </>
                            )}
                        </Button>
                    </form>
                </div>
            </div>
        </div>
    )
}
