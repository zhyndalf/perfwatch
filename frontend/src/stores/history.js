import { defineStore } from 'pinia'
import { historyApi } from '@/api'

const comparisonShiftMs = {
  yesterday: 24 * 60 * 60 * 1000,
  last_week: 7 * 24 * 60 * 60 * 1000,
}

const normalizeTimestamp = (timestamp) => {
  const ms = new Date(timestamp).getTime()
  if (Number.isNaN(ms)) return null
  return Math.round(ms / 1000) * 1000
}

const buildComparisonSeries = (state, selector) => {
  if (!state.compareTo || state.compareTo === 'none') return []
  if (!state.dataPoints.length || !state.comparisonPoints.length) return []

  const shift = comparisonShiftMs[state.compareTo]
  if (!shift) return []

  const comparisonMap = new Map()
  for (const point of state.comparisonPoints) {
    const normalized = normalizeTimestamp(point.timestamp)
    if (normalized === null) continue
    comparisonMap.set(normalized + shift, selector(point))
  }

  return state.dataPoints.map((point) => {
    const normalized = normalizeTimestamp(point.timestamp)
    if (normalized === null) return null
    return comparisonMap.has(normalized) ? comparisonMap.get(normalized) : null
  })
}

export const useHistoryStore = defineStore('history', {
  state: () => ({
    loading: false,
    error: null,
    // Time range selection
    timeRange: {
      start: null,
      end: null,
    },
    // Selected metric type
    selectedMetric: 'cpu',
    compareTo: 'none',
    // Fetched data points
    dataPoints: [],
    comparisonPoints: [],
    comparisonSummary: {
      currentAvg: null,
      comparisonAvg: null,
      changePercent: null,
    },
    // Response metadata
    metadata: {
      count: 0,
      startTime: null,
      endTime: null,
      interval: null,
    },
    // Available metric types
    metricTypes: ['cpu', 'memory', 'network', 'disk', 'perf_events', 'memory_bandwidth'],
  }),

  getters: {
    /**
     * Get timestamps from data points
     */
    timestamps: (state) => {
      return state.dataPoints.map((point) => point.timestamp)
    },

    /**
     * Get formatted timestamps for chart x-axis
     */
    formattedTimestamps: (state) => {
      return state.dataPoints.map((point) => {
        const date = new Date(point.timestamp)
        return date.toLocaleTimeString()
      })
    },

    /**
     * Extract CPU usage data for charts
     */
    cpuUsageData: (state) => {
      if (state.selectedMetric !== 'cpu') return []
      return state.dataPoints.map((point) => point.data?.usage_percent ?? null)
    },

    /**
     * Extract memory usage data for charts
     */
    memoryUsageData: (state) => {
      if (state.selectedMetric !== 'memory') return []
      return state.dataPoints.map((point) => point.data?.usage_percent ?? null)
    },

    /**
     * Extract network upload data for charts
     */
    networkUpData: (state) => {
      if (state.selectedMetric !== 'network') return []
      return state.dataPoints.map((point) => point.data?.bytes_sent_per_sec ?? null)
    },

    /**
     * Extract network download data for charts
     */
    networkDownData: (state) => {
      if (state.selectedMetric !== 'network') return []
      return state.dataPoints.map((point) => point.data?.bytes_recv_per_sec ?? null)
    },

    /**
     * Extract disk read data for charts
     */
    diskReadData: (state) => {
      if (state.selectedMetric !== 'disk') return []
      return state.dataPoints.map((point) => point.data?.io?.read_bytes_per_sec ?? null)
    },

    /**
     * Extract disk write data for charts
     */
    diskWriteData: (state) => {
      if (state.selectedMetric !== 'disk') return []
      return state.dataPoints.map((point) => point.data?.io?.write_bytes_per_sec ?? null)
    },

    /**
     * Extract perf_events IPC data for charts
     */
    perfIpcData: (state) => {
      if (state.selectedMetric !== 'perf_events') return []
      return state.dataPoints.map((point) => point.data?.ipc ?? null)
    },

    /**
     * Extract perf_events miss rates as percentages
     */
    perfL1dMissRateData: (state) => {
      if (state.selectedMetric !== 'perf_events') return []
      return state.dataPoints.map((point) =>
        point.data?.l1d_miss_rate != null ? point.data.l1d_miss_rate * 100 : null
      )
    },

    perfLlcMissRateData: (state) => {
      if (state.selectedMetric !== 'perf_events') return []
      return state.dataPoints.map((point) =>
        point.data?.llc_miss_rate != null ? point.data.llc_miss_rate * 100 : null
      )
    },

    /**
     * Extract memory bandwidth aggregate I/O
     */
    memoryPageIoBytesData: (state) => {
      if (state.selectedMetric !== 'memory_bandwidth') return []
      return state.dataPoints.map((point) => point.data?.page_io_bytes_per_sec ?? null)
    },

    memorySwapIoBytesData: (state) => {
      if (state.selectedMetric !== 'memory_bandwidth') return []
      return state.dataPoints.map((point) => point.data?.swap_io_bytes_per_sec ?? null)
    },

    comparisonTimestamps: (state) => {
      return state.comparisonPoints.map((point) => point.timestamp)
    },

    comparisonCpuUsageData: (state) => {
      if (state.selectedMetric !== 'cpu') return []
      return buildComparisonSeries(state, (point) => point.data?.usage_percent ?? null)
    },

    comparisonMemoryUsageData: (state) => {
      if (state.selectedMetric !== 'memory') return []
      return buildComparisonSeries(state, (point) => point.data?.usage_percent ?? null)
    },

    comparisonNetworkUpData: (state) => {
      if (state.selectedMetric !== 'network') return []
      return buildComparisonSeries(state, (point) => point.data?.bytes_sent_per_sec ?? null)
    },

    comparisonNetworkDownData: (state) => {
      if (state.selectedMetric !== 'network') return []
      return buildComparisonSeries(state, (point) => point.data?.bytes_recv_per_sec ?? null)
    },

    comparisonDiskReadData: (state) => {
      if (state.selectedMetric !== 'disk') return []
      return buildComparisonSeries(state, (point) => point.data?.io?.read_bytes_per_sec ?? null)
    },

    comparisonDiskWriteData: (state) => {
      if (state.selectedMetric !== 'disk') return []
      return buildComparisonSeries(state, (point) => point.data?.io?.write_bytes_per_sec ?? null)
    },

    comparisonPerfIpcData: (state) => {
      if (state.selectedMetric !== 'perf_events') return []
      return buildComparisonSeries(state, (point) => point.data?.ipc ?? null)
    },

    comparisonPerfL1dMissRateData: (state) => {
      if (state.selectedMetric !== 'perf_events') return []
      return buildComparisonSeries(state, (point) =>
        point.data?.l1d_miss_rate != null ? point.data.l1d_miss_rate * 100 : null
      )
    },

    comparisonPerfLlcMissRateData: (state) => {
      if (state.selectedMetric !== 'perf_events') return []
      return buildComparisonSeries(state, (point) =>
        point.data?.llc_miss_rate != null ? point.data.llc_miss_rate * 100 : null
      )
    },

    comparisonMemoryPageIoBytesData: (state) => {
      if (state.selectedMetric !== 'memory_bandwidth') return []
      return buildComparisonSeries(state, (point) => point.data?.page_io_bytes_per_sec ?? null)
    },

    comparisonMemorySwapIoBytesData: (state) => {
      if (state.selectedMetric !== 'memory_bandwidth') return []
      return buildComparisonSeries(state, (point) => point.data?.swap_io_bytes_per_sec ?? null)
    },

    /**
     * Check if we have data loaded
     */
    hasData: (state) => state.dataPoints.length > 0,
    hasComparison: (state) => state.comparisonPoints.length > 0,
  },

  actions: {
    /**
     * Set the selected metric type
     * @param {string} metricType
     */
    setSelectedMetric(metricType) {
      this.selectedMetric = metricType
      // Clear existing data when metric type changes
      this.dataPoints = []
      this.comparisonPoints = []
      this.comparisonSummary = { currentAvg: null, comparisonAvg: null, changePercent: null }
      this.metadata = { count: 0, startTime: null, endTime: null, interval: null }
    },

    /**
     * Set the time range for queries
     * @param {Date|string} start
     * @param {Date|string} end
     */
    setTimeRange(start, end) {
      this.timeRange.start = start instanceof Date ? start.toISOString() : start
      this.timeRange.end = end instanceof Date ? end.toISOString() : end
    },

    /**
     * Load historical metrics data
     * @param {string} metricType - Metric type to query
     * @param {string} startTime - ISO datetime string
     * @param {string} endTime - ISO datetime string
     * @param {number} [limit=1000] - Max results
     */
    async loadHistory(metricType, startTime, endTime, limit = 1000) {
      this.loading = true
      this.error = null

      try {
        const response = await historyApi.getMetrics(metricType, startTime, endTime, limit)
        const data = response.data

        this.selectedMetric = metricType
        this.dataPoints = data.data_points || []
        this.comparisonPoints = []
        this.comparisonSummary = { currentAvg: null, comparisonAvg: null, changePercent: null }
        this.metadata = {
          count: data.count,
          startTime: data.start_time,
          endTime: data.end_time,
          interval: data.interval || null,
        }
        this.timeRange = {
          start: startTime,
          end: endTime,
        }
      } catch (err) {
        console.error('Failed to load history:', err)
        this.error = err.response?.data?.detail || err.message || 'Failed to load history'
        this.dataPoints = []
        this.metadata = { count: 0, startTime: null, endTime: null, interval: null }
      } finally {
        this.loading = false
      }
    },

    async loadComparison(metricType, period, compareTo, limit = 1000) {
      this.loading = true
      this.error = null

      try {
        const response = await historyApi.compareMetrics(metricType, period, compareTo, limit)
        const data = response.data

        this.selectedMetric = metricType
        this.compareTo = compareTo
        this.dataPoints = data.current?.data_points || []
        this.comparisonPoints = data.comparison?.data_points || []
        this.comparisonSummary = {
          currentAvg: data.summary?.current_avg ?? null,
          comparisonAvg: data.summary?.comparison_avg ?? null,
          changePercent: data.summary?.change_percent ?? null,
        }
        this.metadata = {
          count: this.dataPoints.length,
          startTime: data.current?.start_time ?? null,
          endTime: data.current?.end_time ?? null,
          interval: data.interval || null,
        }
        this.timeRange = {
          start: data.current?.start_time ?? null,
          end: data.current?.end_time ?? null,
        }
      } catch (err) {
        console.error('Failed to load comparison:', err)
        this.error = err.response?.data?.detail || err.message || 'Failed to load comparison'
        this.dataPoints = []
        this.comparisonPoints = []
        this.comparisonSummary = { currentAvg: null, comparisonAvg: null, changePercent: null }
        this.metadata = { count: 0, startTime: null, endTime: null, interval: null }
      } finally {
        this.loading = false
      }
    },

    /**
     * Refresh current query
     */
    async refresh() {
      if (this.timeRange.start && this.timeRange.end) {
        await this.loadHistory(
          this.selectedMetric,
          this.timeRange.start,
          this.timeRange.end
        )
      }
    },

    /**
     * Clear all loaded data
     */
    clearData() {
      this.dataPoints = []
      this.metadata = { count: 0, startTime: null, endTime: null, interval: null }
      this.error = null
    },

    /**
     * Load data for the last N hours
     * @param {number} hours - Number of hours to look back
     */
    async loadLastHours(hours) {
      const end = new Date()
      const start = new Date(end.getTime() - hours * 60 * 60 * 1000)

      await this.loadHistory(
        this.selectedMetric,
        start.toISOString(),
        end.toISOString()
      )
    },
  },
})
