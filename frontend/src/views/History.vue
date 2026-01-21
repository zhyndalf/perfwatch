<template>
  <div class="p-6 space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">History</h1>
        <p class="text-gray-400 text-sm">Load two time ranges and compare them</p>
      </div>
      <div class="min-w-[180px]">
        <label class="block text-sm font-medium text-gray-400 mb-2">Metric Type</label>
        <select
          v-model="metricType"
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
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <div class="card space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-white font-semibold">Dataset A</h2>
          <span v-if="historyStore.datasetA.count" class="text-xs text-gray-400">
            {{ historyStore.datasetA.count }} points
            <span v-if="historyStore.datasetA.interval">• {{ historyStore.datasetA.interval }}</span>
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">Start Time</label>
            <input
              v-model="startTimeA"
              type="datetime-local"
              class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-cyan"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">End Time</label>
            <input
              v-model="endTimeA"
              type="datetime-local"
              class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-cyan"
            />
          </div>
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            @click="setLastHours('A', 1)"
            class="px-3 py-2 text-sm bg-dark-bg border border-dark-border rounded-lg text-gray-300 hover:text-white hover:border-accent-cyan transition-colors"
          >
            1h
          </button>
          <button
            @click="setLastHours('A', 6)"
            class="px-3 py-2 text-sm bg-dark-bg border border-dark-border rounded-lg text-gray-300 hover:text-white hover:border-accent-cyan transition-colors"
          >
            6h
          </button>
          <button
            @click="setLastHours('A', 24)"
            class="px-3 py-2 text-sm bg-dark-bg border border-dark-border rounded-lg text-gray-300 hover:text-white hover:border-accent-cyan transition-colors"
          >
            24h
          </button>
        </div>

        <button
          @click="loadDataset('A')"
          :disabled="historyStore.loadingA || !canLoadA"
          class="px-6 py-2 bg-accent-cyan text-dark-bg font-semibold rounded-lg hover:bg-accent-cyan/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="historyStore.loadingA" class="flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Loading...
          </span>
          <span v-else>Load Dataset A</span>
        </button>

        <div v-if="historyStore.errorA" class="text-sm text-red-400">
          {{ historyStore.errorA }}
        </div>
      </div>

      <div class="card space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-white font-semibold">Dataset B</h2>
          <span v-if="historyStore.datasetB.count" class="text-xs text-gray-400">
            {{ historyStore.datasetB.count }} points
            <span v-if="historyStore.datasetB.interval">• {{ historyStore.datasetB.interval }}</span>
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">Start Time</label>
            <input
              v-model="startTimeB"
              type="datetime-local"
              class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-cyan"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-2">End Time</label>
            <input
              v-model="endTimeB"
              type="datetime-local"
              class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-cyan"
            />
          </div>
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            @click="setLastHours('B', 1)"
            class="px-3 py-2 text-sm bg-dark-bg border border-dark-border rounded-lg text-gray-300 hover:text-white hover:border-accent-cyan transition-colors"
          >
            1h
          </button>
          <button
            @click="setLastHours('B', 6)"
            class="px-3 py-2 text-sm bg-dark-bg border border-dark-border rounded-lg text-gray-300 hover:text-white hover:border-accent-cyan transition-colors"
          >
            6h
          </button>
          <button
            @click="setLastHours('B', 24)"
            class="px-3 py-2 text-sm bg-dark-bg border border-dark-border rounded-lg text-gray-300 hover:text-white hover:border-accent-cyan transition-colors"
          >
            24h
          </button>
        </div>

        <button
          @click="loadDataset('B')"
          :disabled="historyStore.loadingB || !canLoadB"
          class="px-6 py-2 bg-accent-cyan text-dark-bg font-semibold rounded-lg hover:bg-accent-cyan/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="historyStore.loadingB" class="flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Loading...
          </span>
          <span v-else>Load Dataset B</span>
        </button>

        <div v-if="historyStore.errorB" class="text-sm text-red-400">
          {{ historyStore.errorB }}
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <div class="card">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-white font-semibold">Dataset A Chart</h2>
          <span class="text-xs text-gray-400">{{ datasetATimeLabel }}</span>
        </div>
        <div v-if="!historyStore.hasA && !historyStore.loadingA" class="h-72 flex items-center justify-center text-gray-500">
          No data loaded for Dataset A
        </div>
        <div v-else-if="historyStore.loadingA" class="h-72 flex items-center justify-center text-gray-400">
          Loading...
        </div>
        <VChart v-else :option="datasetAOptions" class="h-72" autoresize />
      </div>

      <div class="card">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-white font-semibold">Dataset B Chart</h2>
          <span class="text-xs text-gray-400">{{ datasetBTimeLabel }}</span>
        </div>
        <div v-if="!historyStore.hasB && !historyStore.loadingB" class="h-72 flex items-center justify-center text-gray-500">
          No data loaded for Dataset B
        </div>
        <div v-else-if="historyStore.loadingB" class="h-72 flex items-center justify-center text-gray-400">
          Loading...
        </div>
        <VChart v-else :option="datasetBOptions" class="h-72" autoresize />
      </div>
    </div>

    <div class="card space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-white font-semibold">Comparison Charts</h2>
        <span class="text-xs text-gray-400">{{ comparisonLabel }}</span>
      </div>
      <div v-if="!historyStore.hasA || !historyStore.hasB" class="h-72 flex items-center justify-center text-gray-500">
        Load both datasets to compare
      </div>
      <div v-else class="space-y-4">
        <div v-for="chart in comparisonCharts" :key="chart.title" class="border border-dark-border rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-white font-semibold">{{ chart.title }}</h3>
            <span class="text-xs text-gray-400">{{ chart.subtitle }}</span>
          </div>
          <VChart :option="chart.options" class="h-64" autoresize />
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="card space-y-2">
        <h3 class="text-white font-semibold">Dataset A Summary</h3>
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <p class="text-gray-400 text-xs">Min</p>
            <p class="text-lg font-bold text-accent-green">{{ formatValue(statsA.min) }}</p>
          </div>
          <div>
            <p class="text-gray-400 text-xs">Max</p>
            <p class="text-lg font-bold text-accent-cyan">{{ formatValue(statsA.max) }}</p>
          </div>
          <div>
            <p class="text-gray-400 text-xs">Avg</p>
            <p class="text-lg font-bold text-accent-purple">{{ formatValue(statsA.avg) }}</p>
          </div>
        </div>
      </div>

      <div class="card space-y-2">
        <h3 class="text-white font-semibold">Dataset B Summary</h3>
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <p class="text-gray-400 text-xs">Min</p>
            <p class="text-lg font-bold text-accent-green">{{ formatValue(statsB.min) }}</p>
          </div>
          <div>
            <p class="text-gray-400 text-xs">Max</p>
            <p class="text-lg font-bold text-accent-cyan">{{ formatValue(statsB.max) }}</p>
          </div>
          <div>
            <p class="text-gray-400 text-xs">Avg</p>
            <p class="text-lg font-bold text-accent-purple">{{ formatValue(statsB.avg) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { useHistoryStore } from '@/stores/history'

use([GridComponent, TooltipComponent, LegendComponent, DataZoomComponent, LineChart, CanvasRenderer])

const historyStore = useHistoryStore()

const metricType = computed({
  get: () => historyStore.metricType,
  set: (value) => historyStore.setMetricType(value),
})

const startTimeA = ref('')
const endTimeA = ref('')
const startTimeB = ref('')
const endTimeB = ref('')

onMounted(() => {
  setLastHours('A', 1)
  setLastHours('B', 1)
})

const canLoadA = computed(() => startTimeA.value && endTimeA.value)
const canLoadB = computed(() => startTimeB.value && endTimeB.value)

const datasetATimeLabel = computed(() => formatRange(historyStore.datasetA))
const datasetBTimeLabel = computed(() => formatRange(historyStore.datasetB))

const datasetAOptions = computed(() =>
  buildDatasetOptions(historyStore.datasetA.dataPoints, metricType.value, 'Dataset A')
)

const datasetBOptions = computed(() =>
  buildDatasetOptions(historyStore.datasetB.dataPoints, metricType.value, 'Dataset B')
)

const comparisonLabel = computed(() => {
  if (!historyStore.hasA || !historyStore.hasB) return ''
  return 'Aligned by relative time from each start'
})

const comparisonCharts = computed(() => {
  return buildComparisonCharts(
    historyStore.datasetA.dataPoints,
    historyStore.datasetB.dataPoints,
    metricType.value
  )
})

const statsA = computed(() => buildStats(historyStore.datasetA.dataPoints, metricType.value))
const statsB = computed(() => buildStats(historyStore.datasetB.dataPoints, metricType.value))

function setLastHours(which, hours) {
  const end = new Date()
  const start = new Date(end.getTime() - hours * 60 * 60 * 1000)
  const startValue = formatDateTimeLocal(start)
  const endValue = formatDateTimeLocal(end)

  if (which === 'A') {
    startTimeA.value = startValue
    endTimeA.value = endValue
    return
  }
  startTimeB.value = startValue
  endTimeB.value = endValue
}

async function loadDataset(which) {
  const startValue = which === 'A' ? startTimeA.value : startTimeB.value
  const endValue = which === 'A' ? endTimeA.value : endTimeB.value
  const startDate = new Date(startValue)
  const endDate = new Date(endValue)

  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    historyStore[which === 'A' ? 'errorA' : 'errorB'] = 'Please provide valid start and end times.'
    return
  }
  if (startDate >= endDate) {
    historyStore[which === 'A' ? 'errorA' : 'errorB'] = 'Start time must be before end time.'
    return
  }

  await historyStore.loadDataset(which, startDate.toISOString(), endDate.toISOString())
}

function formatDateTimeLocal(date) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function formatRange(dataset) {
  if (!dataset.startTime || !dataset.endTime) return ''
  const start = new Date(dataset.startTime)
  const end = new Date(dataset.endTime)
  return `${start.toLocaleString()} - ${end.toLocaleString()}`
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
  if (metricType.value === 'cpu' || metricType.value === 'memory') {
    return value.toFixed(1) + '%'
  }
  if (metricType.value === 'network' || metricType.value === 'disk' || metricType.value === 'memory_bandwidth') {
    return formatBytes(value) + '/s'
  }
  return value.toFixed(2)
}

function buildDatasetOptions(points, type, label) {
  const timestamps = points.map((point) => new Date(point.timestamp).toLocaleTimeString())
  const baseOptions = {
    grid: { left: 64, right: 32, top: 40, bottom: 80, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(30, 30, 35, 0.95)',
      borderColor: '#3b3b45',
      textStyle: { color: '#f8fafc' },
    },
    xAxis: {
      type: 'category',
      data: timestamps,
      axisLabel: { color: '#e2e8f0', rotate: 45, margin: 12 },
      axisLine: { lineStyle: { color: '#475569' } },
    },
    dataZoom: [
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
    ],
    legend: { textStyle: { color: '#e2e8f0' } },
  }

  if (type === 'cpu') {
    return {
      ...baseOptions,
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: { formatter: '{value}%', color: '#e2e8f0', margin: 10 },
        splitLine: { lineStyle: { color: '#334155' } },
        axisLine: { lineStyle: { color: '#475569' } },
      },
      series: [
        {
          name: `${label} CPU Usage`,
          type: 'line',
          showSymbol: false,
          areaStyle: { opacity: 0.15, color: '#3b82f6' },
          lineStyle: { color: '#3b82f6', width: 2 },
          data: points.map((point) => point.data?.usage_percent ?? null),
        },
      ],
    }
  }

  if (type === 'memory') {
    return {
      ...baseOptions,
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: { formatter: '{value}%', color: '#e2e8f0', margin: 10 },
        splitLine: { lineStyle: { color: '#334155' } },
        axisLine: { lineStyle: { color: '#475569' } },
      },
      series: [
        {
          name: `${label} Memory Usage`,
          type: 'line',
          showSymbol: false,
          areaStyle: { opacity: 0.15, color: '#22c55e' },
          lineStyle: { color: '#22c55e', width: 2 },
          data: points.map((point) => point.data?.usage_percent ?? null),
        },
      ],
    }
  }

  if (type === 'network') {
    return {
      ...baseOptions,
      legend: {
        data: ['Download', 'Upload'],
        textStyle: { color: '#e2e8f0' },
      },
      yAxis: {
        type: 'value',
        axisLabel: { formatter: (val) => formatBytes(val) + '/s', color: '#e2e8f0', margin: 10 },
        splitLine: { lineStyle: { color: '#334155' } },
        axisLine: { lineStyle: { color: '#475569' } },
      },
      series: [
        {
          name: 'Download',
          type: 'line',
          showSymbol: false,
          lineStyle: { color: '#a855f7', width: 2 },
          data: points.map((point) => point.data?.bytes_recv_per_sec ?? null),
        },
        {
          name: 'Upload',
          type: 'line',
          showSymbol: false,
          lineStyle: { color: '#06b6d4', width: 2 },
          data: points.map((point) => point.data?.bytes_sent_per_sec ?? null),
        },
      ],
    }
  }

  if (type === 'disk') {
    return {
      ...baseOptions,
      legend: {
        data: ['Read', 'Write'],
        textStyle: { color: '#e2e8f0' },
      },
      yAxis: {
        type: 'value',
        axisLabel: { formatter: (val) => formatBytes(val) + '/s', color: '#e2e8f0', margin: 10 },
        splitLine: { lineStyle: { color: '#334155' } },
        axisLine: { lineStyle: { color: '#475569' } },
      },
      series: [
        {
          name: 'Read',
          type: 'line',
          showSymbol: false,
          lineStyle: { color: '#22c55e', width: 2 },
          data: points.map((point) => point.data?.io?.read_bytes_per_sec ?? null),
        },
        {
          name: 'Write',
          type: 'line',
          showSymbol: false,
          lineStyle: { color: '#f97316', width: 2 },
          data: points.map((point) => point.data?.io?.write_bytes_per_sec ?? null),
        },
      ],
    }
  }

  if (type === 'perf_events') {
    return {
      ...baseOptions,
      legend: {
        data: ['IPC', 'L1D Miss %', 'LLC Miss %'],
        textStyle: { color: '#e2e8f0' },
      },
      grid: { ...baseOptions.grid, right: 48 },
      yAxis: [
        {
          type: 'value',
          name: 'IPC',
          axisLabel: { color: '#e2e8f0', margin: 10 },
          splitLine: { lineStyle: { color: '#334155' } },
          axisLine: { lineStyle: { color: '#475569' } },
        },
        {
          type: 'value',
          name: 'Miss %',
          min: 0,
          max: 100,
          axisLabel: { formatter: '{value}%', color: '#e2e8f0', margin: 10 },
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
          data: points.map((point) => point.data?.ipc ?? null),
        },
        {
          name: 'L1D Miss %',
          type: 'line',
          showSymbol: false,
          yAxisIndex: 1,
          lineStyle: { color: '#f97316', width: 2 },
          data: points.map((point) =>
            point.data?.l1d_miss_rate != null ? point.data.l1d_miss_rate * 100 : null
          ),
        },
        {
          name: 'LLC Miss %',
          type: 'line',
          showSymbol: false,
          yAxisIndex: 1,
          lineStyle: { color: '#a855f7', width: 2 },
          data: points.map((point) =>
            point.data?.llc_miss_rate != null ? point.data.llc_miss_rate * 100 : null
          ),
        },
      ],
    }
  }

  if (type === 'memory_bandwidth') {
    return {
      ...baseOptions,
      legend: {
        data: ['Page I/O', 'Swap I/O'],
        textStyle: { color: '#e2e8f0' },
      },
      yAxis: {
        type: 'value',
        axisLabel: { formatter: (val) => formatBytes(val) + '/s', color: '#e2e8f0', margin: 10 },
        splitLine: { lineStyle: { color: '#334155' } },
        axisLine: { lineStyle: { color: '#475569' } },
      },
      series: [
        {
          name: 'Page I/O',
          type: 'line',
          showSymbol: false,
          lineStyle: { color: '#22c55e', width: 2 },
          data: points.map((point) => point.data?.page_io_bytes_per_sec ?? null),
        },
        {
          name: 'Swap I/O',
          type: 'line',
          showSymbol: false,
          lineStyle: { color: '#f59e0b', width: 2 },
          data: points.map((point) => point.data?.swap_io_bytes_per_sec ?? null),
        },
      ],
    }
  }

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
        name: label,
        type: 'line',
        showSymbol: false,
        lineStyle: { color: '#3b82f6', width: 2 },
        data: points.map((point) => point.data?.value ?? null),
      },
    ],
  }
}

function buildPrimaryValue(point, type) {
  if (!point?.data) return null
  if (type === 'cpu' || type === 'memory') {
    return point.data?.usage_percent ?? null
  }
  if (type === 'network') {
    const sent = point.data?.bytes_sent_per_sec ?? 0
    const recv = point.data?.bytes_recv_per_sec ?? 0
    return sent + recv
  }
  if (type === 'disk') {
    const read = point.data?.io?.read_bytes_per_sec ?? 0
    const write = point.data?.io?.write_bytes_per_sec ?? 0
    return read + write
  }
  if (type === 'perf_events') {
    return point.data?.ipc ?? null
  }
  if (type === 'memory_bandwidth') {
    const page = point.data?.page_io_bytes_per_sec ?? 0
    const swap = point.data?.swap_io_bytes_per_sec ?? 0
    return page + swap
  }
  return null
}

function buildComparisonCharts(pointsA, pointsB, type) {
  const seriesList = getComparisonSeries(type)
  return seriesList.map((series) => {
    const seriesA = buildRelativeSeries(pointsA, series.extractor)
    const seriesB = buildRelativeSeries(pointsB, series.extractor)
    const offsets = Array.from(new Set([...seriesA.offsets, ...seriesB.offsets])).sort((a, b) => a - b)
    const labels = offsets.map((offset) => formatOffset(offset))
    const valuesA = offsets.map((offset) => (seriesA.map.has(offset) ? seriesA.map.get(offset) : null))
    const valuesB = offsets.map((offset) => (seriesB.map.has(offset) ? seriesB.map.get(offset) : null))

    return {
      title: series.title,
      subtitle: series.subtitle,
      options: {
        grid: { left: 64, right: 32, top: 32, bottom: 70, containLabel: true },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(30, 30, 35, 0.95)',
          borderColor: '#3b3b45',
          textStyle: { color: '#f8fafc' },
        },
        legend: {
          data: ['Dataset A', 'Dataset B'],
          textStyle: { color: '#e2e8f0' },
        },
        xAxis: {
          type: 'category',
          data: labels,
          axisLabel: { color: '#e2e8f0', rotate: 45, margin: 12 },
          axisLine: { lineStyle: { color: '#475569' } },
        },
        yAxis: buildComparisonAxis(series.axisType),
        series: [
          {
            name: 'Dataset A',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#3b82f6', width: 2 },
            data: valuesA,
          },
          {
            name: 'Dataset B',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#f97316', width: 2 },
            data: valuesB,
          },
        ],
      },
    }
  })
}

function buildComparisonAxis(axisType) {
  if (axisType === 'percent') {
    return {
      type: 'value',
      max: 100,
      axisLabel: { formatter: '{value}%', color: '#e2e8f0', margin: 10 },
      splitLine: { lineStyle: { color: '#334155' } },
      axisLine: { lineStyle: { color: '#475569' } },
    }
  }
  if (axisType === 'bytes_per_sec') {
    return {
      type: 'value',
      axisLabel: { formatter: (val) => formatBytes(val) + '/s', color: '#e2e8f0', margin: 10 },
      splitLine: { lineStyle: { color: '#334155' } },
      axisLine: { lineStyle: { color: '#475569' } },
    }
  }
  return {
    type: 'value',
    axisLabel: { color: '#e2e8f0', margin: 10 },
    splitLine: { lineStyle: { color: '#334155' } },
    axisLine: { lineStyle: { color: '#475569' } },
  }
}

function buildRelativeSeries(points, extractor) {
  if (!points.length) {
    return { offsets: [], map: new Map() }
  }
  const start = new Date(points[0].timestamp).getTime()
  const offsets = []
  const map = new Map()
  for (const point of points) {
    const current = new Date(point.timestamp).getTime()
    if (Number.isNaN(current)) continue
    const offset = Math.round((current - start) / 1000)
    offsets.push(offset)
    map.set(offset, extractor(point))
  }
  return { offsets, map }
}

function formatOffset(offsetSeconds) {
  const abs = Math.abs(offsetSeconds)
  const hours = Math.floor(abs / 3600)
  const minutes = Math.floor((abs % 3600) / 60)
  if (hours > 0) {
    return `${hours}h ${String(minutes).padStart(2, '0')}m`
  }
  return `${minutes}m`
}

function buildStats(points, type) {
  const values = points
    .map((point) => buildPrimaryValue(point, type))
    .filter((value) => value !== null && value !== undefined)
  if (!values.length) {
    return { min: null, max: null, avg: null }
  }
  const min = Math.min(...values)
  const max = Math.max(...values)
  const avg = values.reduce((sum, value) => sum + value, 0) / values.length
  return { min, max, avg }
}

function getComparisonSeries(type) {
  if (type === 'network') {
    return [
      {
        title: 'Network Download',
        subtitle: 'Bytes received per second',
        axisType: 'bytes_per_sec',
        extractor: (point) => point.data?.bytes_recv_per_sec ?? null,
      },
      {
        title: 'Network Upload',
        subtitle: 'Bytes sent per second',
        axisType: 'bytes_per_sec',
        extractor: (point) => point.data?.bytes_sent_per_sec ?? null,
      },
    ]
  }

  if (type === 'disk') {
    return [
      {
        title: 'Disk Read',
        subtitle: 'Read bytes per second',
        axisType: 'bytes_per_sec',
        extractor: (point) => point.data?.io?.read_bytes_per_sec ?? null,
      },
      {
        title: 'Disk Write',
        subtitle: 'Write bytes per second',
        axisType: 'bytes_per_sec',
        extractor: (point) => point.data?.io?.write_bytes_per_sec ?? null,
      },
    ]
  }

  if (type === 'memory_bandwidth') {
    return [
      {
        title: 'Page I/O',
        subtitle: 'Page I/O bytes per second',
        axisType: 'bytes_per_sec',
        extractor: (point) => point.data?.page_io_bytes_per_sec ?? null,
      },
      {
        title: 'Swap I/O',
        subtitle: 'Swap I/O bytes per second',
        axisType: 'bytes_per_sec',
        extractor: (point) => point.data?.swap_io_bytes_per_sec ?? null,
      },
    ]
  }

  if (type === 'perf_events') {
    return [
      {
        title: 'IPC',
        subtitle: 'Instructions per cycle',
        axisType: 'number',
        extractor: (point) => point.data?.ipc ?? null,
      },
      {
        title: 'L1D Miss Rate',
        subtitle: 'L1D miss percentage',
        axisType: 'percent',
        extractor: (point) =>
          point.data?.l1d_miss_rate != null ? point.data.l1d_miss_rate * 100 : null,
      },
      {
        title: 'LLC Miss Rate',
        subtitle: 'LLC miss percentage',
        axisType: 'percent',
        extractor: (point) =>
          point.data?.llc_miss_rate != null ? point.data.llc_miss_rate * 100 : null,
      },
    ]
  }

  if (type === 'cpu') {
    return [
      {
        title: 'CPU Usage',
        subtitle: 'Usage percent',
        axisType: 'percent',
        extractor: (point) => point.data?.usage_percent ?? null,
      },
    ]
  }

  if (type === 'memory') {
    return [
      {
        title: 'Memory Usage',
        subtitle: 'Usage percent',
        axisType: 'percent',
        extractor: (point) => point.data?.usage_percent ?? null,
      },
    ]
  }

  return [
    {
      title: 'Value',
      subtitle: 'Metric value',
      axisType: 'number',
      extractor: (point) => buildPrimaryValue(point, type),
    },
  ]
}
</script>
