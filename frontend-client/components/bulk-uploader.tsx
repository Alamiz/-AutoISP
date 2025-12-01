"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Upload, Download, FileText } from "lucide-react"
import { apiPost } from "@/lib/api"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { toast } from "sonner"

interface BulkUploaderProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onAccountSaved: () => void
}

export function BulkUploader({ open, onOpenChange, onAccountSaved }: BulkUploaderProps) {
  const [dragActive, setDragActive] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [provider, setProvider] = useState<string>("gmx")
  const fileInputRef = useRef<HTMLInputElement>(null)

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

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first!");

    try {
      setLoading(true)

      const text = await file.text();

      // Parse file into accounts
      const lines = text.split(/\r?\n/).filter(line => line.trim());

      // Check if the first line is a header
      const hasHeader = lines[0].toLowerCase().includes("email,");

      // If header exists, skip it
      const dataLines = hasHeader ? lines.slice(1) : lines;

      // Parse file into accounts
      const accounts = dataLines.map(line => {
        const [email, password, recovery_email, number] = line.split(",").map(s => s.trim());
        return {
          email,
          provider,
          type: "desktop",
          credentials: {
            password,
            recovery_email: recovery_email || undefined,
            number: number || undefined
          }
        };
      });

      const response = await apiPost("/api/accounts/bulk-upload/", accounts);
      console.log("Upload response:", response);
      toast.success(`Successfully uploaded ${accounts.length} accounts.`)

      onOpenChange(false)
      setFile(null)
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
    onOpenChange(false)
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="bg-card border-border p-4">
        <SheetHeader>
          <SheetTitle className="text-foreground">Bulk Upload Accounts</SheetTitle>
          <SheetDescription className="text-muted-foreground">
            Upload multiple accounts via CSV file.
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-6 mt-6">
          {/* Provider Selection */}
          <div className="space-y-2">
            <Label>Default Provider</Label>
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger className="bg-input border-border">
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gmx">GMX</SelectItem>
                <SelectItem value="webde">WEB.DE</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              This provider will be applied to all uploaded accounts.
            </p>
          </div>

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
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={handleCancel}
              className="flex-1 border-border hover:bg-accent"
            >
              Cancel
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
      </SheetContent>
    </Sheet>
  )
}
