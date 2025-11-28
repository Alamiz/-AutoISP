import { BreadcrumbItem, BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb';
import { PageBreadcrumb } from '@/components/breadcrumb-context';

function AccountsPage() {
    return (
        <>
            <PageBreadcrumb>
                <BreadcrumbItem>
                    <BreadcrumbLink href="/">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                    <BreadcrumbPage>Accounts</BreadcrumbPage>
                </BreadcrumbItem>
            </PageBreadcrumb>
            <div>AccountsPage</div>
        </>
    )
}

export default AccountsPage