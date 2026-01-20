import { defineStore } from 'pinia'
import { retentionApi } from '@/api'

export const useRetentionStore = defineStore('retention', {
  state: () => ({
    loading: false,
    saving: false,
    error: '',
    success: '',
    retentionDays: 30,
    downsampleAfterDays: 7,
    downsampleInterval: '1h',
    archiveEnabled: true,
    lastArchiveRun: null,
    cleanupSummary: null,
  }),

  actions: {
    async fetchPolicy() {
      this.loading = true
      this.error = ''
      this.success = ''
      this.cleanupSummary = null

      try {
        const response = await retentionApi.getPolicy()
        const data = response.data
        this.retentionDays = data.retention_days
        this.downsampleAfterDays = data.downsample_after_days
        this.downsampleInterval = data.downsample_interval
        this.archiveEnabled = data.archive_enabled
        this.lastArchiveRun = data.last_archive_run
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load retention policy'
      } finally {
        this.loading = false
      }
    },

    async updatePolicy() {
      this.error = ''
      this.success = ''
      this.cleanupSummary = null

      if (this.downsampleAfterDays > this.retentionDays) {
        this.error = 'Downsample days must be less than or equal to retention days'
        return null
      }

      this.saving = true
      try {
        const response = await retentionApi.updatePolicy({
          retention_days: this.retentionDays,
          downsample_after_days: this.downsampleAfterDays,
          downsample_interval: this.downsampleInterval,
          archive_enabled: this.archiveEnabled,
        })
        this.lastArchiveRun = response.data.last_archive_run
        this.success = 'Retention policy updated'
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to update retention policy'
        return null
      } finally {
        this.saving = false
      }
    },

    async runCleanup() {
      this.error = ''
      this.success = ''
      this.cleanupSummary = null
      this.saving = true

      try {
        const response = await retentionApi.runCleanup()
        this.cleanupSummary = {
          deleted: response.data.deleted_count,
          downsampled: response.data.downsampled_count,
        }
        this.lastArchiveRun = response.data.last_archive_run
        this.success = 'Cleanup completed'
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to run cleanup'
        return null
      } finally {
        this.saving = false
      }
    },
  },
})
