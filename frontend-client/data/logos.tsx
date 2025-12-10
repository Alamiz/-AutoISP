import { cn } from "@/lib/utils"

export const GmxLogo = ({ className }: { className?: string }) => (
    <div className={cn("flex items-center justify-center font-bold text-[0.6rem]", className)}>GM</div>
)

export const WebdeLogo = ({ className }: { className?: string }) => (
    <div className={cn("flex items-center justify-center font-bold text-[0.6rem]", className)}>WE</div>
)