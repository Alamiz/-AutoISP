"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Play, Settings, Clock, Zap, Mail, Archive, Paperclip, Shield, Search, FlaskConical } from "lucide-react"
import { AutomationScheduler } from "./automation-scheduler"
import type { Automation } from "@/lib/types"
import { apiPost } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { useAccounts } from "@/hooks/useAccounts"
import { useProvider } from "@/contexts/provider-context"
import { gmxAutomations, webdeAutomations } from "@/data/automations"

// Map provider names to their automation lists
const automationsByProvider = {
  gmx: gmxAutomations,
  webde: webdeAutomations,
}

export function AutomationControls() {
  const { selectedProvider: globalProvider } = useProvider()
  const selectedProvider = globalProvider?.name === "Web.de" ? "webde" : "gmx"

  const [availableAutomations, setAvailableAutomations] = useState<Automation[]>(gmxAutomations)
  const [selectedAutomations, setSelectedAutomations] = useState<string[]>([])
  const [scheduleType, setScheduleType] = useState<"now" | "later">("now")
  const [showScheduler, setShowScheduler] = useState(false)
  const [automationParams, setAutomationParams] = useState<Record<string, Record<string, any>>>({})
  const [activeTab, setActiveTab] = useState("select")

  const { selectedAccounts, setSelectedAccounts } = useAccounts()
  const queryClient = useQueryClient()

  // Update available automations when provider changes
  useEffect(() => {
    setAvailableAutomations(automationsByProvider[selectedProvider])
    // Clear selections when switching providers
    setSelectedAutomations([])
    setAutomationParams({})
    setActiveTab("select")
  }, [selectedProvider])

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
      case "email":
        return <Mail className="h-4 w-4" />
      case "inbox":
        return <Archive className="h-4 w-4" />
      case "attachments":
        return <Paperclip className="h-4 w-4" />
      case "maintenance":
        return <Shield className="h-4 w-4" />
      case "browsing":
        return <Search className="h-4 w-4" />
      case "test":
        return <FlaskConical className="h-4 w-4" />
      default:
        return <Zap className="h-4 w-4" />
    }
  }

  const getCategoryColor = (category: Automation["category"]) => {
    switch (category) {
      case "email":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20"
      case "inbox":
        return "bg-green-500/10 text-green-400 border-green-500/20"
      case "attachments":
        return "bg-purple-500/10 text-purple-400 border-purple-500/20"
      case "maintenance":
        return "bg-orange-500/10 text-orange-400 border-orange-500/20"
      case "browsing":
        return "bg-sky-500/10 text-sky-400 border-sky-500/20"
      case "test":
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
        account_ids: selectedAccounts.map(acc => acc.id),
        provider: selectedProvider,
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
      setSelectedAccounts([]);
    }
  }

  const selectedAutomationObjects = availableAutomations.filter((automation) =>
    selectedAutomations.includes(automation.id),
  )

  const hasRequiredParams = selectedAutomationObjects.every((automation) => {
    const params = automation.parameters || {}
    const userParams = automationParams[automation.id] || {}

    return Object.entries(params).every(([key, config]) => {
      if (config.required) {
        return userParams[key] && userParams[key].toString().trim() !== ""
      }
      return true
    })
  })

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
                        <div className="flex items-center gap-2">
                          <Clock className="h-3 w-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">{automation.estimatedDuration}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>

            {/* Parameter Configuration */}
            <TabsContent value="configure" className="space-y-4">
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-foreground">Configure Parameters</h4>
                {selectedAutomationObjects.map((automation) => {
                  const params = automation.parameters || {}
                  const hasParams = Object.keys(params).length > 0

                  return (
                    <div key={automation.id} className="p-4 rounded-lg border border-border bg-accent/20">
                      <div className="flex items-center gap-2 mb-3">
                        {getCategoryIcon(automation.category)}
                        <h5 className="font-medium text-foreground">{automation.name}</h5>
                      </div>

                      {hasParams ? (
                        <div className="space-y-3">
                          {Object.entries(params).map(([paramKey, config]) => (
                            <div key={paramKey} className="space-y-1">
                              <Label className="text-sm text-foreground">
                                {config.label}
                                {config.required && <span className="text-red-400 ml-1">*</span>}
                              </Label>
                              {config.type === "textarea" ? (
                                <Textarea
                                  value={automationParams[automation.id]?.[paramKey] || ""}
                                  onChange={(e) => handleParameterChange(automation.id, paramKey, e.target.value)}
                                  placeholder={`Enter ${config.label.toLowerCase()}`}
                                  className="bg-input border-border"
                                  rows={3}
                                />
                              ) : config.type === "number" ? (
                                <Input
                                  type="number"
                                  value={automationParams[automation.id]?.[paramKey] || ""}
                                  onChange={(e) => handleParameterChange(automation.id, paramKey, e.target.value)}
                                  placeholder={`Enter ${config.label.toLowerCase()}`}
                                  className="bg-input border-border"
                                />
                              ) : (
                                <Input
                                  value={automationParams[automation.id]?.[paramKey] || ""}
                                  onChange={(e) => handleParameterChange(automation.id, paramKey, e.target.value)}
                                  placeholder={`Enter ${config.label.toLowerCase()}`}
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
                      Provider: <span className="font-medium capitalize">{selectedProvider}</span>
                    </p>
                    <p className="text-sm text-foreground mb-2">
                      {selectedAutomations.length} automation{selectedAutomations.length > 1 ? "s" : ""} selected
                    </p>
                    <div className="space-y-1">
                      {selectedAutomationObjects.map((automation) => (
                        <div key={automation.id} className="flex items-center gap-2 text-xs text-muted-foreground">
                          {getCategoryIcon(automation.category)}
                          <span>{automation.name}</span>
                          <span>({automation.estimatedDuration})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-foreground">Schedule</h4>
                  <Select value={scheduleType} onValueChange={(value: "now" | "later") => setScheduleType(value)}>
                    <SelectTrigger className="bg-input border-border">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="now">Run Now</SelectItem>
                      <SelectItem value="later">Schedule for Later</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex gap-2 pt-4">
                  <Button
                    className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                    disabled={!hasRequiredParams || selectedAccounts.length === 0}
                    onClick={handleRunAutomations}
                  >
                    <Play className="h-4 w-4 mr-2" />
                    {scheduleType === "now" ? "Run Now" : "Schedule"}
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    className="border-border hover:bg-accent bg-transparent"
                    disabled={selectedAccounts.length === 0}
                  >
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>

                {!hasRequiredParams && (
                  <p className="text-sm text-red-400">* Please fill in all required parameters in the Configure tab.</p>
                )}
                {selectedAccounts.length === 0 && (
                  <p className="text-sm text-red-400">* Please select accounts in order to start automations.</p>
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