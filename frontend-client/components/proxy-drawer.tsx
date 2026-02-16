"use client"

import { useState, useEffect } from "react"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { apiPatch, apiPost } from "@/lib/api"
import { toast } from "sonner"

interface Proxy {
    id: number
    ip: string
    port: number
    username?: string
    password?: string
    created_at?: string
}

interface ProxyDrawerProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    editingProxy?: Proxy | null
    onProxySaved: () => void
}

export function ProxyDrawer({ open, onOpenChange, editingProxy, onProxySaved }: ProxyDrawerProps) {
    const [loading, setLoading] = useState(false)
    const [formData, setFormData] = useState({
        ip: "",
        port: "",
        username: "",
        password: ""
    })

    useEffect(() => {
        if (editingProxy) {
            setFormData({
                ip: editingProxy.ip || "",
                port: editingProxy.port?.toString() || "",
                username: editingProxy.username || "",
                password: editingProxy.password || ""
            })
        } else {
            setFormData({
                ip: "",
                port: "",
                username: "",
                password: ""
            })
        }
    }, [editingProxy, open])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            setLoading(true)
            const payload = {
                ip: formData.ip,
                port: parseInt(formData.port),
                username: formData.username || undefined,
                password: formData.password || undefined
            }

            if (editingProxy) {
                await apiPatch(`/proxies/${editingProxy.id}`, payload, "local")
                toast.success("Proxy updated successfully")
            } else {
                await apiPost("/proxies", payload, "local")
                toast.success("Proxy added successfully")
            }

            onProxySaved()
            onOpenChange(false)
        } catch (error: any) {
            toast.error(error.message || "Failed to save proxy")
        } finally {
            setLoading(false)
        }
    }

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="bg-card border-border p-0 sm:max-w-md w-full">
                <div className="p-6 pb-2">
                    <SheetHeader>
                        <SheetTitle className="text-foreground">
                            {editingProxy ? "Edit Proxy" : "Add Proxy"}
                        </SheetTitle>
                        <SheetDescription className="text-muted-foreground">
                            {editingProxy
                                ? "Update proxy details."
                                : "Add a new proxy to your pool."}
                        </SheetDescription>
                    </SheetHeader>
                </div>

                <ScrollArea className="h-[calc(100vh-140px)] px-4">
                    <form onSubmit={handleSubmit} className="space-y-6 pb-6 p-2">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="ip">IP Address</Label>
                                <Input
                                    id="ip"
                                    value={formData.ip}
                                    onChange={(e) => setFormData({ ...formData, ip: e.target.value })}
                                    placeholder="1.2.3.4"
                                    required
                                    className="bg-input border-border"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="port">Port</Label>
                                <Input
                                    id="port"
                                    type="number"
                                    value={formData.port}
                                    onChange={(e) => setFormData({ ...formData, port: e.target.value })}
                                    placeholder="8080"
                                    required
                                    className="bg-input border-border"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="username">Username (Optional)</Label>
                                <Input
                                    id="username"
                                    value={formData.username}
                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                    className="bg-input border-border"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="password">Password (Optional)</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    className="bg-input border-border"
                                />
                            </div>
                        </div>

                        <div className="flex gap-3 pt-4">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => onOpenChange(false)}
                                className="flex-1 border-border hover:bg-accent"
                            >
                                Cancel
                            </Button>
                            <Button
                                type="submit"
                                className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                                disabled={loading || !formData.ip || !formData.port}
                            >
                                {loading ? "Saving..." : editingProxy ? "Update Proxy" : "Add Proxy"}
                            </Button>
                        </div>
                    </form>
                </ScrollArea>
            </SheetContent>
        </Sheet>
    )
}
