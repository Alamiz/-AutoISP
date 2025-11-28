"use client";

import { SidebarProvider } from "@/components/ui/sidebar";
import { QueryProvider } from "./query-provider"
import { BreadcrumbProvider } from "@/components/breadcrumb-context";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <BreadcrumbProvider>
        <QueryProvider>
          {children}
        </QueryProvider>
      </BreadcrumbProvider>
    </SidebarProvider>
  );
}
