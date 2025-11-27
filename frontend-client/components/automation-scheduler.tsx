"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Calendar, Clock, Repeat } from "lucide-react"
import type { Automation } from "@/lib/types"

interface AutomationSchedulerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  selectedAutomations: Automation[]
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  parameters: Record<string, Record<string, any>>
}

export function AutomationScheduler({ open, onOpenChange, selectedAutomations, parameters }: AutomationSchedulerProps) {
  const [scheduleType, setScheduleType] = useState<"once" | "recurring">("once")
  const [scheduledDate, setScheduledDate] = useState("")
  const [scheduledTime, setScheduledTime] = useState("")
  const [recurringPattern, setRecurringPattern] = useState<"daily" | "weekly" | "monthly">("daily")
  const [recurringDays, setRecurringDays] = useState<string[]>([])
  const [endDate, setEndDate] = useState("")

  const daysOfWeek = [
    { value: "monday", label: "Mon" },
    { value: "tuesday", label: "Tue" },
    { value: "wednesday", label: "Wed" },
    { value: "thursday", label: "Thu" },
    { value: "friday", label: "Fri" },
    { value: "saturday", label: "Sat" },
    { value: "sunday", label: "Sun" },
  ]

  const handleDayToggle = (day: string, checked: boolean) => {
    if (checked) {
      setRecurringDays([...recurringDays, day])
    } else {
      setRecurringDays(recurringDays.filter((d) => d !== day))
    }
  }

  const handleSchedule = () => {
    const scheduleData = {
      type: scheduleType,
      automations: selectedAutomations.map((a) => a.id),
      parameters,
      schedule: {
        date: scheduledDate,
        time: scheduledTime,
        ...(scheduleType === "recurring" && {
          pattern: recurringPattern,
          days: recurringDays,
          endDate,
        }),
      },
    }

    console.log("Scheduling automations:", scheduleData)
    onOpenChange(false)
  }

  // Get current date and time for min values
  const now = new Date()
  const currentDate = now.toISOString().split("T")[0]
  // const currentTime = now.toTimeString().slice(0, 5)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl bg-card border-border">
        <DialogHeader>
          <DialogTitle className="text-foreground">Schedule Automations</DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Configure when and how often to run the selected automations.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Selected Automations Summary */}
          <div className="p-4 rounded-lg border border-border bg-accent/20">
            <h4 className="text-sm font-medium text-foreground mb-2">Selected Automations</h4>
            <div className="space-y-2">
              {selectedAutomations.map((automation) => (
                <div key={automation.id} className="flex items-center gap-2">
                  <Badge variant="secondary" className="text-xs">
                    {automation.category}
                  </Badge>
                  <span className="text-sm text-foreground">{automation.name}</span>
                  <span className="text-xs text-muted-foreground">({automation.estimatedDuration})</span>
                </div>
              ))}
            </div>
          </div>

          {/* Schedule Type */}
          <div className="space-y-3">
            <Label className="text-foreground">Schedule Type</Label>
            <Select value={scheduleType} onValueChange={(value: "once" | "recurring") => setScheduleType(value)}>
              <SelectTrigger className="bg-input border-border">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="once">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    Run Once
                  </div>
                </SelectItem>
                <SelectItem value="recurring">
                  <div className="flex items-center gap-2">
                    <Repeat className="h-4 w-4" />
                    Recurring
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Date and Time */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="date" className="text-foreground">
                Date
              </Label>
              <Input
                id="date"
                type="date"
                value={scheduledDate}
                onChange={(e) => setScheduledDate(e.target.value)}
                min={currentDate}
                className="bg-input border-border"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="time" className="text-foreground">
                Time
              </Label>
              <Input
                id="time"
                type="time"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                className="bg-input border-border"
                required
              />
            </div>
          </div>

          {/* Recurring Options */}
          {scheduleType === "recurring" && (
            <div className="space-y-4">
              <div className="space-y-3">
                <Label className="text-foreground">Repeat Pattern</Label>
                <Select
                  value={recurringPattern}
                  onValueChange={(value: "daily" | "weekly" | "monthly") => setRecurringPattern(value)}
                >
                  <SelectTrigger className="bg-input border-border">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {recurringPattern === "weekly" && (
                <div className="space-y-3">
                  <Label className="text-foreground">Days of Week</Label>
                  <div className="flex gap-2">
                    {daysOfWeek.map((day) => (
                      <div key={day.value} className="flex items-center space-x-2">
                        <Checkbox
                          id={day.value}
                          checked={recurringDays.includes(day.value)}
                          onCheckedChange={(checked) => handleDayToggle(day.value, !!checked)}
                        />
                        <Label htmlFor={day.value} className="text-sm text-foreground">
                          {day.label}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="endDate" className="text-foreground">
                  End Date (Optional)
                </Label>
                <Input
                  id="endDate"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={scheduledDate || currentDate}
                  className="bg-input border-border"
                />
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="flex-1 border-border hover:bg-accent"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSchedule}
              disabled={!scheduledDate || !scheduledTime}
              className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
            >
              <Clock className="h-4 w-4 mr-2" />
              Schedule Automations
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
