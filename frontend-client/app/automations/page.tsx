import { PageBreadcrumb } from '@/components/breadcrumb-context'
import { BreadcrumbItem, BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'

function AutomationsPage() {
    return (
        <>
            <PageBreadcrumb>
                <BreadcrumbItem>
                    <BreadcrumbLink href="/">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                    <BreadcrumbPage>Automations</BreadcrumbPage>
                </BreadcrumbItem>
            </PageBreadcrumb>
            <div>AutomationsPage</div>
        </>
    )
}

export default AutomationsPage