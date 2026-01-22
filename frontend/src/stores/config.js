import { defineStore } from 'pinia'
import { configApi } from '@/api'

export const useConfigStore = defineStore('config', {
  state: () => ({
    loading: false,
    saving: false,
    error: '',
    success: '',
    samplingIntervalSeconds: null,
    perfEventsEnabled: null,
    perfEventsCpuCores: null,
    perfEventsIntervalMs: null,
    appVersion: null,
  }),

  actions: {
    async fetchConfig() {
      this.loading = true
      this.error = ''
      this.success = ''

      try {
        const response = await configApi.getConfig()
        const data = response.data
        this.samplingIntervalSeconds = data.sampling_interval_seconds
        this.perfEventsEnabled = data.perf_events_enabled
        this.perfEventsCpuCores = data.perf_events_cpu_cores
        this.perfEventsIntervalMs = data.perf_events_interval_ms
        this.appVersion = data.app_version
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load config'
      } finally {
        this.loading = false
      }
    },

    async updateConfig() {
      this.error = ''
      this.success = ''
      this.saving = true

      try {
        const response = await configApi.updateConfig({
          sampling_interval_seconds: this.samplingIntervalSeconds,
          perf_events_enabled: this.perfEventsEnabled,
          perf_events_cpu_cores: this.perfEventsCpuCores,
          perf_events_interval_ms: this.perfEventsIntervalMs,
        })
        const data = response.data?.config
        if (data) {
          this.samplingIntervalSeconds = data.sampling_interval_seconds
          this.perfEventsEnabled = data.perf_events_enabled
          this.perfEventsCpuCores = data.perf_events_cpu_cores
          this.perfEventsIntervalMs = data.perf_events_interval_ms
          this.appVersion = data.app_version
        }
        this.success = 'Application settings updated'
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to update config'
        return null
      } finally {
        this.saving = false
      }
    },
  },
})
