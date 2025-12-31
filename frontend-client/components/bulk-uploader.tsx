"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Upload, Download, FileText, Settings, ArrowRight, ArrowLeft } from "lucide-react"
import { apiPost } from "@/lib/api"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Slider } from "@/components/ui/slider"
import { toast } from "sonner"
import { useProvider } from "@/contexts/provider-context"

interface BulkUploaderProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onAccountSaved: () => void
}

export function BulkUploader({ open, onOpenChange, onAccountSaved }: BulkUploaderProps) {
  const [step, setStep] = useState<1 | 2>(1)
  const [dragActive, setDragActive] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Settings State
  const { selectedProvider } = useProvider()
  const [proxies, setProxies] = useState<string>("")
  const [mobilePercentage, setMobilePercentage] = useState<number>(0)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const downloadTemplate = () => {
    const csvContent =
      "email,password,recovery_email,number\nuser1@gmail.com,pass123,recovery1@example.com,1234567890\nuser2@gmail.com,pass456,,"
    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "accounts-template.csv"
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const parseProxies = (proxyText: string) => {
    return proxyText.split("\n")
      .map(p => p.trim())
      .filter(p => p.length > 0)
      .map(p => {
        // Simple parsing logic: host:port:user:pass or host:port
        const parts = p.split(":")
        if (parts.length >= 2) {
          return {
            host: parts[0],
            port: parseInt(parts[1]),
            username: parts[2] || undefined,
            password: parts[3] || undefined,
            protocol: "http" // Default to http
          }
        }
        return null
      })
      .filter(p => p !== null)
  }

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first!");

    try {
      setLoading(true)

      const text = await file.text();
      const lines = text.split(/\r?\n/).filter(line => line.trim());
      const hasHeader = lines[0].toLowerCase().includes("email,");
      const dataLines = hasHeader ? lines.slice(1) : lines;

      const proxyList = parseProxies(proxies)
      const totalAccounts = dataLines.length
      const mobileCount = Math.round(totalAccounts * (mobilePercentage / 100))

      const accounts = dataLines.map((line, index) => {
        const [email, password, recovery_email, number] = line.split(",").map(s => s.trim());

        // Assign Proxy (Round Robin)
        const proxy = proxyList.length > 0 ? proxyList[index % proxyList.length] : undefined

        // Assign Device Type
        // First N accounts get mobile, rest get desktop (simple distribution)
        const type = index < mobileCount ? "mobile" : "desktop"

        return {
          email,
          provider: selectedProvider?.name === "Web.de" ? "webde" : "gmx", // Use global provider
          type,
          credentials: {
            password,
            recovery_email: recovery_email || undefined,
            number: number || undefined
          },
          proxy_settings: proxy
        };
      });

      const response = await apiPost("/api/accounts/bulk-upload/", accounts);
      console.log("Upload response:", response);
      toast.success(`Successfully uploaded ${accounts.length} accounts.`)

      onOpenChange(false)
      setFile(null)
      setStep(1)
      setProxies("")
      setMobilePercentage(0)
      onAccountSaved()
    } catch (error) {
      console.error("Error uploading file:", error)
      toast.error("Error uploading file. Please check the format and try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setFile(null)
    setStep(1)
    onOpenChange(false)
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="bg-card border-border p-4 sm:max-w-md w-full">
        <SheetHeader>
          <SheetTitle className="text-foreground">Bulk Upload Accounts</SheetTitle>
          <SheetDescription className="text-muted-foreground">
            {step === 1 ? "Configure upload settings." : "Upload your accounts file."}
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-6 mt-6">
          {/* Progress Indicator */}
          <div className="flex items-center gap-2 mb-4">
            <div className={`h-2 flex-1 rounded-full ${step >= 1 ? "bg-primary" : "bg-accent"}`} />
            <div className={`h-2 flex-1 rounded-full ${step >= 2 ? "bg-primary" : "bg-accent"}`} />
          </div>

          {step === 1 && (
            <div className="space-y-6">
              <div className="space-y-2">
                <Label>Proxies (Optional)</Label>
                <Textarea
                  placeholder="host:port:username:password&#10;host:port"
                  className="bg-input border-border min-h-[150px] font-mono text-xs"
                  value={proxies}
                  onChange={(e) => setProxies(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  One proxy per line. Will be distributed round-robin.
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex justify-between">
                  <Label>Device Distribution</Label>
                  <span className="text-xs text-muted-foreground">
                    {mobilePercentage}% Mobile / {100 - mobilePercentage}% Desktop
                  </span>
                </div>
                <Slider
                  value={[mobilePercentage]}
                  onValueChange={(vals) => setMobilePercentage(vals[0])}
                  max={100}
                  step={1}
                  className="py-4"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  variant="outline"
                  onClick={handleCancel}
                  className="flex-1 border-border hover:bg-accent"
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => setStep(2)}
                  className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  Next <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              {/* Template Download */}
              <div className="p-4 rounded-lg border border-border bg-accent/20">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-foreground">CSV Template</h4>
                    <p className="text-xs text-muted-foreground">
                      Columns: email, password, recovery_email, number
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={downloadTemplate}
                    className="border-border hover:bg-accent bg-transparent"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
              </div>

              {/* File Upload Area */}
              <div
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${dragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                  }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.txt"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />

                {file ? (
                  <div className="space-y-2">
                    <FileText className="h-8 w-8 mx-auto text-primary" />
                    <p className="text-sm font-medium text-foreground">{file.name}</p>
                    <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="h-8 w-8 mx-auto text-muted-foreground" />
                    <p className="text-sm text-foreground">Drop your CSV or TXT file here, or click to browse</p>
                    <p className="text-xs text-muted-foreground">Supports files up to 10MB</p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setStep(1)}
                  className="flex-1 border-border hover:bg-accent"
                >
                  <ArrowLeft className="mr-2 h-4 w-4" /> Back
                </Button>
                <Button
                  onClick={handleUpload}
                  disabled={!file || loading}
                  className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  {loading ? "Uploading..." : "Upload Accounts"}
                </Button>
              </div>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}
