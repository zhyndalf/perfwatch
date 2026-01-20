import { defineStore } from 'pinia'
import { configApi } from '@/api'

export const useConfigStore = defineStore('config', {
  state: () => ({
    loading: false,
    error: '',
    samplingIntervalSeconds: null,
    perfEventsEnabled: null,
    appVersion: null,
  }),

  actions: {
    async fetchConfig() {
      this.loading = true
      this.error = ''

      try {
        const response = await configApi.getConfig()
        const data = response.data
        this.samplingIntervalSeconds = data.sampling_interval_seconds
        this.perfEventsEnabled = data.perf_events_enabled
        this.appVersion = data.app_version
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load config'
      } finally {
        this.loading = false
      }
    },
  },
})
