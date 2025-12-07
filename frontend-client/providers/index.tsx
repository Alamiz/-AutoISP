"use client";

import { useEffect } from "react";
import { QueryProvider } from "./query-provider"
import { BreadcrumbProvider } from "@/components/breadcrumb-context";
import { UserProvider } from "@/contexts/user-context";
import { ProviderProvider } from "@/contexts/provider-context";
import { auth } from "@/lib/auth";
import { apiPost } from "@/lib/api";

export default function Providers({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const syncToken = async () => {
      const token = auth.getAccessToken();
      if (token) {
        try {
          await apiPost("/auth/set-token", { access_token: token }, "local");
          console.log("Token synced to local backend");
        } catch (err) {
          console.error("Failed to sync token:", err);
        }
      }
    };
    syncToken();
  }, []);

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
