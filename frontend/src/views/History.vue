<template>
  <div class="p-6 space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">History</h1>
        <p class="text-gray-400 text-sm">View historical metrics data</p>
      </div>
      <div v-if="historyStore.metadata.count > 0" class="text-gray-400 text-sm">
        <span class="text-white font-medium">{{ historyStore.metadata.count }}</span> data points
        <span v-if="historyStore.metadata.interval" class="ml-2">
          • {{ historyStore.metadata.interval }} interval
        </span>
      </div>
    </div>

    <!-- Controls Card -->
    <div class="card">
      <div class="flex flex-col lg:flex-row gap-4 items-end">
        <!-- Metric Type Selector -->
        <div class="flex-1 min-w-[150px]">
          <label class="block text-sm font-medium text-gray-400 mb-2">Metric Type</label>
          <select
            v-model="selectedMetric"
            class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-cyan"
          >
            <option value="cpu">CPU</option>
            <option value="memory">Memory</option>
            <option value="network">Network</option>
            <option value="disk">Disk I/O</option>
            <option value="perf_events">Perf Events</option>
            <option value="memory_bandwidth">Memory Bandwidth</option>
          </select>
        </div>

        <!-- Start Time -->
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-400 mb-2">Start Time</label>
          <input
            v-model="startTime"
            type="datetime-local"
            :disabled="compareEnabled"
            class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-cyan"
          />
        </div>

        <!-- End Time -->
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-400 mb-2">End Time</label>
          <input
            v-model="endTime"
            type="datetime-local"
            :disabled="compareEnabled"
            class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-cyan"
          />
        </div>

        <!-- Quick Select Buttons -->
        <div class="flex gap-2">
          <button
            @click="setLastHours(1)"
            :disabled="compareEnabled"
            class="px-3 py-2 text-sm bg-dark-bg border border-dark-border rounded-lg text-gray-300 hover:text-white hover:border-accent-cyan transition-colors"
          >
            1h
          </button>
          <button
            @click="setLastHours(6)"
            :disabled="compareEnabled"
            class="px-3 py-2 text-sm bg-dark-bg border border-dark-border rounded-lg text-gray-300 hover:text-white hover:border-accent-cyan transition-colors"
          >
            6h
          </button>
          <button
            @click="setLastHours(24)"
            :disabled="compareEnabled"
            class="px-3 py-2 text-sm bg-dark-bg border border-dark-border rounded-lg text-gray-300 hover:text-white hover:border-accent-cyan transition-colors"
          >
            24h
          </button>
        </div>

        <!-- Compare Period -->
        <div class="flex-1 min-w-[160px]">
          <label class="block text-sm font-medium text-gray-400 mb-2">Compare Period</label>
          <select
            v-model="comparePeriod"
            class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-cyan"
          >
            <option value="hour">Hour</option>
            <option value="day">Day</option>
            <option value="week">Week</option>
          </select>
        </div>

        <!-- Compare To -->
        <div class="flex-1 min-w-[170px]">
          <label class="block text-sm font-medium text-gray-400 mb-2">Compare To</label>
          <select
            v-model="compareTo"
            class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-cyan"
          >
            <option value="none">None</option>
            <option value="yesterday">Yesterday</option>
            <option value="last_week">Last Week</option>
          </select>
        </div>

        <!-- Load Button -->
        <button
          @click="loadData"
          :disabled="historyStore.loading || !canLoad"
          class="px-6 py-2 bg-accent-cyan text-dark-bg font-semibold rounded-lg hover:bg-accent-cyan/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="historyStore.loading" class="flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Loading...
          </span>
          <span v-else>{{ compareEnabled ? 'Load Comparison' : 'Load Data' }}</span>
        </button>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="historyStore.error" class="card bg-red-500/10 border-red-500/30">
      <div class="flex items-center gap-3 text-red-400">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ historyStore.error }}</span>
      </div>
    </div>

    <!-- Chart Area -->
    <div class="card">
      <div v-if="!historyStore.hasData && !historyStore.loading" class="h-80 flex items-center justify-center">
        <div class="text-center text-gray-500">
          <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p class="text-lg font-medium">No data returned</p>
          <p class="text-sm mt-1">Adjust the time range or comparison period and try again</p>
        </div>
      </div>

      <div v-else-if="historyStore.loading" class="h-80 flex items-center justify-center">
        <div class="flex flex-col items-center gap-3 text-gray-400">
          <svg class="animate-spin h-10 w-10 text-accent-cyan" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span>Loading historical data...</span>
        </div>
      </div>

      <div v-else>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-white font-semibold">{{ metricTitle }}</h2>
          <span class="text-gray-500 text-sm">{{ timeRangeLabel }}</span>
        </div>
        <VChart :option="chartOptions" class="h-80" autoresize />
      </div>
    </div>

    <!-- Data Summary -->
    <div v-if="historyStore.hasData" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card text-center">
        <p class="text-gray-400 text-sm">Data Points</p>
        <p class="text-2xl font-bold text-white">{{ historyStore.metadata.count }}</p>
      </div>
      <div class="card text-center">
        <p class="text-gray-400 text-sm">Min Value</p>
        <p class="text-2xl font-bold text-accent-green">{{ formatValue(minValue) }}</p>
      </div>
      <div class="card text-center">
        <p class="text-gray-400 text-sm">Max Value</p>
        <p class="text-2xl font-bold text-accent-cyan">{{ formatValue(maxValue) }}</p>
      </div>
      <div class="card text-center">
        <p class="text-gray-400 text-sm">Average</p>
        <p class="text-2xl font-bold text-accent-purple">{{ formatValue(avgValue) }}</p>
      </div>
    </div>

    <!-- Comparison Summary -->
    <div v-if="historyStore.hasComparison" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card text-center">
        <p class="text-gray-400 text-sm">Current Avg</p>
        <p class="text-2xl font-bold text-white">{{ formatValue(historyStore.comparisonSummary.currentAvg) }}</p>
      </div>
      <div class="card text-center">
        <p class="text-gray-400 text-sm">Comparison Avg</p>
        <p class="text-2xl font-bold text-accent-cyan">{{ formatValue(historyStore.comparisonSummary.comparisonAvg) }}</p>
      </div>
      <div class="card text-center">
        <p class="text-gray-400 text-sm">Change</p>
        <p class="text-2xl font-bold text-accent-green">
          {{ formatChange(historyStore.comparisonSummary.changePercent) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { useHistoryStore } from '@/stores/history'

use([GridComponent, TooltipComponent, LegendComponent, DataZoomComponent, LineChart, CanvasRenderer])

const historyStore = useHistoryStore()

// Form state
const selectedMetric = ref('cpu')
const startTime = ref('')
const endTime = ref('')
const compareTo = ref('none')
const comparePeriod = ref('hour')

// Initialize with last hour as default
onMounted(async () => {
  setLastHours(1)
  await loadData()
})

// Computed
const compareEnabled = computed(() => compareTo.value !== 'none')

const canLoad = computed(() => {
  if (compareEnabled.value) {
    return compareTo.value !== 'none'
  }
  return startTime.value && endTime.value
})

const metricTitle = computed(() => {
  const titles = {
    cpu: 'CPU Usage History',
    memory: 'Memory Usage History',
    network: 'Network Throughput History',
    disk: 'Disk I/O History',
    perf_events: 'Performance Events History',
    memory_bandwidth: 'Memory Bandwidth History',
  }
  return titles[selectedMetric.value] || 'Metrics History'
})

const timeRangeLabel = computed(() => {
  if (!historyStore.timeRange.start || !historyStore.timeRange.end) return ''
  const start = new Date(historyStore.timeRange.start)
  const end = new Date(historyStore.timeRange.end)
  return `${start.toLocaleString()} - ${end.toLocaleString()}`
})

// Extract primary data series based on metric type
const primaryData = computed(() => {
  switch (selectedMetric.value) {
    case 'cpu':
      return historyStore.cpuUsageData
    case 'memory':
      return historyStore.memoryUsageData
    case 'network':
      return historyStore.networkDownData
    case 'disk':
      return historyStore.diskReadData
    case 'perf_events':
      return historyStore.perfIpcData
    case 'memory_bandwidth':
      return historyStore.memoryPageIoBytesData
    default:
      return []
  }
})


// Calculate statistics
const minValue = computed(() => {
  const data = primaryData.value.filter((v) => v !== null)
  return data.length > 0 ? Math.min(...data) : null
})

const maxValue = computed(() => {
  const data = primaryData.value.filter((v) => v !== null)
  return data.length > 0 ? Math.max(...data) : null
})

const avgValue = computed(() => {
  const data = primaryData.value.filter((v) => v !== null)
  if (data.length === 0) return null
  return data.reduce((a, b) => a + b, 0) / data.length
})

// Chart options based on metric type
const chartOptions = computed(() => {
  const baseOptions = {
    grid: { left: 50, right: 20, top: 40, bottom: 70 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(30, 30, 35, 0.95)',
      borderColor: '#3b3b45',
      textStyle: { color: '#f8fafc' },
    },
    xAxis: {
      type: 'category',
      data: historyStore.formattedTimestamps,
      axisLine: { lineStyle: { color: '#3b3b45' } },
      axisLabel: { color: '#e2e8f0', rotate: 45 },
      axisLine: { lineStyle: { color: '#475569' } },
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100,
      },
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
    ],
  }

  switch (selectedMetric.value) {
    case 'cpu':
      return {
        ...baseOptions,
        yAxis: {
          type: 'value',
          max: 100,
          axisLabel: { formatter: '{value}%', color: '#e2e8f0' },
          splitLine: { lineStyle: { color: '#334155' } },
          axisLine: { lineStyle: { color: '#475569' } },
        },
        series: [
          {
            name: 'CPU Usage',
            type: 'line',
            showSymbol: false,
            areaStyle: { opacity: 0.15, color: '#3b82f6' },
            lineStyle: { color: '#3b82f6', width: 2 },
            data: historyStore.cpuUsageData,
          },
          ...(historyStore.hasComparison
            ? [
                {
                  name: 'CPU Usage (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' },
                  data: historyStore.comparisonCpuUsageData,
                },
              ]
            : []),
        ],
      }

    case 'memory':
      return {
        ...baseOptions,
        yAxis: {
          type: 'value',
          max: 100,
          axisLabel: { formatter: '{value}%', color: '#e2e8f0' },
          splitLine: { lineStyle: { color: '#334155' } },
          axisLine: { lineStyle: { color: '#475569' } },
        },
        series: [
          {
            name: 'Memory Usage',
            type: 'line',
            showSymbol: false,
            areaStyle: { opacity: 0.15, color: '#22c55e' },
            lineStyle: { color: '#22c55e', width: 2 },
            data: historyStore.memoryUsageData,
          },
          ...(historyStore.hasComparison
            ? [
                {
                  name: 'Memory Usage (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' },
                  data: historyStore.comparisonMemoryUsageData,
                },
              ]
            : []),
        ],
      }

    case 'network':
      return {
        ...baseOptions,
        legend: {
          data: historyStore.hasComparison
            ? ['Download', 'Upload', 'Download (Comparison)', 'Upload (Comparison)']
            : ['Download', 'Upload'],
          textStyle: { color: '#e2e8f0' },
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: (val) => formatBytes(val) + '/s', color: '#e2e8f0' },
          splitLine: { lineStyle: { color: '#334155' } },
          axisLine: { lineStyle: { color: '#475569' } },
        },
        series: [
          {
            name: 'Download',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#a855f7', width: 2 },
            data: historyStore.networkDownData,
          },
          {
            name: 'Upload',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#06b6d4', width: 2 },
            data: historyStore.networkUpData,
          },
          ...(historyStore.hasComparison
            ? [
                {
                  name: 'Download (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' },
                  data: historyStore.comparisonNetworkDownData,
                },
                {
                  name: 'Upload (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  lineStyle: { color: '#cbd5f5', width: 2, type: 'dashed' },
                  data: historyStore.comparisonNetworkUpData,
                },
              ]
            : []),
        ],
      }

    case 'disk':
      return {
        ...baseOptions,
        legend: {
          data: historyStore.hasComparison
            ? ['Read', 'Write', 'Read (Comparison)', 'Write (Comparison)']
            : ['Read', 'Write'],
          textStyle: { color: '#e2e8f0' },
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: (val) => formatBytes(val) + '/s', color: '#e2e8f0' },
          splitLine: { lineStyle: { color: '#334155' } },
          axisLine: { lineStyle: { color: '#475569' } },
        },
        series: [
          {
            name: 'Read',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#22c55e', width: 2 },
            data: historyStore.diskReadData,
          },
          {
            name: 'Write',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#f97316', width: 2 },
            data: historyStore.diskWriteData,
          },
          ...(historyStore.hasComparison
            ? [
                {
                  name: 'Read (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' },
                  data: historyStore.comparisonDiskReadData,
                },
                {
                  name: 'Write (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  lineStyle: { color: '#cbd5f5', width: 2, type: 'dashed' },
                  data: historyStore.comparisonDiskWriteData,
                },
              ]
            : []),
        ],
      }

    case 'perf_events':
      return {
        ...baseOptions,
        legend: {
          data: historyStore.hasComparison
            ? ['IPC', 'L1D Miss %', 'LLC Miss %', 'IPC (Comparison)']
            : ['IPC', 'L1D Miss %', 'LLC Miss %'],
          textStyle: { color: '#e2e8f0' },
        },
        yAxis: [
          {
            type: 'value',
            name: 'IPC',
            axisLabel: { color: '#e2e8f0' },
            splitLine: { lineStyle: { color: '#334155' } },
            axisLine: { lineStyle: { color: '#475569' } },
          },
          {
            type: 'value',
            name: 'Miss %',
            min: 0,
            max: 100,
            axisLabel: { formatter: '{value}%', color: '#e2e8f0' },
            axisLine: { lineStyle: { color: '#475569' } },
            splitLine: { show: false },
          },
        ],
        series: [
          {
            name: 'IPC',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#38bdf8', width: 2 },
            data: historyStore.perfIpcData,
          },
          ...(historyStore.hasComparison
            ? [
                {
                  name: 'IPC (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' },
                  data: historyStore.comparisonPerfIpcData,
                },
              ]
            : []),
          {
            name: 'L1D Miss %',
            type: 'line',
            showSymbol: false,
            yAxisIndex: 1,
            lineStyle: { color: '#f97316', width: 2 },
            data: historyStore.perfL1dMissRateData,
          },
          {
            name: 'LLC Miss %',
            type: 'line',
            showSymbol: false,
            yAxisIndex: 1,
            lineStyle: { color: '#a855f7', width: 2 },
            data: historyStore.perfLlcMissRateData,
          },
          ...(historyStore.hasComparison
            ? [
                {
                  name: 'L1D Miss % (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  yAxisIndex: 1,
                  lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' },
                  data: historyStore.comparisonPerfL1dMissRateData,
                },
                {
                  name: 'LLC Miss % (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  yAxisIndex: 1,
                  lineStyle: { color: '#cbd5f5', width: 2, type: 'dashed' },
                  data: historyStore.comparisonPerfLlcMissRateData,
                },
              ]
            : []),
        ],
      }

    case 'memory_bandwidth':
      return {
        ...baseOptions,
        legend: {
          data: historyStore.hasComparison
            ? ['Page I/O', 'Swap I/O', 'Page I/O (Comparison)', 'Swap I/O (Comparison)']
            : ['Page I/O', 'Swap I/O'],
          textStyle: { color: '#e2e8f0' },
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: (val) => formatBytes(val) + '/s', color: '#e2e8f0' },
          splitLine: { lineStyle: { color: '#334155' } },
          axisLine: { lineStyle: { color: '#475569' } },
        },
        series: [
          {
            name: 'Page I/O',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#22c55e', width: 2 },
            data: historyStore.memoryPageIoBytesData,
          },
          {
            name: 'Swap I/O',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#f59e0b', width: 2 },
            data: historyStore.memorySwapIoBytesData,
          },
          ...(historyStore.hasComparison
            ? [
                {
                  name: 'Page I/O (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' },
                  data: historyStore.comparisonMemoryPageIoBytesData,
                },
                {
                  name: 'Swap I/O (Comparison)',
                  type: 'line',
                  showSymbol: false,
                  lineStyle: { color: '#cbd5f5', width: 2, type: 'dashed' },
                  data: historyStore.comparisonMemorySwapIoBytesData,
                },
              ]
            : []),
        ],
      }

    default:
      return {
        ...baseOptions,
        yAxis: {
          type: 'value',
          axisLabel: { color: '#e2e8f0' },
          splitLine: { lineStyle: { color: '#334155' } },
          axisLine: { lineStyle: { color: '#475569' } },
        },
        series: [
          {
            name: 'Value',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#3b82f6', width: 2 },
            data: primaryData.value,
          },
        ],
      }
  }
})

// Methods
function setLastHours(hours) {
  const end = new Date()
  const start = new Date(end.getTime() - hours * 60 * 60 * 1000)

  // Format for datetime-local input (YYYY-MM-DDTHH:mm)
  startTime.value = formatDateTimeLocal(start)
  endTime.value = formatDateTimeLocal(end)
}

function formatDateTimeLocal(date) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

async function loadData() {
  if (compareEnabled.value) {
    await historyStore.loadComparison(selectedMetric.value, comparePeriod.value, compareTo.value)
    return
  }

  // Convert datetime-local to ISO string
  const start = new Date(startTime.value).toISOString()
  const end = new Date(endTime.value).toISOString()

  await historyStore.loadHistory(selectedMetric.value, start, end)
}

function formatBytes(value) {
  if (value === null || value === undefined) return 'N/A'
  const bytes = Number(value)
  if (Number.isNaN(bytes)) return 'N/A'
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  const num = bytes / 1024 ** i
  return `${num.toFixed(num >= 10 ? 0 : 1)} ${units[i]}`
}

function formatValue(value) {
  if (value === null || value === undefined) return 'N/A'

  // For percentage metrics
  if (selectedMetric.value === 'cpu' || selectedMetric.value === 'memory') {
    return value.toFixed(1) + '%'
  }

  // For byte-based metrics
  if (selectedMetric.value === 'network' || selectedMetric.value === 'disk') {
    return formatBytes(value) + '/s'
  }

  if (selectedMetric.value === 'memory_bandwidth') {
    return formatBytes(value) + '/s'
  }

  return value.toFixed(2)
}

function formatChange(value) {
  if (value === null || value === undefined) return 'N/A'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(1)}%`
}
</script>
