"use client";

import { useEffect } from "react";
import { QueryProvider } from "./query-provider"
import { BreadcrumbProvider } from "@/components/breadcrumb-context";
import { UserProvider } from "@/contexts/user-context";
import { ProviderProvider } from "@/contexts/provider-context";
import { JobProvider } from "./job-provider";
import { auth } from "@/lib/auth";
import { apiPost } from "@/lib/api";
import { AccountProvider } from "./account-provider";
import { ProxyProvider } from "./proxy-provider";
import { RouteGuard } from "@/components/route-guard";

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
            <JobProvider>
              <AccountProvider>
                <ProxyProvider>
                  <RouteGuard>
                    {children}
                  </RouteGuard>
                </ProxyProvider>
              </AccountProvider>
            </JobProvider>
          </ProviderProvider>
        </UserProvider>
      </QueryProvider>
    </BreadcrumbProvider>
  );
}

