"use client"

import { useEffect } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { Separator } from "@/components/ui/separator"
import { Breadcrumb, BreadcrumbItem, BreadcrumbList, BreadcrumbPage } from "@/components/ui/breadcrumb"
import { useBreadcrumb } from "@/components/breadcrumb-context"
import { AuthGuard } from "@/components/auth-guard"

export default function MainLayout({
    children,
}: {
    children: React.ReactNode
}) {
    useEffect(() => {
        // Restore window to default size when entering main app
        if (typeof window !== 'undefined' && window.electronAPI) {
            window.electronAPI.resize(1200, 800);
        }
    }, []);

    return (
        <AuthGuard>
            <AppSidebar />
            <SidebarInset>
                <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
                    <div className="flex items-center gap-2 px-4">
                        <SidebarTrigger className="-ml-1" />
                        <Separator
                            orientation="vertical"
                            className="mr-2 data-[orientation=vertical]:h-4"
                        />
                        <BreadcrumbDisplay />
                    </div>
                </header>
                <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
                    {children}
                </div>
            </SidebarInset>
        </AuthGuard>
    )
}

function BreadcrumbDisplay() {
    const { breadcrumb } = useBreadcrumb()

    return (
        <Breadcrumb>
            <BreadcrumbList>
                {breadcrumb ?? (
                    <BreadcrumbItem>
                        <BreadcrumbPage>Home</BreadcrumbPage>
                    </BreadcrumbItem>
                )}
            </BreadcrumbList>
        </Breadcrumb>
    )
}
