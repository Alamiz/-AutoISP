"use client"

import { LiveLogPanel } from "@/components/live-log-panel"

export default function LogsPage() {
    return (
        <div className="flex flex-col h-screen w-screen bg-background">
            <LiveLogPanel isDetached />
        </div>
    )
}
