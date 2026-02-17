import { Badge } from "@/components/ui/badge"
import {
    CheckCircle2,
    XCircle,
    AlertCircle,
    Clock,
    Loader2,
    ShieldAlert,
    Lock,
    Smartphone,
    BadgeHelp,
    CircleDashed,
} from "lucide-react"

interface JobAccountStatusBadgeProps {
    status: string
    className?: string
}

export function JobAccountStatusBadge({ status, className }: JobAccountStatusBadgeProps) {
    const normalizedStatus = (status || "queued").toLowerCase()

    switch (normalizedStatus) {
        case "success":
        case "completed":
            return (
                <Badge variant="success" className={className}>
                    <CheckCircle2 className="mr-1 h-3 w-3" />
                    {normalizedStatus === "success" ? "Success" : "Completed"}
                </Badge>
            )
        case "failed":
            return (
                <Badge variant="destructive" className={className}>
                    <XCircle className="mr-1 h-3 w-3" />
                    Failed
                </Badge>
            )
        case "running":
            return (
                <Badge variant="warning" className={className}>
                    <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                    Running
                </Badge>
            )
        case "queued":
            return (
                <Badge variant="secondary" className={className}>
                    <CircleDashed className="mr-1 h-3 w-3" />
                    Queued
                </Badge>
            )
        case "wrong_password":
            return (
                <Badge variant="destructive" className={className}>
                    <AlertCircle className="mr-1 h-3 w-3" />
                    Wrong Password
                </Badge>
            )
        case "wrong_email":
            return (
                <Badge variant="destructive" className={className}>
                    <AlertCircle className="mr-1 h-3 w-3" />
                    Wrong Email
                </Badge>
            )
        case "locked":
            return (
                <Badge variant="destructive" className={className}>
                    <Lock className="mr-1 h-3 w-3" />
                    Locked
                </Badge>
            )
        case "suspended":
            return (
                <Badge variant="destructive" className={className}>
                    <ShieldAlert className="mr-1 h-3 w-3" />
                    Suspended
                </Badge>
            )
        case "phone_verification":
            return (
                <Badge variant="warning" className={className}>
                    <Smartphone className="mr-1 h-3 w-3" />
                    Phone Verify
                </Badge>
            )
        case "captcha":
            return (
                <Badge variant="warning" className={className}>
                    <BadgeHelp className="mr-1 h-3 w-3" />
                    Captcha
                </Badge>
            )
        case "cancelled":
            return (
                <Badge variant="secondary" className={className}>
                    <XCircle className="mr-1 h-3 w-3" />
                    Cancelled
                </Badge>
            )
        default:
            return (
                <Badge variant="secondary" className={className}>
                    {status}
                </Badge>
            )
    }
}
