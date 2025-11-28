import { LoginGuard } from "@/components/login-guard"

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <LoginGuard>
            <div className="h-full w-full">
                {children}
            </div>
        </LoginGuard>
    )
}
