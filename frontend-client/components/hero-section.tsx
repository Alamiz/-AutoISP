"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Zap, CheckCircle2, AlertCircle } from "lucide-react"

export function HeroSection() {
    // Mock data - will be replaced with real data
    const stats = {
        totalAccounts: 12,
        activeAccounts: 9,
        successRate: 94.2,
        failedJobs: 1,
        completedToday: 23,
        averageRunTime: "2.3s",
    }

    return (
        <div className="space-y-8">
            {/* Main Hero */}
            <div className="space-y-4">
                <div className="space-y-2">
                    <h2 className="text-4xl md:text-5xl font-bold text-foreground text-balance">Automate Your ISP Workflow</h2>
                    <p className="text-lg text-muted-foreground max-w-2xl">
                        Manage multiple accounts, run automations, and monitor performance all in one place.
                    </p>
                </div>
            </div>

            {/* Key Metrics Grid */}
        </div>
    )
}
