"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Play, Settings, Clock, Zap, Mail, Archive, Paperclip, Shield, Search, FlaskConical, Loader2, Calendar as CalendarIcon, RotateCw } from "lucide-react"
import { AutomationScheduler } from "./automation-scheduler"
import { apiPost } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { useAccounts } from "@/hooks/useAccounts"
import { useProvider } from "@/contexts/provider-context"
import { useJobs } from "@/contexts/jobs-context"
import { automations } from "@/data/automations"
import { Automation } from "@/lib/types"
import { format } from "date-fns"
import { cn } from "@/lib/utils"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

export function AutomationControls() {
  const { selectedProvider: globalProvider } = useProvider()
  // Map global provider name to automation provider key
  const selectedProviderKey = globalProvider?.name === "Web.de" ? "webde" : "gmx"

  const [availableAutomations, setAvailableAutomations] = useState<Automation[]>([])
  const [selectedAutomations, setSelectedAutomations] = useState<string[]>([])
  const [scheduleType, setScheduleType] = useState<"now" | "later">("now")
  const [showScheduler, setShowScheduler] = useState(false)
  const [automationParams, setAutomationParams] = useState<Record<string, Record<string, any>>>({})
  const [activeTab, setActiveTab] = useState("select")

  const { selectedAccounts, clearSelection, getSelectedCount, statusFilter } = useAccounts()
  const queryClient = useQueryClient()
  const { busyAccountIds } = useJobs()
  const availableAccounts = selectedAccounts.filter(acc => !busyAccountIds.has(String(acc.id)))
  const busyAccounts = selectedAccounts.filter(acc => busyAccountIds.has(String(acc.id)))

  // Update available automations when provider changes
  useEffect(() => {
    const filtered = automations.filter(a => a.provider === selectedProviderKey)
    setAvailableAutomations(filtered)

    // Clear selections when switching providers
    setSelectedAutomations([])
    setAutomationParams({})
    setActiveTab("select")
  }, [selectedProviderKey])

  const handleAutomationToggle = (automationId: string, checked: boolean) => {
    if (checked) {
      setSelectedAutomations([...selectedAutomations, automationId])
    } else {
      setSelectedAutomations(selectedAutomations.filter((id) => id !== automationId))
      const newParams = { ...automationParams }
      delete newParams[automationId]
      setAutomationParams(newParams)
    }
  }

  const handleParameterChange = (automationId: string, paramKey: string, value: any) => {
    setAutomationParams((prev) => ({
      ...prev,
      [automationId]: {
        ...prev[automationId],
        [paramKey]: value,
      },
    }))
  }

  const getCategoryIcon = (category: Automation["category"]) => {
    switch (category) {
      case "Email":
        return <Mail className="h-4 w-4" />
      case "Auth":
        return <Shield className="h-4 w-4" />
      case "Maintenance":
        return <Settings className="h-4 w-4" />
      case "Browsing":
        return <Search className="h-4 w-4" />
      case "Test":
        return <FlaskConical className="h-4 w-4" />
      default:
        return <Zap className="h-4 w-4" />
    }
  }

  const getCategoryColor = (category: Automation["category"]) => {
    switch (category) {
      case "Email":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20"
      case "Auth":
        return "bg-green-500/10 text-green-400 border-green-500/20"
      case "Maintenance":
        return "bg-orange-500/10 text-orange-400 border-orange-500/20"
      case "Browsing":
        return "bg-sky-500/10 text-sky-400 border-sky-500/20"
      case "Test":
        return "bg-pink-500/10 text-pink-400 border-pink-500/20"
      default:
        return "bg-gray-500/10 text-gray-400 border-gray-500/20"
    }
  }

  const runAutomations = useMutation({
    mutationFn: async ({ automationId, automation }: { automationId: string, automation: Automation }) => {
      return await apiPost('/automations/run', {
        automation_id: automation.id,
        parameters: automationParams[automationId] || {},
        account_ids: availableAccounts.map(acc => acc.id),
      },
        "local"
      )
    },
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["accounts"] })
    },
    onError: (err, variables) => {
      console.error(`Error running automation ${variables.automation.name}:`, err)
      toast.error(`Failed to run ${variables.automation.name}`)
    },
    onSuccess: (data, variables) => {
      toast.success(`Successfully ran ${variables.automation.name}`)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] })
    },
  })

  const runSequentialAutomations = useMutation({
    mutationFn: async ({ automationId, automation }: { automationId: string, automation: Automation }) => {
      return await apiPost('/automations/run-sequential', {
        automation_id: automation.id,
        parameters: automationParams[automationId] || {},
        account_ids: availableAccounts.map(acc => acc.id),
      },
        "local"
      )
    },
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["accounts"] })
    },
    onError: (err, variables) => {
      console.error(`Error running sequential automation ${variables.automation.name}:`, err)
      toast.error(`Failed to run sequential ${variables.automation.name}`)
    },
    onSuccess: (data, variables) => {
      toast.success(`Sequential run completed: ${variables.automation.name}`)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] })
      queryClient.invalidateQueries({ queryKey: ["activities"] })
    },
  })

  const handleRunAutomations = async () => {
    if (scheduleType === "later") {
      setShowScheduler(true)
    } else {
      for (const automationId of selectedAutomations) {
        const automation = availableAutomations.find(a => a.id === automationId)
        if (automation) {
          try {
            await runAutomations.mutateAsync({ automationId, automation })
          } catch (error) {
            console.error(`Error running automation ${automation.name}:`, error)
          }
        }
      }
      clearSelection();
    }
  }

  const handleRunSequential = async () => {
    for (const automationId of selectedAutomations) {
      const automation = availableAutomations.find(a => a.id === automationId)
      if (automation) {
        try {
          await runSequentialAutomations.mutateAsync({ automationId, automation })
        } catch (error) {
          console.error(`Error running sequential automation ${automation.name}:`, error)
        }
      }
    }
    clearSelection();
  }

  const selectedAutomationObjects = availableAutomations.filter((automation) =>
    selectedAutomations.includes(automation.id),
  )

  const hasRequiredParams = selectedAutomationObjects.every((automation) => {
    const params = automation.params || []
    const userParams = automationParams[automation.id] || {}

    return params.every((param) => {
      if (param.required) {
        return userParams[param.name] && userParams[param.name].toString().trim() !== ""
      }
      return true
    })
  })

  const isRunning = runAutomations.isPending || runSequentialAutomations.isPending

  return (
    <>
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Automation Controls</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="grid w-full grid-cols-3 bg-muted">
              <TabsTrigger value="select">Select</TabsTrigger>
              <TabsTrigger value="configure" disabled={selectedAutomations.length === 0}>
                Configure
              </TabsTrigger>
              <TabsTrigger value="run" disabled={selectedAutomations.length === 0}>
                Run
              </TabsTrigger>
            </TabsList>

            {/* Automation Selection */}
            <TabsContent value="select" className="space-y-4">
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-foreground">Available Automations</h4>
                <div className="space-y-2">
                  {availableAutomations.map((automation) => (
                    <div
                      key={automation.id}
                      className="flex items-start gap-3 p-3 rounded-lg hover:bg-accent/30 border border-border"
                    >
                      <Checkbox
                        checked={selectedAutomations.includes(automation.id)}
                        onCheckedChange={(checked) => handleAutomationToggle(automation.id, !!checked)}
                        className="mt-1"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="flex items-center gap-1">
                            {getCategoryIcon(automation.category)}
                            <span className="text-sm font-medium text-foreground">{automation.name}</span>
                          </div>
                          <Badge className={getCategoryColor(automation.category)}>{automation.category}</Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mb-1">{automation.description}</p>
                      </div>
                    </div>
                  ))}
                  {availableAutomations.length === 0 && (
                    <p className="text-sm text-muted-foreground text-center py-4">No automations available for this provider.</p>
                  )}
                </div>
              </div>
            </TabsContent>

            {/* Parameter Configuration */}
            <TabsContent value="configure" className="space-y-4">
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-foreground">Configure Parameters</h4>
                {selectedAutomationObjects.map((automation) => {
                  const params = automation.params || []
                  const hasParams = params.length > 0

                  return (
                    <div key={automation.id} className="p-4 rounded-lg border border-border bg-accent/20">
                      <div className="flex items-center gap-2 mb-3">
                        {getCategoryIcon(automation.category)}
                        <h5 className="font-medium text-foreground">{automation.name}</h5>
                      </div>

                      {hasParams ? (
                        <div className="space-y-3">
                          {params.map((param) => (
                            <div key={param.name} className="space-y-1">
                              <Label className="text-sm text-foreground">
                                {param.label}
                                {param.required && <span className="text-red-400 ml-1">*</span>}
                              </Label>
                              {param.type === "date" ? (
                                <Popover>
                                  <PopoverTrigger asChild>
                                    <Button
                                      variant={"outline"}
                                      className={cn(
                                        "w-full justify-start text-left font-normal bg-input border-border",
                                        !automationParams[automation.id]?.[param.name] && "text-muted-foreground"
                                      )}
                                    >
                                      <CalendarIcon className="mr-2 h-4 w-4" />
                                      {automationParams[automation.id]?.[param.name] ? (
                                        format(new Date(automationParams[automation.id]?.[param.name]), "PPP")
                                      ) : (
                                        <span>Pick a date</span>
                                      )}
                                    </Button>
                                  </PopoverTrigger>
                                  <PopoverContent className="w-auto p-0" align="start">
                                    <Calendar
                                      mode="single"
                                      selected={automationParams[automation.id]?.[param.name] ? new Date(automationParams[automation.id]?.[param.name]) : undefined}
                                      onSelect={(date) => handleParameterChange(automation.id, param.name, date ? format(date, "yyyy-MM-dd") : "")}
                                      initialFocus
                                    />
                                  </PopoverContent>
                                </Popover>
                              ) : param.type === "file" ? (
                                <Input
                                  type="file"
                                  accept={param.accept || "*"}
                                  onChange={(e) => {
                                    const file = e.target.files?.[0];
                                    if (file) {
                                      const filePath = (file as any).path;
                                      if (filePath) {
                                        handleParameterChange(automation.id, param.name, filePath);
                                      } else {
                                        const reader = new FileReader();
                                        reader.onload = () => {
                                          handleParameterChange(automation.id, param.name, reader.result as string);
                                        };
                                        reader.readAsDataURL(file);
                                      }
                                    }
                                  }}
                                  className="bg-input border-border"
                                />
                              ) : (
                                <Input
                                  type={param.type}
                                  value={automationParams[automation.id]?.[param.name] || ""}
                                  onChange={(e) => handleParameterChange(automation.id, param.name, e.target.value)}
                                  placeholder={param.placeholder || `Enter ${param.label.toLowerCase()}`}
                                  className="bg-input border-border"
                                />
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">No configuration required</p>
                      )}
                    </div>
                  )
                })}
              </div>
            </TabsContent>

            {/* Run Configuration */}
            <TabsContent value="run" className="space-y-4">
              <div className="space-y-4">
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-foreground">Execution Summary</h4>
                  <div className="p-3 rounded-lg border border-border bg-accent/20">
                    <p className="text-sm text-foreground mb-2">
                      Provider: <span className="font-medium capitalize">{selectedProviderKey}</span>
                    </p>
                    <p className="text-sm text-foreground mb-2">
                      {selectedAutomations.length} automation{selectedAutomations.length > 1 ? "s" : ""} selected
                    </p>
                    <div className="space-y-1">
                      {selectedAutomationObjects.map((automation) => (
                        <div key={automation.id} className="flex items-center gap-2 text-xs text-muted-foreground">
                          {getCategoryIcon(automation.category)}
                          <span>{automation.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 pt-4">
                  <Button
                    className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                    disabled={!hasRequiredParams || getSelectedCount() === 0 || isRunning}
                    onClick={handleRunAutomations}
                  >
                    {runAutomations.isPending ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4 mr-2" />
                    )}
                    {runAutomations.isPending ? "Submitting..." : (scheduleType === "now" ? "Run Now" : "Schedule")}
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1 border-border hover:bg-accent"
                    disabled={!hasRequiredParams || getSelectedCount() === 0 || isRunning}
                    onClick={handleRunSequential}
                  >
                    {runSequentialAutomations.isPending ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <RotateCw className="h-4 w-4 mr-2" />
                    )}
                    {runSequentialAutomations.isPending ? "Running..." : "Run Sequential"}
                  </Button>
                </div>

                {!hasRequiredParams && (
                  <p className="text-sm text-red-400">* Please fill in all required parameters in the Configure tab.</p>
                )}
                {getSelectedCount() === 0 && (
                  <p className="text-sm text-red-400">* Please select accounts in order to start automations.</p>
                )}
                {busyAccounts.length > 0 && (
                  <p className="text-sm text-orange-400">
                    * {busyAccounts.length} account(s) already have running/queued jobs and will be skipped.
                  </p>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <AutomationScheduler
        open={showScheduler}
        onOpenChange={setShowScheduler}
        selectedAutomations={selectedAutomationObjects}
        parameters={automationParams}
      />
    </>
  )
}