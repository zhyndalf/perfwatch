/**
 * Chart configuration factory for ECharts.
 * Provides reusable chart configuration builders to eliminate duplication.
 */

import { formatBytes, formatPerfValueWithUnit } from './formatters'

// Shared color palette
export const CHART_COLORS = {
  cpu: '#3b82f6',
  memory: '#22c55e',
  networkUp: '#06b6d4',
  networkDown: '#a855f7',
  diskRead: '#22c55e',
  diskWrite: '#f97316',
  pageIn: '#14b8a6',
  pageOut: '#f97316',
  swapIn: '#ec4899',
  swapOut: '#8b5cf6',
  perfEvent: '#38bdf8',
  datasetA: '#3b82f6',
  datasetB: '#f97316',
}

// Shared axis styling
const AXIS_STYLE = {
  axisLabel: { color: '#e2e8f0' },
  axisLine: { lineStyle: { color: '#475569' } },
  splitLine: { lineStyle: { color: '#334155' } },
}

/**
 * Create base grid configuration.
 * @param {Object} overrides - Optional grid property overrides
 * @returns {Object} Grid configuration
 */
export function createBaseGrid(overrides = {}) {
  return {
    left: 56,
    right: 24,
    top: 20,
    bottom: 36,
    containLabel: true,
    ...overrides,
  }
}

/**
 * Create base tooltip configuration.
 * @param {Object} overrides - Optional tooltip property overrides
 * @returns {Object} Tooltip configuration
 */
export function createBaseTooltip(overrides = {}) {
  return {
    trigger: 'axis',
    backgroundColor: 'rgba(30, 30, 35, 0.95)',
    borderColor: '#3b3b45',
    textStyle: { color: '#f8fafc' },
    ...overrides,
  }
}

/**
 * Create X-axis configuration for time series.
 * @param {Array} timestamps - Array of timestamp labels
 * @param {Object} overrides - Optional axis property overrides
 * @returns {Object} X-axis configuration
 */
export function createTimeXAxis(timestamps, overrides = {}) {
  return {
    type: 'category',
    data: timestamps,
    ...AXIS_STYLE,
    ...overrides,
  }
}

/**
 * Create Y-axis configuration for percentage values (0-100%).
 * @param {Object} overrides - Optional axis property overrides
 * @returns {Object} Y-axis configuration
 */
export function createPercentYAxis(overrides = {}) {
  return {
    type: 'value',
    max: 100,
    axisLabel: { formatter: '{value}%', color: '#e2e8f0', margin: 10 },
    splitLine: AXIS_STYLE.splitLine,
    axisLine: AXIS_STYLE.axisLine,
    ...overrides,
  }
}

/**
 * Create Y-axis configuration for throughput values (bytes/s).
 * @param {Object} overrides - Optional axis property overrides
 * @returns {Object} Y-axis configuration
 */
export function createThroughputYAxis(overrides = {}) {
  return {
    type: 'value',
    axisLabel: {
      formatter: (val) => formatBytes(val) + '/s',
      color: '#e2e8f0',
      margin: 10,
    },
    splitLine: AXIS_STYLE.splitLine,
    axisLine: AXIS_STYLE.axisLine,
    ...overrides,
  }
}

/**
 * Create Y-axis configuration for generic numeric values.
 * @param {Object} overrides - Optional axis property overrides
 * @returns {Object} Y-axis configuration
 */
export function createNumericYAxis(overrides = {}) {
  return {
    type: 'value',
    axisLabel: { color: '#e2e8f0', margin: 10 },
    splitLine: AXIS_STYLE.splitLine,
    axisLine: AXIS_STYLE.axisLine,
    ...overrides,
  }
}

/**
 * Create a line series configuration.
 * @param {string} name - Series name
 * @param {Array} data - Series data
 * @param {string} color - Line color
 * @param {Object} overrides - Optional series property overrides
 * @returns {Object} Series configuration
 */
export function createLineSeries(name, data, color, overrides = {}) {
  return {
    name,
    type: 'line',
    showSymbol: false,
    lineStyle: { color, width: 2 },
    data,
    ...overrides,
  }
}

/**
 * Create legend configuration.
 * @param {Array} data - Legend items
 * @param {Object} overrides - Optional legend property overrides
 * @returns {Object} Legend configuration
 */
export function createLegend(data, overrides = {}) {
  return {
    data,
    textStyle: { color: '#e2e8f0' },
    ...overrides,
  }
}

/**
 * Create data zoom configuration for interactive charts.
 * @returns {Array} Data zoom configuration array
 */
export function createDataZoom() {
  return [
    { type: 'inside', start: 0, end: 100 },
    {
      type: 'slider',
      start: 0,
      end: 100,
      height: 20,
      bottom: 10,
      borderColor: '#3b3b45',
      backgroundColor: '#1a1a1f',
      fillerColor: 'rgba(59, 130, 246, 0.2)',
      handleStyle: { color: '#3b82f6' },
      textStyle: { color: '#e2e8f0' },
    },
  ]
}

// ============================================================================
// High-level chart builders for History.vue
// ============================================================================

/**
 * Create base options for history charts with data zoom.
 * @param {Array} timestamps - Array of timestamp labels
 * @returns {Object} Base chart options
 */
export function createHistoryBaseOptions(timestamps) {
  return {
    grid: createBaseGrid({ left: 64, right: 32, top: 40, bottom: 80 }),
    tooltip: createBaseTooltip(),
    xAxis: {
      type: 'category',
      data: timestamps,
      axisLabel: { color: '#e2e8f0', rotate: 45, margin: 12 },
      axisLine: { lineStyle: { color: '#475569' } },
    },
    dataZoom: createDataZoom(),
    legend: createLegend([]),
  }
}

/**
 * Build chart options for CPU metrics in history view.
 * @param {Array} points - Data points array
 * @param {string} label - Chart label
 * @returns {Object} Chart options
 */
export function buildCpuHistoryChart(points, label) {
  const timestamps = points.map((p) => new Date(p.timestamp).toLocaleTimeString())
  return {
    ...createHistoryBaseOptions(timestamps),
    yAxis: createPercentYAxis(),
    series: [
      createLineSeries(
        `${label} CPU Usage`,
        points.map((p) => p.data?.usage_percent ?? null),
        CHART_COLORS.cpu,
        { areaStyle: { opacity: 0.15, color: CHART_COLORS.cpu } }
      ),
    ],
  }
}

/**
 * Build chart options for memory metrics in history view.
 * @param {Array} points - Data points array
 * @param {string} label - Chart label
 * @returns {Object} Chart options
 */
export function buildMemoryHistoryChart(points, label) {
  const timestamps = points.map((p) => new Date(p.timestamp).toLocaleTimeString())
  return {
    ...createHistoryBaseOptions(timestamps),
    yAxis: createPercentYAxis(),
    series: [
      createLineSeries(
        `${label} Memory Usage`,
        points.map((p) => p.data?.usage_percent ?? null),
        CHART_COLORS.memory,
        { areaStyle: { opacity: 0.15, color: CHART_COLORS.memory } }
      ),
    ],
  }
}

/**
 * Build chart options for network metrics in history view.
 * @param {Array} points - Data points array
 * @returns {Object} Chart options
 */
export function buildNetworkHistoryChart(points) {
  const timestamps = points.map((p) => new Date(p.timestamp).toLocaleTimeString())
  return {
    ...createHistoryBaseOptions(timestamps),
    legend: createLegend(['Download', 'Upload']),
    yAxis: createThroughputYAxis(),
    series: [
      createLineSeries(
        'Download',
        points.map((p) => p.data?.bytes_recv_per_sec ?? null),
        CHART_COLORS.networkDown
      ),
      createLineSeries(
        'Upload',
        points.map((p) => p.data?.bytes_sent_per_sec ?? null),
        CHART_COLORS.networkUp
      ),
    ],
  }
}

/**
 * Build chart options for disk metrics in history view.
 * @param {Array} points - Data points array
 * @returns {Object} Chart options
 */
export function buildDiskHistoryChart(points) {
  const timestamps = points.map((p) => new Date(p.timestamp).toLocaleTimeString())
  return {
    ...createHistoryBaseOptions(timestamps),
    legend: createLegend(['Read', 'Write']),
    yAxis: createThroughputYAxis(),
    series: [
      createLineSeries(
        'Read',
        points.map((p) => p.data?.io?.read_bytes_per_sec ?? null),
        CHART_COLORS.diskRead
      ),
      createLineSeries(
        'Write',
        points.map((p) => p.data?.io?.write_bytes_per_sec ?? null),
        CHART_COLORS.diskWrite
      ),
    ],
  }
}

/**
 * Build chart options for perf events in history view.
 * @param {Array} points - Data points array
 * @param {string} perfEvent - Selected perf event name
 * @param {Function} getPerfEventValue - Function to extract perf event value
 * @param {Function} getPerfEventUnit - Function to get perf event unit
 * @returns {Object} Chart options
 */
export function buildPerfEventsHistoryChart(points, perfEvent, getPerfEventValue, getPerfEventUnit) {
  const timestamps = points.map((p) => new Date(p.timestamp).toLocaleTimeString())
  const unit = getPerfEventUnit(points, perfEvent)
  return {
    ...createHistoryBaseOptions(timestamps),
    legend: createLegend([perfEvent]),
    yAxis: {
      type: 'value',
      name: unit || '',
      axisLabel: {
        color: '#e2e8f0',
        margin: 10,
        formatter: (value) => formatPerfValueWithUnit(value, unit),
      },
      splitLine: { lineStyle: { color: '#334155' } },
      axisLine: { lineStyle: { color: '#475569' } },
    },
    series: [
      createLineSeries(
        perfEvent,
        points.map((p) => getPerfEventValue(p, perfEvent)),
        CHART_COLORS.perfEvent
      ),
    ],
  }
}

/**
 * Build chart options for memory bandwidth in history view.
 * @param {Array} points - Data points array
 * @returns {Object} Chart options
 */
export function buildMemoryBandwidthHistoryChart(points) {
  const timestamps = points.map((p) => new Date(p.timestamp).toLocaleTimeString())
  return {
    ...createHistoryBaseOptions(timestamps),
    legend: createLegend(['Page I/O', 'Swap I/O']),
    yAxis: createThroughputYAxis(),
    series: [
      createLineSeries(
        'Page I/O',
        points.map((p) => p.data?.page_io_bytes_per_sec ?? null),
        CHART_COLORS.diskRead
      ),
      createLineSeries(
        'Swap I/O',
        points.map((p) => p.data?.swap_io_bytes_per_sec ?? null),
        '#f59e0b'
      ),
    ],
  }
}

/**
 * Build default chart options for unknown metric types.
 * @param {Array} points - Data points array
 * @param {string} label - Chart label
 * @returns {Object} Chart options
 */
export function buildDefaultHistoryChart(points, label) {
  const timestamps = points.map((p) => new Date(p.timestamp).toLocaleTimeString())
  return {
    ...createHistoryBaseOptions(timestamps),
    yAxis: createNumericYAxis(),
    series: [
      createLineSeries(
        label,
        points.map((p) => p.data?.value ?? null),
        CHART_COLORS.cpu
      ),
    ],
  }
}
