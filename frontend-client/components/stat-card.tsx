import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface StatCardProps {
    title: string
    value: string | number
    description: string
    icon: React.ReactNode
    variant: "primary" | "success" | "warning" | "destructive"
    className?: string
}

export function StatCard({ title, value, description, icon, variant, className }: StatCardProps) {
    const variants = {
        primary: {
            bg: "bg-gradient-to-br from-purple-500/15 via-purple-500/5 to-transparent",
            icon: "text-purple-400 bg-purple-500/20 border-purple-500/30 shadow-[0_0_15px_rgba(168,85,247,0.2)]",
            border: "border-purple-500/20 hover:border-purple-500/40",
            glow: "shadow-purple-500/5"
        },
        success: {
            bg: "bg-gradient-to-br from-green-500/15 via-green-500/5 to-transparent",
            icon: "text-green-400 bg-green-500/20 border-green-500/30 shadow-[0_0_15px_rgba(34,197,94,0.2)]",
            border: "border-green-500/20 hover:border-green-500/40",
            glow: "shadow-green-500/5"
        },
        warning: {
            bg: "bg-gradient-to-br from-orange-500/15 via-orange-500/5 to-transparent",
            icon: "text-orange-400 bg-orange-500/20 border-orange-500/30 shadow-[0_0_15px_rgba(249,115,22,0.2)]",
            border: "border-orange-500/20 hover:border-orange-500/40",
            glow: "shadow-orange-500/5"
        },
        destructive: {
            bg: "bg-gradient-to-br from-red-500/15 via-red-500/5 to-transparent",
            icon: "text-red-400 bg-red-500/20 border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.2)]",
            border: "border-red-500/20 hover:border-red-500/40",
            glow: "shadow-red-500/5"
        }
    }

    const config = variants[variant]

    return (
        <Card className={cn(
            "group relative overflow-hidden backdrop-blur-sm transition-all duration-500",
            "hover:scale-[1.02] hover:shadow-2xl hover:-translate-y-1",
            "bg-card/30 border-t border-l",
            config.border,
            config.glow,
            className
        )}>
            {/* Ambient Background Gradient */}
            <div className={cn("absolute inset-0 opacity-40 group-hover:opacity-60 transition-opacity duration-500", config.bg)} />

            {/* Subtle Top-Right Accent */}
            <div className={cn("absolute -top-12 -right-12 w-24 h-24 rounded-full blur-3xl opacity-20 transition-all duration-700 group-hover:scale-150 group-hover:opacity-30",
                variant === "primary" ? "bg-purple-500" :
                    variant === "success" ? "bg-green-500" :
                        variant === "warning" ? "bg-orange-500" : "bg-red-500"
            )} />

            <CardHeader className="relative flex flex-row items-center justify-between space-y-0 pb-1">
                <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground/70 group-hover:text-foreground/90 transition-colors">
                    {title}
                </CardTitle>
                <div className={cn("p-1.5 rounded-lg border transition-all duration-500 group-hover:rotate-6 group-hover:scale-110", config.icon)}>
                    {icon}
                </div>
            </CardHeader>
            <CardContent className="relative pt-0">
                <div className="flex items-baseline gap-1">
                    <div className="text-2xl font-black tracking-tighter bg-clip-text text-transparent bg-linear-to-b from-foreground to-foreground/70">
                        {value}
                    </div>
                </div>
                <div className="flex items-center gap-1.5 mt-1">
                    <div className={cn("w-1 h-1 rounded-full animate-pulse",
                        variant === "primary" ? "bg-purple-400" :
                            variant === "success" ? "bg-green-400" :
                                variant === "warning" ? "bg-orange-400" : "bg-red-400"
                    )} />
                    <p className="text-xs font-semibold text-muted-foreground/60 transition-colors group-hover:text-muted-foreground/90">
                        {description}
                    </p>
                </div>
            </CardContent>
        </Card>
    )
}
