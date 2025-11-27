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
import { apiPost, apiPut } from "@/lib/api"

interface Account {
  id: string
  email: string
  password: string
  label: string
  lastChecked: string
  status: "idle" | "running" | "error" | "disabled" | "new"
  latestAutomation: string
}

interface AccountDrawerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  editingAccount?: Account | null
  onAccountSaved: () => void
}

export function AccountDrawer({ open, onOpenChange, editingAccount, onAccountSaved }: AccountDrawerProps) {
  const [showPassword, setShowPassword] = useState(false)
  const formik = useFormik({
    initialValues: {
      email: "",
      password: "",
      label: "",
    },
    validationSchema: accountSchema,
    onSubmit: async (values, { setSubmitting, resetForm }) => {
      try {
        if (editingAccount)
          await updateAccount()
        else
          await addAccount()

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

  useEffect(() => {
    if (editingAccount) {
      formik.setFieldValue("email", editingAccount.email)
      formik.setFieldValue("password", editingAccount.password)
      formik.setFieldValue("label", editingAccount.label)
    } else {
      formik.resetForm()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editingAccount])

  async function addAccount() {
    await apiPost("/accounts", {
      email: formik.values.email,
      password: formik.values.password,
      label: formik.values.label,
    })
  }

  async function updateAccount() {
    await apiPut(`/accounts/${editingAccount?.id}`, {
      password: formik.values.password,
      label: formik.values.label,
    })
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="bg-card border-border p-4">
        <SheetHeader>
          <SheetTitle className="text-foreground">
            {editingAccount ? "Edit Gmail Account" : "Add Gmail Account"}
          </SheetTitle>
          <SheetDescription className="text-muted-foreground">
            {editingAccount
              ? "Update account details. Password changes require re-authentication."
              : "Add a new Gmail account for automation. Credentials are encrypted at rest."}
          </SheetDescription>
        </SheetHeader>

        <Alert className="mt-4 border-border bg-accent/20">
          <Shield className="h-4 w-4" />
          <AlertDescription className="text-sm text-muted-foreground">
            <strong>Security:</strong> Passwords are encrypted using AES-256 and stored in a secure database. Consider
            using App Passwords for enhanced security.
          </AlertDescription>
        </Alert>

        <form onSubmit={formik.handleSubmit} className="space-y-6 mt-6">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-foreground">
              Email Address
            </Label>
            <Input
              id="email"
              type="email"
              value={formik.values.email}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              placeholder="user@gmail.com"
              className="bg-input border-border"
              disabled={!!editingAccount} // Disable email editing
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-foreground">
              Password {editingAccount && "(leave unchanged to keep current)"}
            </Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                value={formik.values.password}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                placeholder={editingAccount ? "••••••••" : "Enter password"}
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
          </div>

          <div className="space-y-2">
            <Label htmlFor="label" className="text-foreground">
              Label (Optional)
            </Label>
            <Input
              id="label"
              value={formik.values.label}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              placeholder="e.g., Primary, Marketing, Support"
              className="bg-input border-border"
              required={false}
            />
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
            <Button type="submit" className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90" disabled={formik.isSubmitting}>
              {editingAccount ? "Update Account" : "Add Account"}
            </Button>
          </div>
        </form>
      </SheetContent>
    </Sheet>
  )
}
