"use client"

import { Button } from "@/components/ui/button"
import { Menu, X, Home, Zap, BarChart3, Settings, LogOut, Mailbox as MailBox } from "lucide-react"
import Link from "next/link"

interface SidebarProps {
    isOpen: boolean
    onToggle: () => void
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
    const navItems = [
        { icon: Home, label: "Home", href: "/" },
        { icon: MailBox, label: "Accounts", href: "/accounts" },
        { icon: BarChart3, label: "Dashboard", href: "/dashboard" },
        { icon: Zap, label: "Automations", href: "/automations" },
        { icon: Settings, label: "Settings", href: "/settings" },
    ]

    return (
        <>
            {/* Sidebar */}
            <aside
                className={`fixed left-0 top-8 pb-8 h-screen bg-card border-r border-border transition-all duration-300 flex flex-col ${isOpen ? "w-64" : "w-20"
                    }`}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-border">
                    {isOpen && (
                        <div className="flex items-center gap-2">
                            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center">
                                <span className="text-primary-foreground font-bold text-sm">GM</span>
                            </div>
                            <span className="font-semibold text-foreground">Gmail Automation</span>
                        </div>
                    )}
                    <Button variant="ghost" size="icon" onClick={onToggle} className="text-muted-foreground">
                        {isOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
                    </Button>
                </div>

                {/* Navigation Items */}
                <nav className="flex-1 space-y-2 p-4">
                    {navItems.map((item) => (
                        <Link key={item.href} href={item.href}>
                            <Button
                                variant="ghost"
                                className={`w-full justify-start text-muted-foreground hover:text-foreground transition-colors ${isOpen ? "px-4" : "px-2"
                                    }`}
                            >
                                <item.icon className="h-5 w-5" />
                                {isOpen && <span className="ml-3">{item.label}</span>}
                            </Button>
                        </Link>
                    ))}
                </nav>

                {/* Footer */}
                <div className="p-4 border-t border-border">
                    <Button variant="ghost" className={`w-full justify-start text-muted-foreground ${isOpen ? "px-4" : "px-2"}`}>
                        <LogOut className="h-5 w-5" />
                        {isOpen && <span className="ml-3">Logout</span>}
                    </Button>
                </div>
            </aside>

            {/* Toggle Button for Mobile */}
            <div className="fixed bottom-4 right-4 lg:hidden">
                <Button size="icon" onClick={onToggle} className="rounded-full shadow-lg">
                    <Menu className="h-5 w-5" />
                </Button>
            </div>
        </>
    )
}
