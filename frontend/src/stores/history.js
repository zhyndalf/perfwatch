import { defineStore } from 'pinia'
import { historyApi } from '@/api'

const metricTypes = ['cpu', 'memory', 'network', 'disk', 'perf_events', 'memory_bandwidth']

const emptyDataset = () => ({
  startTime: null,
  endTime: null,
  interval: null,
  count: 0,
  dataPoints: [],
})

export const useHistoryStore = defineStore('history', {
  state: () => ({
    metricType: 'cpu',
    loadingA: false,
    loadingB: false,
    errorA: null,
    errorB: null,
    datasetA: emptyDataset(),
    datasetB: emptyDataset(),
    metricTypes: [...metricTypes],
  }),

  getters: {
    hasA: (state) => state.datasetA.dataPoints.length > 0,
    hasB: (state) => state.datasetB.dataPoints.length > 0,
  },

  actions: {
    setMetricType(metricType) {
      this.metricType = metricType
      this.clearDataset('A')
      this.clearDataset('B')
    },

    async loadDataset(which, startTime, endTime, limit = 1000) {
      const isA = which === 'A'
      const loadingKey = isA ? 'loadingA' : 'loadingB'
      const errorKey = isA ? 'errorA' : 'errorB'
      const datasetKey = isA ? 'datasetA' : 'datasetB'

      this[loadingKey] = true
      this[errorKey] = null

      try {
        const response = await historyApi.getMetrics(this.metricType, startTime, endTime, limit)
        const data = response.data

        this[datasetKey] = {
          startTime: data.start_time ?? startTime,
          endTime: data.end_time ?? endTime,
          interval: data.interval || null,
          count: data.count ?? (data.data_points || []).length,
          dataPoints: data.data_points || [],
        }
      } catch (err) {
        console.error('Failed to load history:', err)
        this[errorKey] = err.response?.data?.detail || err.message || 'Failed to load history'
        this[datasetKey] = emptyDataset()
      } finally {
        this[loadingKey] = false
      }
    },

    clearDataset(which) {
      if (which === 'A') {
        this.datasetA = emptyDataset()
        this.errorA = null
        return
      }
      if (which === 'B') {
        this.datasetB = emptyDataset()
        this.errorB = null
      }
    },
  },
})
