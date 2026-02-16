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
import { toast } from "sonner"
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

  const formik = useFormik({
    initialValues: {
      email: "",
      password: "",
      provider: defaultProvider,
      recovery_email: "",
      number: "",
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
        toast.error("Failed to save account")
      } finally {
        setSubmitting(false);
      }
    }
  })

  // Initialize form when editing or opening
  useEffect(() => {
    if (editingAccount) {
      formik.setValues({
        email: editingAccount.email || "",
        password: editingAccount.credentials?.password || "",
        provider: editingAccount.provider || "gmx",
        recovery_email: editingAccount.credentials?.recovery_email || "",
        number: editingAccount.credentials?.number || "",
      })
    } else {
      formik.resetForm()
      const currentProvider = globalProvider?.name === "Web.de" ? "webde" : "gmx"
      formik.setFieldValue("provider", currentProvider)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editingAccount, open])

  async function addAccount(values: any) {
    await apiPost("/accounts", {
      email: values.email,
      password: values.password,
      provider: values.provider,
      recovery_email: values.recovery_email || undefined,
      phone_number: values.number || undefined,
      status: "unknown"
    }, "local")
  }

  async function updateAccount(values: any) {
    await apiPatch(`/accounts/${editingAccount?.id}`, {
      password: values.password,
      recovery_email: values.recovery_email || undefined,
      phone_number: values.number || undefined,
    }, "local")
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
          <form onSubmit={formik.handleSubmit} className="space-y-6 pb-6 p-2">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  {...formik.getFieldProps("email")}
                  disabled={!!editingAccount}
                  className="bg-input border-border"
                  placeholder="example@gmx.de"
                />
                {formik.touched.email && formik.errors.email && (
                  <div className="text-red-500 text-xs">{formik.errors.email as string}</div>
                )}
              </div>

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
                  <div className="text-red-500 text-xs">{formik.errors.password as string}</div>
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
                  <div className="text-red-500 text-xs">{formik.errors.recovery_email as string}</div>
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
