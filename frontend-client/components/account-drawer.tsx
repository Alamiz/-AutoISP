"use client"

import { useState, useEffect } from "react"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Eye, EyeOff, Shield } from "lucide-react"
import { useFormik } from "formik";
import { accountSchema } from "@/lib/validation/accountSchema"
import { apiPatch, apiPost, apiPut } from "@/lib/api"
import { Account } from "@/lib/types"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useProvider } from "@/contexts/provider-context"

interface AccountDrawerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  editingAccount?: Account | null
  onAccountSaved: () => void
}

const GMX_DOMAINS = [
  "gmx.de"
]

const WEBDE_DOMAINS = [
  "web.de"
]

export function AccountDrawer({ open, onOpenChange, editingAccount, onAccountSaved }: AccountDrawerProps) {
  const [showPassword, setShowPassword] = useState(false)
  const { selectedProvider: globalProvider } = useProvider()
  const defaultProvider = globalProvider?.name === "Web.de" ? "webde" : "gmx"

  // Local state for split email fields
  const [username, setUsername] = useState("")
  const [domain, setDomain] = useState("gmx.de")

  const formik = useFormik({
    initialValues: {
      email: "",
      password: "",
      label: "",
      provider: defaultProvider,
      type: "desktop",
      recovery_email: "",
      number: "",
      proxy_host: "",
      proxy_port: "",
      proxy_username: "",
      proxy_password: "",
      proxy_protocol: "http",
    },
    validationSchema: accountSchema,
    onSubmit: async (values, { setSubmitting, resetForm }) => {
      try {
        if (editingAccount)
          await updateAccount(values)
        else
          await addAccount(values)

        onOpenChange(false)
        resetForm()
        onAccountSaved()
      } catch (error) {
        console.error("Error submitting form:", error);
      } finally {
        setSubmitting(false);
      }
    }
  })

  // Update formik email when username or domain changes
  useEffect(() => {
    if (username && domain) {
      formik.setFieldValue("email", `${username}@${domain}`)
    } else if (username) {
      // If domain is missing, just set username (will fail validation but keeps state)
      formik.setFieldValue("email", username)
    }
  }, [username, domain])

  // Initialize form and local state when editing or opening
  useEffect(() => {
    if (editingAccount) {
      const emailParts = editingAccount.email.split("@")
      const initialUsername = emailParts[0] || ""
      const initialDomain = emailParts[1] || (editingAccount.provider === "webde" ? "web.de" : "gmx.de")

      setUsername(initialUsername)
      setDomain(initialDomain)

      formik.setValues({
        email: editingAccount.email || "",
        password: editingAccount.credentials?.password || "",
        label: editingAccount.label || "",
        provider: editingAccount.provider || "gmx",
        type: editingAccount.type || "desktop",
        recovery_email: editingAccount.credentials?.recovery_email || "",
        number: editingAccount.credentials?.number || "",
        proxy_host: editingAccount.proxy_settings?.host || "",
        proxy_port: editingAccount.proxy_settings?.port?.toString() || "",
        proxy_username: editingAccount.proxy_settings?.username || "",
        proxy_password: editingAccount.proxy_settings?.password || "",
        proxy_protocol: editingAccount.proxy_settings?.protocol || "http",
      })
    } else {
      formik.resetForm()
      // Reset local state
      setUsername("")
      // Set default domain based on provider
      const currentProvider = globalProvider?.name === "Web.de" ? "webde" : "gmx"
      setDomain(currentProvider === "webde" ? "web.de" : "gmx.de")
      formik.setFieldValue("provider", currentProvider)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editingAccount, open]) // Added open to reset when opening fresh

  // Update domain options when provider changes (though provider is now global/fixed per drawer context usually)
  // But if we want to support switching provider inside drawer (which we removed), we'd need this.
  // Since we removed provider switcher from drawer, we rely on globalProvider.
  // However, formik.values.provider might be set from editingAccount.

  const currentProvider = formik.values.provider as "gmx" | "webde"
  const availableDomains = currentProvider === "webde" ? WEBDE_DOMAINS : GMX_DOMAINS

  // Ensure domain is valid for provider
  useEffect(() => {
    if (currentProvider && !availableDomains.includes(domain)) {
      setDomain(availableDomains[0])
    }
  }, [currentProvider])


  async function addAccount(values: any) {
    await apiPost("/api/accounts/", {
      email: values.email,
      provider: values.provider,
      type: values.type,
      credentials: {
        password: values.password,
        recovery_email: values.recovery_email || undefined,
        number: values.number || undefined,
      },
      proxy_settings: values.proxy_host ? {
        host: values.proxy_host,
        port: parseInt(values.proxy_port),
        username: values.proxy_username || undefined,
        password: values.proxy_password || undefined,
        protocol: values.proxy_protocol,
      } : undefined,
      label: values.label,
    })
  }

  async function updateAccount(values: any) {
    await apiPatch(`/api/accounts/${editingAccount?.id}/`, {
      credentials: {
        password: values.password,
        recovery_email: values.recovery_email || undefined,
        number: values.number || undefined,
      },
      provider: values.provider,
      type: values.type,
      proxy_settings: values.proxy_host ? {
        host: values.proxy_host,
        port: parseInt(values.proxy_port),
        username: values.proxy_username || undefined,
        password: values.proxy_password || undefined,
        protocol: values.proxy_protocol,
      } : undefined,
      label: values.label,
    })
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="bg-card border-border p-0 sm:max-w-md w-full">
        <div className="p-6 pb-2">
          <SheetHeader>
            <SheetTitle className="text-foreground">
              {editingAccount ? "Edit Account" : "Add Account"}
            </SheetTitle>
            <SheetDescription className="text-muted-foreground">
              {editingAccount
                ? "Update account details."
                : "Add a new account for automation."}
            </SheetDescription>
          </SheetHeader>
        </div>

        <ScrollArea className="h-[calc(100vh-140px)] px-4 ">
          <form onSubmit={formik.handleSubmit} className="space-y-6 pb-6">
            <Tabs defaultValue="general" className="w-full px-2">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="general">General</TabsTrigger>
                <TabsTrigger value="security">Security</TabsTrigger>
                <TabsTrigger value="proxy">Proxy</TabsTrigger>
              </TabsList>

              <TabsContent value="general" className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Email Address</Label>
                  <div className="flex gap-2">
                    <div className="flex-1">
                      <Input
                        id="username"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        disabled={!!editingAccount}
                        className="bg-input border-border col-span-3"
                        placeholder="username"
                      />
                    </div>
                    <Select
                      value={domain}
                      onValueChange={setDomain}
                      disabled={!!editingAccount}
                    >
                      <SelectTrigger className="bg-input border-border">
                        <SelectValue placeholder="@domain" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableDomains.map(d => (
                          <SelectItem key={d} value={d}>@{d}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  {formik.touched.email && formik.errors.email && (
                    <div className="text-red-500 text-xs">{formik.errors.email}</div>
                  )}
                </div>

                <div className="grid grid-cols-4 gap-12">
                  {/* Provider selection removed - uses global context */}
                  <div className="col-span-1 space-y-2">
                    <Label htmlFor="type">Type</Label>
                    <Select
                      onValueChange={(value) => formik.setFieldValue("type", value)}
                      value={formik.values.type}
                    >
                      <SelectTrigger className="bg-input border-border">
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="desktop">Desktop</SelectItem>
                        <SelectItem value="mobile">Mobile</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="col-span-3 space-y-2">
                    <Label htmlFor="label">Label (Optional)</Label>
                    <Input
                      id="label"
                      {...formik.getFieldProps("label")}
                      className="bg-input border-border"
                    />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="security" className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      {...formik.getFieldProps("password")}
                      className="bg-input border-border pr-10"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                  {formik.touched.password && formik.errors.password && (
                    <div className="text-red-500 text-xs">{formik.errors.password}</div>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="recovery_email">Recovery Email (Optional)</Label>
                  <Input
                    id="recovery_email"
                    type="email"
                    {...formik.getFieldProps("recovery_email")}
                    className="bg-input border-border"
                  />
                  {formik.touched.recovery_email && formik.errors.recovery_email && (
                    <div className="text-red-500 text-xs">{formik.errors.recovery_email}</div>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="number">Phone Number (Optional)</Label>
                  <Input
                    id="number"
                    {...formik.getFieldProps("number")}
                    className="bg-input border-border"
                  />
                </div>
              </TabsContent>

              <TabsContent value="proxy" className="space-y-4 mt-4">
                <Alert className="border-border bg-accent/20 mb-4">
                  <Shield className="h-4 w-4" />
                  <AlertDescription className="text-xs text-muted-foreground">
                    Configure proxy settings if this account requires a specific IP address.
                  </AlertDescription>
                </Alert>

                <div className="grid grid-cols-3 gap-4">
                  <div className="col-span-2 space-y-2">
                    <Label htmlFor="proxy_host">Host</Label>
                    <Input
                      id="proxy_host"
                      {...formik.getFieldProps("proxy_host")}
                      className="bg-input border-border"
                      placeholder="1.2.3.4"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="proxy_port">Port</Label>
                    <Input
                      id="proxy_port"
                      type="number"
                      {...formik.getFieldProps("proxy_port")}
                      className="bg-input border-border"
                      placeholder="8080"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="proxy_protocol">Protocol</Label>
                  <Select
                    onValueChange={(value) => formik.setFieldValue("proxy_protocol", value)}
                    value={formik.values.proxy_protocol}
                  >
                    <SelectTrigger className="bg-input border-border">
                      <SelectValue placeholder="Select protocol" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="http">HTTP</SelectItem>
                      <SelectItem value="https">HTTPS</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="proxy_username">Username (Optional)</Label>
                  <Input
                    id="proxy_username"
                    {...formik.getFieldProps("proxy_username")}
                    className="bg-input border-border"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="proxy_password">Password (Optional)</Label>
                  <Input
                    id="proxy_password"
                    type="password"
                    {...formik.getFieldProps("proxy_password")}
                    className="bg-input border-border"
                  />
                </div>
              </TabsContent>
            </Tabs>

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                className="flex-1 border-border hover:bg-accent"
              >
                Cancel
              </Button>
              <Button type="submit" className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90" disabled={formik.isSubmitting || formik.isValidating || !formik.isValid}>
                {editingAccount ? "Update Account" : "Add Account"}
              </Button>
            </div>
          </form>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  )
}
