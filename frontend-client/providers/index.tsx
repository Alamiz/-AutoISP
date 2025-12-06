"use client";

import { QueryProvider } from "./query-provider"
import { BreadcrumbProvider } from "@/components/breadcrumb-context";
import { UserProvider } from "@/contexts/user-context";
import { ProviderProvider } from "@/contexts/provider-context";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <BreadcrumbProvider>
      <QueryProvider>
        <UserProvider>
          <ProviderProvider>
            {children}
          </ProviderProvider>
        </UserProvider>
      </QueryProvider>
    </BreadcrumbProvider>
  );
}
