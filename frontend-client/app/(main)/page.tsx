"use client"

import { useState, useEffect } from "react"
// import { Dashboard } from "@/components/dashboard"
import { AccountList } from "@/components/account-list"
import { AutomationControls } from "@/components/automation-controls"
import { HeroSection } from "@/components/hero-section"
import { QuickActions } from "@/components/quick-actions"
import { BreadcrumbItem, BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb"
// import { AutomationControls } from "@/components/automation-controls"
// import { AutomationTemplates } from "@/components/automation-templates"
import { LiveLogPanel } from "@/components/live-log-panel"
import { AccountProvider } from "@/providers/account-provider"

import { PageBreadcrumb } from "@/components/breadcrumb-context"

export default function HomePage() {
  const [isLogPanelDetached, setIsLogPanelDetached] = useState(false)

  useEffect(() => {
    // Clear logs on initial load
    localStorage.removeItem("auto_isp_logs")

    // Listen for when log panel window is closed
    const handleAttached = () => {
      setIsLogPanelDetached(false)
    }

    window.electronAPI?.onLogPanelAttached(handleAttached)

    return () => {
      window.electronAPI?.removeLogPanelAttachedListener?.(handleAttached)
    }
  }, [])

  // Handle detach - set state when user clicks detach
  const handleDetach = () => {
    window.electronAPI?.detachLogPanel()
    setIsLogPanelDetached(true)
  }

  return (
    <div className="flex h-full bg-background">
      <PageBreadcrumb>
        <BreadcrumbItem>
          <BreadcrumbLink href="/">Home</BreadcrumbLink>
        </BreadcrumbItem>
      </PageBreadcrumb>
      {/* <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">GM</span>
              </div>
              <h1 className="text-xl font-semibold text-foreground">Gmail Automation Manager</h1>
            </div>
            <button onClick={() => window.electronAPI.openDevTools()} type="button" className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">Developer Console</span>
            </button>
          </div>
        </div>
      </header> */}

      <main className={`flex-1 overflow-auto transition-all duration-300`}>
        <AccountProvider>

          <div className="p-6 space-y-6 h-full flex flex-col">
            {/* <HeroSection /> */}
            {/* <QuickActions /> */}
            <div className={`grid grid-cols-1 ${isLogPanelDetached ? '2xl:grid-cols-3' : '2xl:grid-cols-4'} gap-8 2xl:h-full`}>
              {/* Left Column - Dashboard & Controls */}
              <div className="2xl:col-span-1 space-y-6">
                {/* <Dashboard /> */}
                <AutomationControls />
              </div>

              {/* Middle Column - Account Management & Templates */}
              <div className={`${isLogPanelDetached ? '2xl:col-span-2' : '2xl:col-span-2'} space-y-6 min-h-[400px] 2xl:h-full 2xl:min-h-0`}>
                <AccountList />
                {/* <AutomationTemplates /> */}
              </div>

              {/* Right Column - Live Logs (hidden when detached) */}
              {!isLogPanelDetached && (
                <div className="2xl:col-span-1 min-h-[300px] 2xl:h-full 2xl:min-h-0">
                  <LiveLogPanel onDetach={handleDetach} />
                </div>
              )}
            </div>
          </div>
        </AccountProvider>
      </main>
    </div>
  )
}
