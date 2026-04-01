/*
 * Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
 */

"use client"

import { useEffect, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Save } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { customInstance } from "@/lib/axios-instance"

interface AutoTuningConfig {
  compression_threshold: number
  reindex_frequency_hours: number
  memory_limit_mb: number
  enable_alerts: boolean
  alert_threshold: number
}

const fetchConfig = () =>
  customInstance<AutoTuningConfig>({
    url: "/context-mode/config",
    method: "GET",
  })

const updateConfig = (config: AutoTuningConfig) =>
  customInstance({
    url: "/context-mode/config",
    method: "POST",
    data: config,
  })

export function AutoTuningConfig() {
  const queryClient = useQueryClient()
  const [isDirty, setIsDirty] = useState(false)
  const [formData, setFormData] = useState<AutoTuningConfig>({
    compression_threshold: 0.8,
    reindex_frequency_hours: 24,
    memory_limit_mb: 512,
    enable_alerts: true,
    alert_threshold: 0.5,
  })

  const { data, isLoading } = useQuery({
    queryKey: ["context-mode", "config"],
    queryFn: fetchConfig,
    retry: false,
  })

  useEffect(() => {
    if (data) {
      setFormData(data)
    }
  }, [data])

  const mutation = useMutation({
    mutationFn: updateConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["context-mode", "config"] })
      setIsDirty(false)
    },
  })

  const handleChange = (field: keyof AutoTuningConfig, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
    setIsDirty(true)
  }

  const handleSave = async () => {
    await mutation.mutateAsync(formData)
  }

  if (isLoading) {
    return (
      <div className="space-y-4 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-9 w-full" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">
          Auto-Tuning Configuration
        </h3>
        <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
          Adjust compression thresholds and indexing behavior
        </p>
      </div>

      <div className="space-y-4">
        {/* Compression Threshold */}
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-[hsl(var(--foreground))]">
            Compression Threshold
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="0.5"
              max="1"
              step="0.05"
              value={formData.compression_threshold}
              onChange={(e) =>
                handleChange(
                  "compression_threshold",
                  parseFloat(e.target.value)
                )
              }
              className="flex-1 h-2 rounded-lg bg-[hsl(var(--border))] cursor-pointer"
            />
            <span className="text-sm font-mono text-[hsl(var(--muted-foreground))] w-12">
              {(formData.compression_threshold * 100).toFixed(0)}%
            </span>
          </div>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">
            Minimum compression ratio to consider indexing successful
          </p>
        </div>

        {/* Reindex Frequency */}
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-[hsl(var(--foreground))]">
            Reindex Frequency (hours)
          </label>
          <input
            type="number"
            min="1"
            max="168"
            value={formData.reindex_frequency_hours}
            onChange={(e) =>
              handleChange("reindex_frequency_hours", parseInt(e.target.value))
            }
            className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2 text-sm text-[hsl(var(--foreground))] focus:outline-none focus:border-[hsl(var(--primary))]"
          />
          <p className="text-xs text-[hsl(var(--muted-foreground))]">
            How often to automatically reindex memory (1-168 hours)
          </p>
        </div>

        {/* Memory Limit */}
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-[hsl(var(--foreground))]">
            Memory Limit (MB)
          </label>
          <input
            type="number"
            min="100"
            max="2048"
            step="50"
            value={formData.memory_limit_mb}
            onChange={(e) =>
              handleChange("memory_limit_mb", parseInt(e.target.value))
            }
            className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2 text-sm text-[hsl(var(--foreground))] focus:outline-none focus:border-[hsl(var(--primary))]"
          />
          <p className="text-xs text-[hsl(var(--muted-foreground))]">
            Maximum memory allocation for indexing operations
          </p>
        </div>

        {/* Enable Alerts */}
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="alerts"
            checked={formData.enable_alerts}
            onChange={(e) =>
              handleChange("enable_alerts", e.target.checked)
            }
            className="rounded border border-[hsl(var(--border))] cursor-pointer"
          />
          <label
            htmlFor="alerts"
            className="text-sm font-medium text-[hsl(var(--foreground))] cursor-pointer"
          >
            Enable compression alerts
          </label>
        </div>

        {formData.enable_alerts && (
          <div className="flex flex-col gap-2 pl-6">
            <label className="text-sm font-medium text-[hsl(var(--foreground))]">
              Alert Threshold
            </label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0.3"
                max="0.9"
                step="0.05"
                value={formData.alert_threshold}
                onChange={(e) =>
                  handleChange("alert_threshold", parseFloat(e.target.value))
                }
                className="flex-1 h-2 rounded-lg bg-[hsl(var(--border))] cursor-pointer"
              />
              <span className="text-sm font-mono text-[hsl(var(--muted-foreground))] w-12">
                {(formData.alert_threshold * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              Alert if compression drops below this threshold
            </p>
          </div>
        )}
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={!isDirty || mutation.isPending}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] text-sm font-medium hover:bg-[hsl(var(--primary)/0.9)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Save className="h-4 w-4" />
          {mutation.isPending ? "Saving..." : "Save Changes"}
        </button>
      </div>

      {mutation.isSuccess && (
        <p className="text-sm text-green-500">
          Configuration saved successfully.
        </p>
      )}
      {mutation.isError && (
        <p className="text-sm text-red-500">
          Failed to save configuration. Please try again.
        </p>
      )}
    </div>
  )
}
