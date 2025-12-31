"use client"
import { Card, CardContent } from "@/components/ui/card"
import { Plus, Play, Settings, BarChart3, Download, Shield } from "lucide-react"

export function QuickActions() {
    const actions = [
        {
            icon: Plus,
            label: "Add Account",
            description: "Add a new Gmail account",
            color: "bg-blue-500/10 text-blue-500 hover:bg-blue-500/20",
        },
        {
            icon: Play,
            label: "Run Automation",
            description: "Execute an automation",
            color: "bg-green-500/10 text-green-500 hover:bg-green-500/20",
        },
        {
            icon: BarChart3,
            label: "View Analytics",
            description: "Check performance metrics",
            color: "bg-purple-500/10 text-purple-500 hover:bg-purple-500/20",
        },
        {
            icon: Shield,
            label: "Backup Accounts",
            description: "Create account backups",
            color: "bg-orange-500/10 text-orange-500 hover:bg-orange-500/20",
        },
        {
            icon: Settings,
            label: "Settings",
            description: "Configure preferences",
            color: "bg-slate-500/10 text-slate-500 hover:bg-slate-500/20",
        },
        {
            icon: Download,
            label: "Export Data",
            description: "Download reports",
            color: "bg-cyan-500/10 text-cyan-500 hover:bg-cyan-500/20",
        },
    ]

    return (
        <div className="space-y-4 mt-8">
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Quick Actions</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {actions.map((action) => {
                    const Icon = action.icon
                    return (
                        <Card
                            key={action.label}
                            className="bg-card border-border hover:border-primary/50 transition-all cursor-pointer group"
                        >
                            <CardContent className="pt-6">
                                <div className="space-y-3 text-center">
                                    <div
                                        className={`w-10 h-10 rounded-lg ${action.color} flex items-center justify-center mx-auto transition-colors`}
                                    >
                                        <Icon className="h-5 w-5" />
                                    </div>
                                    <div className="space-y-1">
                                        <p className="text-sm font-medium text-foreground">{action.label}</p>
                                        <p className="text-xs text-muted-foreground">{action.description}</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )
                })}
            </div>
        </div>
    )
}
