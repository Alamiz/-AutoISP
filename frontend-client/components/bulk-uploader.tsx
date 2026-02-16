"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Upload, Download, FileText, ArrowRight, ArrowLeft, CheckCircle, XCircle, Trash2 } from "lucide-react"
import { apiPost, ApiError } from "@/lib/api"
import { toast } from "sonner"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useProvider } from "@/contexts/provider-context"

interface BulkUploaderProps {
  mode: "accounts" | "proxies"
  open: boolean
  onOpenChange: (open: boolean) => void
  onUploadSuccess: () => void
}

interface ParsedItem {
  id: string
  data: any
  raw: string
  valid: boolean
  error?: string
  selected: boolean
}

export function BulkUploader({ mode, open, onOpenChange, onUploadSuccess }: BulkUploaderProps) {
  const { selectedProvider } = useProvider()
  const [step, setStep] = useState<1 | 2>(1)
  const [activeTab, setActiveTab] = useState<"file" | "paste">("file")
  const [dragActive, setDragActive] = useState(false)

  // Input State
  const [file, setFile] = useState<File | null>(null)
  const [pastedText, setPastedText] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Parsed Data State
  const [items, setItems] = useState<ParsedItem[]>([])
  const [loading, setLoading] = useState(false)

  // Reset state on open/close
  useEffect(() => {
    if (!open) {
      setTimeout(() => {
        setStep(1)
        setFile(null)
        setPastedText("")
        setItems([])
      }, 300)
    }
  }, [open])

  // --------------------------------------------------------------------------
  // STEP 1: Input Handling (File / Paste)
  // --------------------------------------------------------------------------

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
    let content = ""
    let filename = ""

    if (mode === "accounts") {
      content = "user1@gmx.net,pass123,rec@gmail.com,1234567890\nuser2@web.de,pass456,,"
      filename = "accounts.txt"
    } else {
      content = "192.168.1.1:8080:user:pass\n10.0.0.1:3128"
      filename = "proxies.txt"
    }

    const blob = new Blob([content], { type: "text/plain" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const handleParse = async () => {
    let rawContent = ""
    if (activeTab === "file") {
      if (!file) {
        toast.error("Please select a file first")
        return
      }
      rawContent = await file.text()
    } else {
      if (!pastedText.trim()) {
        toast.error("Please paste content first")
        return
      }
      rawContent = pastedText
    }

    const lines = rawContent.split(/\r?\n/).filter(line => line.trim())
    const parsed: ParsedItem[] = []

    // Check for header row to skip
    let startingIndex = 0
    if (lines.length > 0) {
      const firstLine = lines[0].toLowerCase()
      if (mode === "accounts" && firstLine.includes("email")) startingIndex = 1
      if (mode === "proxies" && firstLine.includes("ip")) startingIndex = 1
    }

    const dataLines = lines.slice(startingIndex)

    dataLines.forEach((line, idx) => {
      // Use index as ID for stability
      const id = `item-${idx}`

      if (mode === "accounts") {
        const item = parseAccountLine(line, id)
        if (item) parsed.push(item)
      } else {
        const item = parseProxyLine(line, id)
        if (item) parsed.push(item)
      }
    })

    if (parsed.length === 0) {
      toast.error("No data found to parse")
      return
    }

    setItems(parsed)
    setStep(2)
  }

  // --------------------------------------------------------------------------
  // Parsing Logic
  // --------------------------------------------------------------------------

  const parseAccountLine = (line: string, id: string): ParsedItem => {
    // Format: email, password, recovery, phone
    const parts = line.split(",").map(s => s.trim())

    // Validations
    let valid = true
    let error = ""

    if (parts.length < 2) {
      valid = false
      error = "Missing parts (need email, password)"
    } else if (!parts[0].includes("@")) {
      valid = false
      error = "Invalid email format"
    }

    return {
      id,
      raw: line,
      valid,
      error,
      selected: valid,
      data: {
        email: parts[0],
        password: parts[1],
        provider: selectedProvider?.slug || "gmx", // Use global provider
        recovery_email: parts[2] || undefined,
        phone_number: parts[3] || undefined,
        status: "unknown"
      }
    }
  }

  const parseProxyLine = (line: string, id: string): ParsedItem => {
    // Format: ip:port:user:pass OR comma separated
    const splitter = line.includes(":") ? ":" : ","
    const parts = line.split(splitter).map(s => s.trim())

    let valid = true
    let error = ""
    const ip = parts[0]
    const port = parseInt(parts[1])

    if (parts.length < 2) {
      valid = false
      error = "Missing parts (need ip, port)"
    } else if (isNaN(port)) {
      valid = false
      error = "Invalid port number"
    }
    // Basic IP Check (IPv4 + localhost)
    else if (!/^(\d{1,3}\.){3}\d{1,3}$/.test(ip)) {
      if (ip !== "localhost") {
        valid = false
        error = "Invalid IP format"
      }
    }

    return {
      id,
      raw: line,
      valid,
      error,
      selected: valid,
      data: {
        ip: parts[0],
        port: port,
        username: parts[2] || undefined,
        password: parts[3] || undefined
      }
    }
  }

  // --------------------------------------------------------------------------
  // STEP 2: Preview & Actions
  // --------------------------------------------------------------------------

  const toggleSelection = (id: string) => {
    setItems(prev => prev.map(item =>
      item.id === id ? { ...item, selected: !item.selected } : item
    ))
  }

  const toggleAll = (checked: boolean) => {
    setItems(prev => prev.map(item =>
      item.valid ? { ...item, selected: checked } : item
    ))
  }

  const removeItem = (id: string) => {
    setItems(prev => prev.filter(item => item.id !== id))
  }

  const handleUpload = async () => {
    const toUpload = items.filter(i => i.selected && i.valid).map(i => i.data)

    if (toUpload.length === 0) {
      toast.error("No valid items selected for upload")
      return
    }

    setLoading(true)
    try {
      const endpoint = mode === "accounts"
        ? "/accounts/bulk-upsert"
        : "/proxies/bulk-upsert"

      const response = await apiPost(endpoint, toUpload, "local")

      // @ts-ignore
      const count = (response.created_ids?.length || 0) + (response.existing_ids?.length || 0)
      toast.success(`Successfully uploaded ${count} items`)

      onUploadSuccess()
      onOpenChange(false)
    } catch (error) {
      console.error("Upload error:", error)
      if (error instanceof ApiError) {
        toast.error(error.message)
      } else {
        toast.error("Upload failed")
      }
    } finally {
      setLoading(false)
    }
  }

  const validCount = items.filter(i => i.valid).length
  const invalidCount = items.filter(i => !i.valid).length
  const selectedCount = items.filter(i => i.selected).length

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="bg-card border-border p-0 sm:max-w-xl w-full flex flex-col h-full">
        <SheetHeader className="px-6 py-4 border-b border-border">
          <div className="flex justify-between items-start pr-8">
            <div>
              <SheetTitle>Bulk Upload {mode === "accounts" ? "Accounts" : "Proxies"}</SheetTitle>
              <SheetDescription>
                {step === 1 ? "Import your data." : "Review and upload."}
              </SheetDescription>
            </div>
            {mode === "accounts" && selectedProvider && (
              <Badge variant="secondary" className="mt-1">
                Target: {selectedProvider.name}
              </Badge>
            )}
          </div>
        </SheetHeader>

        <div className="flex-1 overflow-hidden flex flex-col p-6">
          {step === 1 ? (
            <div className="h-full flex flex-col space-y-6">
              <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)} className="w-full flex-1 flex flex-col">
                <TabsList className="grid w-full grid-cols-2 mb-4">
                  <TabsTrigger value="file">Upload File</TabsTrigger>
                  <TabsTrigger value="paste">Paste Text</TabsTrigger>
                </TabsList>

                <TabsContent value="file" className="flex-1 flex flex-col space-y-4">
                  <div className="p-4 rounded-lg border border-border bg-accent/20">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium">Template</h4>
                        <p className="text-xs text-muted-foreground">
                          {mode === "accounts" ? "email, password, recovery..." : "ip, port, username, password"}
                        </p>
                      </div>
                      <Button variant="outline" size="sm" onClick={downloadTemplate}>
                        <Download className="h-4 w-4 mr-2" /> Download
                      </Button>
                    </div>
                  </div>

                  <div
                    className={`flex-1 relative border-2 border-dashed rounded-lg p-8 text-center transition-colors flex flex-col items-center justify-center ${dragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
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
                      <div className="space-y-4">
                        <FileText className="h-12 w-12 mx-auto text-primary" />
                        <div>
                          <p className="text-lg font-medium">{file.name}</p>
                          <p className="text-sm text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                        <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setFile(null) }}>
                          Remove File
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <Upload className="h-12 w-12 mx-auto text-muted-foreground" />
                        <div>
                          <p className="text-lg font-medium">Drop file here</p>
                          <p className="text-sm text-muted-foreground">or click to browse</p>
                        </div>
                      </div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="paste" className="flex flex-col h-auto">
                  <div className="mb-2 text-xs text-muted-foreground shrink-0">
                    {mode === "accounts" ? (
                      <span>Format: <code>email, password, [recovery], [phone]</code></span>
                    ) : (
                      <span>Format: <code>ip:port:user:pass</code> or <code>ip,port,user,pass</code></span>
                    )}
                  </div>

                  <Textarea
                    value={pastedText}
                    onChange={(e) => setPastedText(e.target.value)}
                    placeholder={mode === "accounts"
                      ? "user1@example.com,pass123\nuser2@example.com,pass456,rec@gmail.com"
                      : "192.168.1.1:8080:user:pass\n10.0.0.1:3128"}
                    className="w-full font-mono text-sm resize-y overflow-y-auto h-[calc(100vh-300px)]"
                  />
                </TabsContent>
              </Tabs>

              <div className="flex gap-3 pt-2">
                <Button variant="outline" onClick={() => onOpenChange(false)} className="flex-1">Cancel</Button>
                <Button onClick={handleParse} disabled={activeTab === "file" ? !file : !pastedText.trim()} className="flex-1">
                  Preview <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>
          ) : (
            // STEP 2: PREVIEW
            <div className="h-full flex flex-col space-y-4">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50 dark:bg-green-900/20">
                    {validCount} Valid
                  </Badge>
                  {invalidCount > 0 && (
                    <Badge variant="outline" className="text-red-600 border-red-200 bg-red-50 dark:bg-red-900/20">
                      {invalidCount} Invalid
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox
                    id="select-all"
                    checked={selectedCount === validCount && validCount > 0}
                    onCheckedChange={(c) => toggleAll(!!c)}
                    disabled={validCount === 0}
                  />
                  <label htmlFor="select-all" className="cursor-pointer font-medium">Select Valid</label>
                </div>
              </div>

              <div className="border border-border rounded-lg overflow-hidden flex flex-col h-[calc(100vh-320px)]">
                <div className="grid grid-cols-[auto_1fr_auto] gap-4 p-3 bg-muted/50 border-b border-border text-xs font-medium text-muted-foreground uppercase sticky top-0">
                  <div className="w-8"></div>
                  <div>Data</div>
                  <div className="text-center">Status</div>
                </div>
                <div className="overflow-y-auto flex-1 min-h-0">
                  <div className="divide-y divide-border">
                    {[...items]
                      .sort((a, b) => (a.valid === b.valid ? 0 : a.valid ? 1 : -1))
                      .map((item) => (
                        <div key={item.id} className={`grid grid-cols-[auto_1fr_auto] gap-4 p-3 items-center group transition-colors ${!item.valid ? "bg-red-50/50 dark:bg-red-900/10" : ""}`}>
                          <div className="flex items-center justify-center w-8">
                            {item.valid ? (
                              <Checkbox
                                checked={item.selected}
                                onCheckedChange={() => toggleSelection(item.id)}
                              />
                            ) : (
                              <XCircle className="h-4 w-4 text-red-500" />
                            )}
                          </div>
                          <div className="font-mono text-sm break-all">
                            {mode === "accounts" ? (
                              <div className="flex flex-col">
                                <span className="font-medium">{item.data.email}</span>
                                <span className="text-xs text-muted-foreground">{item.data.provider}</span>
                              </div>
                            ) : (
                              <div className="flex flex-col">
                                <span className="font-medium">{item.data.ip}:{item.data.port}</span>
                                {item.data.username && <span className="text-xs text-muted-foreground">User: {item.data.username}</span>}
                              </div>
                            )}
                            {!item.valid && <p className="text-xs text-red-500 mt-1">{item.error}</p>}
                          </div>

                          <div className="flex items-center gap-2">
                            {item.valid ? (
                              <CheckCircle className="h-4 w-4 text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                            ) : null}
                            <Button variant="ghost" size="icon" className="h-6 w-6 text-muted-foreground hover:text-destructive" onClick={() => removeItem(item.id)}>
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <Button variant="outline" onClick={() => setStep(1)} className="flex-1">
                  <ArrowLeft className="mr-2 h-4 w-4" /> Back to Input
                </Button>
                <Button onClick={handleUpload} disabled={selectedCount === 0 || loading} className="flex-1">
                  {loading ? "Uploading..." : `Upload ${selectedCount} Items`}
                </Button>
              </div>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}
