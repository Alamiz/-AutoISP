import { Badge } from "@/components/ui/badge"
import { CheckCircle2, XCircle, AlertCircle, ShieldAlert, BadgeHelp, Lock, Smartphone, Timer } from "lucide-react"

interface AccountStatusBadgeProps {
    status: string
    className?: string
}

export function AccountStatusBadge({ status, className }: AccountStatusBadgeProps) {
    const normalizedStatus = (status || "unknown").toLowerCase()

    switch (normalizedStatus) {
        case "active":
            return (
                <Badge variant="success" className={className}>
                    <CheckCircle2 className="mr-1 h-3 w-3" />
                    Active
                </Badge>
            )
        case "valid": // Legacy/Alternative
            return (
                <Badge variant="success" className={className}>
                    <CheckCircle2 className="mr-1 h-3 w-3" />
                    Valid
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
        case "failed":
            return (
                <Badge variant="destructive" className={className}>
                    <XCircle className="mr-1 h-3 w-3" />
                    Failed
                </Badge>
            )
        case "unknown":
        default:
            return (
                <Badge variant="secondary" className={className}>
                    Unknown
                </Badge>
            )
    }
}
