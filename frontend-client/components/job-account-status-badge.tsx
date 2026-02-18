import { Badge } from "@/components/ui/badge"
import { CheckCircle2, XCircle, AlertCircle, Loader2, ShieldAlert, Lock, Smartphone, BadgeHelp, CircleDashed } from "lucide-react"
import { cn } from "@/lib/utils"

interface JobAccountStatusBadgeProps {
    status: string
    className?: string
}

export function JobAccountStatusBadge({ status, className }: JobAccountStatusBadgeProps) {
    const normalizedStatus = (status || "queued").toLowerCase()

    const getStatusConfig = (status: string) => {
        switch (status) {
            case "success":
            case "completed":
                return {
                    icon: <CheckCircle2 className="mr-1 h-3 w-3" />,
                    label: status === "success" ? "Success" : "Completed",
                    className: "bg-green-500/10 text-green-500 border-green-500/20"
                }
            case "failed":
                return {
                    icon: <XCircle className="mr-1 h-3 w-3" />,
                    label: "Failed",
                    className: "bg-red-500/10 text-red-500 border-red-500/20"
                }
            case "running":
                return {
                    icon: <Loader2 className="mr-1 h-3 w-3 animate-spin" />,
                    label: "Running",
                    className: "bg-blue-500/10 text-blue-400 border-blue-500/20"
                }
            case "queued":
                return {
                    icon: <CircleDashed className="mr-1 h-3 w-3" />,
                    label: "Queued",
                    className: "bg-orange-500/10 text-orange-400 border-orange-500/20"
                }
            case "wrong_password":
                return {
                    icon: <AlertCircle className="mr-1 h-3 w-3" />,
                    label: "Wrong Password",
                    className: "bg-red-500/10 text-red-500 border-red-500/20"
                }
            case "wrong_email":
                return {
                    icon: <AlertCircle className="mr-1 h-3 w-3" />,
                    label: "Wrong Email",
                    className: "bg-red-500/10 text-red-500 border-red-500/20"
                }
            case "locked":
                return {
                    icon: <Lock className="mr-1 h-3 w-3" />,
                    label: "Locked",
                    className: "bg-red-500/10 text-red-500 border-red-500/20"
                }
            case "suspended":
                return {
                    icon: <ShieldAlert className="mr-1 h-3 w-3" />,
                    label: "Suspended",
                    className: "bg-red-500/10 text-red-500 border-red-500/20"
                }
            case "phone_verification":
                return {
                    icon: <Smartphone className="mr-1 h-3 w-3" />,
                    label: "Phone Verify",
                    className: "bg-orange-500/10 text-orange-500 border-orange-500/20"
                }
            case "captcha":
                return {
                    icon: <BadgeHelp className="mr-1 h-3 w-3" />,
                    label: "Captcha",
                    className: "bg-orange-500/10 text-orange-500 border-orange-500/20"
                }
            case "cancelled":
                return {
                    icon: <XCircle className="mr-1 h-3 w-3" />,
                    label: "Cancelled",
                    className: "bg-gray-500/10 text-gray-500 border-gray-500/20"
                }
            default:
                return {
                    icon: null,
                    label: status || "Unknown",
                    className: "bg-gray-500/10 text-gray-500 border-gray-500/20"
                }
        }
    }

    const config = getStatusConfig(normalizedStatus)

    return (
        <Badge
            variant="outline"
            className={cn(
                "font-medium border shadow-none",
                config.className,
                className
            )}
        >
            {config.icon}
            {config.label}
        </Badge>
    )
}
