"use client"

// import { Dashboard } from "@/components/dashboard"
import { AccountList } from "@/components/account-list"
// import { AutomationControls } from "@/components/automation-controls"
// import { AutomationTemplates } from "@/components/automation-templates"
// import { LiveLogPanel } from "@/components/live-log-panel"
import { AccountProvider } from "@/providers/account-provider"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
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
      </header>

      <main className="container mx-auto px-6 py-8">
        <AccountProvider>
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
            {/* Left Column - Dashboard & Controls */}
            <div className="xl:col-span-1 space-y-6">
              {/* <Dashboard /> */}
              {/* <AutomationControls /> */}
            </div>

            {/* Middle Column - Account Management & Templates */}
            <div className="xl:col-span-2 space-y-6">
              <AccountList />
              {/* <AutomationTemplates /> */}
            </div>

            {/* Right Column - Live Logs */}
            <div className="xl:col-span-1">
              {/* <LiveLogPanel /> */}
            </div>
          </div>
        </AccountProvider>
      </main>
    </div>
  )
}
