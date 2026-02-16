"use client"

import { PageBreadcrumb } from "@/components/breadcrumb-context"
import { BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from "@/components/ui/breadcrumb"
import { SquareTerminal } from "lucide-react"

export default function JobsPage() {
    return (
        <div className="flex h-full flex-col">
            <PageBreadcrumb>
                <BreadcrumbItem>
                    <BreadcrumbLink href="/">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                    <BreadcrumbPage>Jobs</BreadcrumbPage>
                </BreadcrumbItem>
            </PageBreadcrumb>

            <div className="flex-1 p-6">
                <div className="flex items-center gap-3 mb-6">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                        <SquareTerminal className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">Jobs</h1>
                        <p className="text-sm text-muted-foreground">Manage and monitor automation jobs</p>
                    </div>
                </div>

                <div className="rounded-lg border border-dashed border-muted-foreground/25 p-12 text-center">
                    <p className="text-muted-foreground">Job management coming soon.</p>
                </div>
            </div>
        </div>
    )
}
