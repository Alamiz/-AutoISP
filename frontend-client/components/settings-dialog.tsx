"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { User, Lock, Bell, Palette, Shield, Database, Smartphone, Save, CheckCircle2, Globe } from "lucide-react"
import { useUser } from "@/contexts/user-context"

interface SettingsDialogProps {
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
    const [saveSuccess, setSaveSuccess] = useState<string | null>(null)
    const { user, isLoading } = useUser()

    const handleSave = (section: string) => {
        setSaveSuccess(section)
        setTimeout(() => setSaveSuccess(null), 3000)
    }

    if (isLoading || !user) {
        return null
    }

    const displayName = user.first_name && user.last_name
        ? `${user.first_name} ${user.last_name}`
        : user.username

    const initials = user.first_name && user.last_name
        ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
        : user.username.substring(0, 2).toUpperCase()

    const role = user.is_staff ? "Admin" : "User"

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="w-full h-full max-w-full rounded-none sm:w-[95vw] sm:h-[95vh] sm:max-w-[95vw] sm:rounded-lg overflow-hidden flex flex-col">
                <DialogHeader className="border-b border-border pb-4 shrink-0">
                    <DialogTitle>Settings</DialogTitle>
                    <DialogDescription>Manage your account, preferences, and security settings</DialogDescription>
                </DialogHeader>

                <div className="flex-1 overflow-y-auto">
                    {/* User Profile Card */}
                    <div className="mb-6 px-6 pt-4">
                        <Card className="border-border bg-card">
                            <CardContent className="pt-6">
                                <div className="flex items-center gap-4">
                                    <div className="h-16 w-16 rounded-full bg-linear-to-br from-primary to-primary/80 flex items-center justify-center shrink-0">
                                        <span className="text-2xl font-bold text-primary-foreground">{initials}</span>
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-bold text-foreground">{displayName}</h2>
                                        <p className="text-sm text-muted-foreground">{user.email}</p>
                                        <div className="flex items-center gap-2 mt-2">
                                            <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
                                                {role}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Settings Tabs */}
                    <div className="px-6 pb-6">
                        <Tabs defaultValue="profile" className="w-full">
                            <TabsList className="grid w-full grid-cols-4 lg:grid-cols-7 gap-2 bg-muted p-2 h-auto mb-6">
                                <TabsTrigger
                                    value="profile"
                                    className="gap-2 text-xs lg:text-sm data-[state=active]:bg-background flex items-center justify-center"
                                >
                                    <User className="h-4 w-4" />
                                    <span className="hidden sm:inline">Profile</span>
                                </TabsTrigger>
                                <TabsTrigger
                                    value="security"
                                    className="gap-2 text-xs lg:text-sm data-[state=active]:bg-background flex items-center justify-center"
                                >
                                    <Lock className="h-4 w-4" />
                                    <span className="hidden sm:inline">Security</span>
                                </TabsTrigger>
                                <TabsTrigger
                                    value="notifications"
                                    className="gap-2 text-xs lg:text-sm data-[state=active]:bg-background flex items-center justify-center"
                                >
                                    <Bell className="h-4 w-4" />
                                    <span className="hidden sm:inline">Notifications</span>
                                </TabsTrigger>
                                <TabsTrigger
                                    value="preferences"
                                    className="gap-2 text-xs lg:text-sm data-[state=active]:bg-background flex items-center justify-center"
                                >
                                    <Palette className="h-4 w-4" />
                                    <span className="hidden sm:inline">Preferences</span>
                                </TabsTrigger>
                                <TabsTrigger
                                    value="api"
                                    className="gap-2 text-xs lg:text-sm data-[state=active]:bg-background flex items-center justify-center"
                                >
                                    <Globe className="h-4 w-4" />
                                    <span className="hidden sm:inline">API</span>
                                </TabsTrigger>
                                <TabsTrigger
                                    value="storage"
                                    className="gap-2 text-xs lg:text-sm data-[state=active]:bg-background flex items-center justify-center"
                                >
                                    <Database className="h-4 w-4" />
                                    <span className="hidden sm:inline">Storage</span>
                                </TabsTrigger>
                                <TabsTrigger
                                    value="privacy"
                                    className="gap-2 text-xs lg:text-sm data-[state=active]:bg-background flex items-center justify-center"
                                >
                                    <Shield className="h-4 w-4" />
                                    <span className="hidden sm:inline">Privacy</span>
                                </TabsTrigger>
                            </TabsList>

                            {/* Profile Tab */}
                            <TabsContent value="profile" className="space-y-4 mt-4">
                                <Card className="border-border bg-card">
                                    <CardHeader>
                                        <CardTitle>Profile Information</CardTitle>
                                        <CardDescription>Update your personal information</CardDescription>
                                    </CardHeader>
                                    <CardContent className="space-y-6">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="space-y-2">
                                                <label className="text-sm font-medium text-foreground">Full Name</label>
                                                <input
                                                    type="text"
                                                    defaultValue={displayName}
                                                    className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-sm font-medium text-foreground">Email</label>
                                                <input
                                                    type="email"
                                                    defaultValue={user.email}
                                                    disabled
                                                    className="w-full px-3 py-2 rounded-lg border border-border bg-muted text-muted-foreground cursor-not-allowed"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-sm font-medium text-foreground">Username</label>
                                                <input
                                                    type="text"
                                                    defaultValue={user.username}
                                                    className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-sm font-medium text-foreground">Role</label>
                                                <select
                                                    defaultValue={role}
                                                    disabled
                                                    className="w-full px-3 py-2 rounded-lg border border-border bg-muted text-muted-foreground cursor-not-allowed"
                                                >
                                                    <option>{role}</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div className="flex justify-end gap-2">
                                            <Button variant="outline" size="sm">
                                                Cancel
                                            </Button>
                                            <Button onClick={() => handleSave("profile")} size="sm" className="gap-2">
                                                <Save className="h-4 w-4" />
                                                Save
                                            </Button>
                                        </div>
                                        {saveSuccess === "profile" && (
                                            <div className="flex items-center gap-2 p-3 rounded-lg bg-green-500/10 text-green-600 text-sm">
                                                <CheckCircle2 className="h-4 w-4" />
                                                Profile updated successfully
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>
                            </TabsContent>

                            {/* Security Tab */}
                            <TabsContent value="security" className="space-y-4 mt-4">
                                <Card className="border-border bg-card">
                                    <CardHeader>
                                        <CardTitle className="text-lg">Password & Authentication</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-foreground">Current Password</label>
                                            <input
                                                type="password"
                                                placeholder="••••••••"
                                                className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-foreground">New Password</label>
                                            <input
                                                type="password"
                                                placeholder="••••••••"
                                                className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                            />
                                        </div>
                                        <div className="flex justify-end gap-2">
                                            <Button variant="outline" size="sm">
                                                Cancel
                                            </Button>
                                            <Button onClick={() => handleSave("security")} size="sm" className="gap-2">
                                                <Save className="h-4 w-4" />
                                                Update
                                            </Button>
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card className="border-border bg-card">
                                    <CardHeader>
                                        <CardTitle className="text-lg">Two-Factor Authentication</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-3">
                                        <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50 border border-border">
                                            <div className="flex items-center gap-3">
                                                <Smartphone className="h-5 w-5 text-muted-foreground" />
                                                <div>
                                                    <p className="text-sm font-medium">Authenticator App</p>
                                                    <p className="text-xs text-muted-foreground">Google Authenticator or similar</p>
                                                </div>
                                            </div>
                                            <Button variant="outline" size="sm">
                                                Enable
                                            </Button>
                                        </div>
                                    </CardContent>
                                </Card>
                            </TabsContent>

                            {/* Notifications Tab */}
                            <TabsContent value="notifications" className="space-y-4 mt-4">
                                <Card className="border-border bg-card">
                                    <CardHeader>
                                        <CardTitle className="text-lg">Email Notifications</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-3">
                                        {[
                                            { label: "Automation Completed", desc: "When automations finish running" },
                                            { label: "Automation Failed", desc: "When automations encounter errors" },
                                            { label: "Account Errors", desc: "Account connection issues" },
                                            { label: "Weekly Digest", desc: "Summary of your automation activity" },
                                        ].map((notification, i) => (
                                            <div key={i} className="flex items-center justify-between p-4 rounded-lg hover:bg-muted/50">
                                                <div>
                                                    <p className="text-sm font-medium text-foreground">{notification.label}</p>
                                                    <p className="text-xs text-muted-foreground">{notification.desc}</p>
                                                </div>
                                                <input
                                                    type="checkbox"
                                                    defaultChecked
                                                    className="h-4 w-4 rounded border-border accent-primary"
                                                />
                                            </div>
                                        ))}
                                        <div className="flex justify-end gap-2 pt-4 border-t border-border">
                                            <Button variant="outline" size="sm">
                                                Reset
                                            </Button>
                                            <Button onClick={() => handleSave("notifications")} size="sm" className="gap-2">
                                                <Save className="h-4 w-4" />
                                                Save
                                            </Button>
                                        </div>
                                    </CardContent>
                                </Card>
                            </TabsContent>

                            {/* Preferences Tab */}
                            <TabsContent value="preferences" className="space-y-4 mt-4">
                                <Card className="border-border bg-card">
                                    <CardHeader>
                                        <CardTitle className="text-lg">Appearance</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-6">
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-foreground">Theme</label>
                                            <select
                                                defaultValue="auto"
                                                className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                            >
                                                <option value="auto">Auto (Follow system)</option>
                                                <option value="light">Light</option>
                                                <option value="dark">Dark</option>
                                            </select>
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium text-foreground">Language</label>
                                            <select
                                                defaultValue="en"
                                                className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                            >
                                                <option value="en">English</option>
                                                <option value="es">Spanish</option>
                                                <option value="fr">French</option>
                                            </select>
                                        </div>
                                    </CardContent>
                                </Card>
                            </TabsContent>

                            {/* API Tab */}
                            <TabsContent value="api" className="space-y-4 mt-4">
                                <Card className="border-border bg-card">
                                    <CardHeader>
                                        <CardTitle className="text-lg">API Keys</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-3">
                                        <p className="text-sm text-muted-foreground">Manage your API keys for third-party integrations</p>
                                        <Button className="w-full">Generate New Key</Button>
                                    </CardContent>
                                </Card>
                            </TabsContent>

                            {/* Storage Tab */}
                            <TabsContent value="storage" className="space-y-4 mt-4">
                                <Card className="border-border bg-card">
                                    <CardHeader>
                                        <CardTitle className="text-lg">Storage Usage</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div>
                                            <div className="flex justify-between mb-2">
                                                <span className="text-sm text-foreground">Used</span>
                                                <span className="text-sm font-medium">2.5 GB / 10 GB</span>
                                            </div>
                                            <div className="w-full bg-muted rounded-full h-3">
                                                <div className="bg-primary h-3 rounded-full" style={{ width: "25%" }}></div>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            </TabsContent>

                            {/* Privacy Tab */}
                            <TabsContent value="privacy" className="space-y-4 mt-4">
                                <Card className="border-border bg-card">
                                    <CardHeader>
                                        <CardTitle className="text-lg">Privacy Settings</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-3">
                                        <div className="flex items-center justify-between p-4 rounded-lg hover:bg-muted/50">
                                            <label className="text-sm font-medium text-foreground">Share analytics</label>
                                            <input type="checkbox" defaultChecked className="h-4 w-4 rounded border-border accent-primary" />
                                        </div>
                                        <div className="flex items-center justify-between p-4 rounded-lg hover:bg-muted/50">
                                            <label className="text-sm font-medium text-foreground">Allow marketing emails</label>
                                            <input type="checkbox" className="h-4 w-4 rounded border-border accent-primary" />
                                        </div>
                                    </CardContent>
                                </Card>
                            </TabsContent>
                        </Tabs>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    )
}
