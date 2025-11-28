"use client";

import { SidebarProvider } from "@/components/ui/sidebar";
import { QueryProvider } from "./query-provider"
import { BreadcrumbProvider } from "@/components/breadcrumb-context";
import { UserProvider } from "@/contexts/user-context";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider className="h-full">
      <BreadcrumbProvider>
        <QueryProvider>
          <UserProvider>
            {children}
          </UserProvider>
        </QueryProvider>
      </BreadcrumbProvider>
    </SidebarProvider>
  );
}
