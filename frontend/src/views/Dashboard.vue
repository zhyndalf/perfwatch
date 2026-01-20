<template>
  <div class="p-6 space-y-6">
    <div v-if="metricsStore.error" class="card bg-red-500/10 border-red-500/30">
      <div class="flex items-center gap-3 text-red-400">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ metricsStore.error }}</span>
      </div>
    </div>
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">Dashboard</h1>
        <p class="text-gray-400 text-sm">Real-time metrics update every 5 seconds</p>
      </div>
      <div class="flex items-center gap-3">
        <span
          class="px-3 py-1 rounded-full text-sm font-medium"
          :class="statusBadgeClass"
        >
          {{ statusLabel }}
        </span>
        <div class="text-gray-400 text-sm">
          Last update:
          <span class="text-white">{{ lastUpdateLabel }}</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- CPU -->
      <div class="card space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-white font-semibold">CPU</h2>
            <p class="text-gray-500 text-sm">Overall and per-core load</p>
          </div>
          <div class="text-right">
            <p class="text-3xl font-bold text-accent-cyan">
              {{ formatNumber(metricsStore.metrics.cpu?.usage_percent) ?? 'N/A' }}%
            </p>
            <p class="text-gray-500 text-xs">Per-core max: {{ perCoreMax ?? 'N/A' }}%</p>
          </div>
        </div>
        <VChart :option="cpuOptions" class="h-56" autoresize />
      </div>

      <!-- Memory -->
      <div class="card space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-white font-semibold">Memory</h2>
            <p class="text-gray-500 text-sm">Usage and swap</p>
          </div>
          <div class="text-right">
            <p class="text-3xl font-bold text-accent-green">
              {{ formatNumber(metricsStore.metrics.memory?.usage_percent) ?? 'N/A' }}%
            </p>
            <p class="text-gray-500 text-xs">
              Used: {{ formatBytes(metricsStore.metrics.memory?.used_bytes) }} /
              {{ formatBytes(metricsStore.metrics.memory?.total_bytes) }}
            </p>
          </div>
        </div>
        <VChart :option="memoryOptions" class="h-56" autoresize />
      </div>

      <!-- Network -->
      <div class="card space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-white font-semibold">Network</h2>
            <p class="text-gray-500 text-sm">Throughput (bytes/sec)</p>
          </div>
          <div class="text-right text-sm text-gray-400">
            <p>Up: <span class="text-accent-cyan">{{ formatBytes(metricsStore.metrics.network?.bytes_sent_per_sec) }}/s</span></p>
            <p>Down: <span class="text-accent-purple">{{ formatBytes(metricsStore.metrics.network?.bytes_recv_per_sec) }}/s</span></p>
          </div>
        </div>
        <VChart :option="networkOptions" class="h-56" autoresize />
      </div>

      <!-- Disk -->
      <div class="card space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-white font-semibold">Disk I/O</h2>
            <p class="text-gray-500 text-sm">Read / Write throughput</p>
          </div>
          <div class="text-right text-sm text-gray-400">
            <p>Read: <span class="text-accent-green">{{ formatBytes(metricsStore.metrics.disk?.io?.read_bytes_per_sec) }}/s</span></p>
            <p>Write: <span class="text-amber-300">{{ formatBytes(metricsStore.metrics.disk?.io?.write_bytes_per_sec) }}/s</span></p>
          </div>
        </div>
        <VChart :option="diskOptions" class="h-56" autoresize />
      </div>
    </div>

    <!-- Advanced Metrics Section -->
    <div v-if="hasPerfEvents || hasMemoryBandwidth" class="space-y-4">
      <h2 class="text-xl font-semibold text-white">Advanced Metrics</h2>
      <p class="text-gray-400 text-sm">Hardware performance counters and memory I/O</p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- IPC & Cache Misses -->
        <div v-if="hasPerfEvents" class="card space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-white font-semibold">CPU Performance</h2>
              <p class="text-gray-500 text-sm">IPC and Cache Miss Rates</p>
            </div>
            <div class="text-right">
              <p class="text-2xl font-bold text-blue-400">
                {{ formatNumber(metricsStore.metrics.perf_events?.ipc, 2) ?? 'N/A' }}
                <span class="text-sm font-normal text-gray-400">IPC</span>
              </p>
              <p class="text-gray-500 text-xs">
                L1D: {{ formatPercent(metricsStore.metrics.perf_events?.l1d_miss_rate) }} |
                LLC: {{ formatPercent(metricsStore.metrics.perf_events?.llc_miss_rate) }}
              </p>
            </div>
          </div>
          <VChart :option="perfEventsOptions" class="h-56" autoresize />
        </div>

        <!-- Branch Prediction & TLB -->
        <div v-if="hasPerfEvents" class="card space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-white font-semibold">Branch & TLB</h2>
              <p class="text-gray-500 text-sm">Misprediction and TLB miss rates</p>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-400">
                Branch: <span class="text-rose-400">{{ formatPercent(metricsStore.metrics.perf_events?.branch_miss_rate) }}</span>
              </p>
              <p class="text-sm text-gray-400">
                DTLB: <span class="text-amber-400">{{ formatPercent(metricsStore.metrics.perf_events?.dtlb_miss_rate) }}</span>
              </p>
            </div>
          </div>
          <VChart :option="branchTlbOptions" class="h-56" autoresize />
        </div>

        <!-- Memory Bandwidth - Page I/O -->
        <div v-if="hasMemoryBandwidth" class="card space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-white font-semibold">Memory I/O</h2>
              <p class="text-gray-500 text-sm">Page cache throughput (KB/sec)</p>
            </div>
            <div class="text-right text-sm text-gray-400">
              <p>In: <span class="text-teal-400">{{ formatKB(metricsStore.metrics.memory_bandwidth?.pgpgin_per_sec) }}/s</span></p>
              <p>Out: <span class="text-orange-400">{{ formatKB(metricsStore.metrics.memory_bandwidth?.pgpgout_per_sec) }}/s</span></p>
            </div>
          </div>
          <VChart :option="memoryBandwidthOptions" class="h-56" autoresize />
        </div>

        <!-- Swap Activity -->
        <div v-if="hasMemoryBandwidth" class="card space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-white font-semibold">Swap Activity</h2>
              <p class="text-gray-500 text-sm">Swap in/out (pages/sec)</p>
            </div>
            <div class="text-right text-sm text-gray-400">
              <p>In: <span class="text-pink-400">{{ formatNumber(metricsStore.metrics.memory_bandwidth?.pswpin_per_sec, 1) ?? '0' }}</span></p>
              <p>Out: <span class="text-violet-400">{{ formatNumber(metricsStore.metrics.memory_bandwidth?.pswpout_per_sec, 1) ?? '0' }}</span></p>
            </div>
          </div>
          <VChart :option="swapOptions" class="h-56" autoresize />
        </div>
      </div>
    </div>

    <!-- Perf Events Unavailable Notice -->
    <div v-if="perfEventsUnavailable" class="card bg-dark-card/50 border-dashed">
      <div class="flex items-center gap-3 text-gray-400">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="text-sm font-medium">Hardware Performance Counters Unavailable</p>
          <p class="text-xs text-gray-500">perf_events requires elevated privileges or kernel support</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { use } from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { useMetricsStore } from '@/stores/metrics'

use([GridComponent, TooltipComponent, LegendComponent, TitleComponent, LineChart, BarChart, CanvasRenderer])

const metricsStore = useMetricsStore()

onMounted(() => {
  metricsStore.connect()
})

onUnmounted(() => {
  metricsStore.disconnect()
})

const statusLabel = computed(() => {
  const map = {
    connected: 'Connected',
    connecting: 'Connecting',
    reconnecting: 'Reconnecting',
    disconnected: 'Disconnected',
  }
  return map[metricsStore.status] || 'Disconnected'
})

const statusBadgeClass = computed(() => {
  switch (metricsStore.status) {
    case 'connected':
      return 'bg-accent-green/20 text-accent-green border border-accent-green/40'
    case 'connecting':
      return 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/40'
    case 'reconnecting':
      return 'bg-amber-500/20 text-amber-300 border border-amber-300/40'
    default:
      return 'bg-dark-border text-gray-400 border border-dark-border'
  }
})

const lastUpdateLabel = computed(() => {
  if (!metricsStore.lastUpdate) return 'Waiting...'
  return new Date(metricsStore.lastUpdate).toLocaleTimeString()
})

const trimmedTimestamps = computed(() =>
  metricsStore.history.timestamps.slice(-60).map((ts) => new Date(ts).toLocaleTimeString())
)

const perCoreMax = computed(() => {
  const cores = metricsStore.metrics.cpu?.per_core
  if (!cores || !cores.length) return null
  return Math.max(...cores.map((v) => Number(v) || 0)).toFixed(1)
})

// Advanced metrics availability
const hasPerfEvents = computed(() => {
  return metricsStore.metrics.perf_events?.available === true
})

const hasMemoryBandwidth = computed(() => {
  return metricsStore.metrics.memory_bandwidth?.available === true
})

const perfEventsUnavailable = computed(() => {
  // Show notice if we received perf_events data but it's unavailable
  const perf = metricsStore.metrics.perf_events
  return perf && perf.available === false
})

const cpuOptions = computed(() => ({
  grid: { left: 40, right: 10, top: 20, bottom: 30 },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: trimmedTimestamps.value,
    axisLabel: { color: '#e2e8f0' },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  yAxis: {
    type: 'value',
    axisLabel: { formatter: '{value}%', color: '#e2e8f0' },
    splitLine: { lineStyle: { color: '#334155' } },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  series: [
    {
      name: 'CPU Usage',
      type: 'line',
      areaStyle: { opacity: 0.15 },
      showSymbol: false,
      data: metricsStore.history.cpuUsage.slice(-60),
      lineStyle: { color: '#3b82f6' },
    },
  ],
}))

const memoryOptions = computed(() => ({
  grid: { left: 40, right: 10, top: 20, bottom: 30 },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: trimmedTimestamps.value,
    axisLabel: { color: '#e2e8f0' },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  yAxis: {
    type: 'value',
    axisLabel: { formatter: '{value}%', color: '#e2e8f0' },
    splitLine: { lineStyle: { color: '#334155' } },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  series: [
    {
      name: 'Memory Usage',
      type: 'line',
      showSymbol: false,
      areaStyle: { opacity: 0.15 },
      data: metricsStore.history.memoryUsage.slice(-60),
      lineStyle: { color: '#22c55e' },
    },
  ],
}))

const networkOptions = computed(() => ({
  grid: { left: 50, right: 10, top: 20, bottom: 30 },
  tooltip: {
    trigger: 'axis',
    valueFormatter: (value) => formatBytes(value) + '/s',
  },
  legend: { data: ['Upload', 'Download'], textStyle: { color: '#e2e8f0' } },
  xAxis: {
    type: 'category',
    data: trimmedTimestamps.value,
    axisLabel: { color: '#e2e8f0' },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  yAxis: {
    type: 'value',
    axisLabel: { formatter: (val) => `${formatThroughput(val)}`, color: '#e2e8f0' },
    splitLine: { lineStyle: { color: '#334155' } },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  series: [
    {
      name: 'Upload',
      type: 'line',
      showSymbol: false,
      data: metricsStore.history.networkUp.slice(-60),
      lineStyle: { color: '#06b6d4' },
    },
    {
      name: 'Download',
      type: 'line',
      showSymbol: false,
      data: metricsStore.history.networkDown.slice(-60),
      lineStyle: { color: '#a855f7' },
    },
  ],
}))

const diskOptions = computed(() => ({
  grid: { left: 50, right: 10, top: 20, bottom: 30 },
  tooltip: {
    trigger: 'axis',
    valueFormatter: (value) => formatBytes(value) + '/s',
  },
  legend: { data: ['Read', 'Write'], textStyle: { color: '#e2e8f0' } },
  xAxis: {
    type: 'category',
    data: trimmedTimestamps.value,
    axisLabel: { color: '#e2e8f0' },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  yAxis: {
    type: 'value',
    axisLabel: { formatter: (val) => `${formatThroughput(val)}`, color: '#e2e8f0' },
    splitLine: { lineStyle: { color: '#334155' } },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  series: [
    {
      name: 'Read',
      type: 'line',
      showSymbol: false,
      data: metricsStore.history.diskRead.slice(-60),
      lineStyle: { color: '#22c55e' },
    },
    {
      name: 'Write',
      type: 'line',
      showSymbol: false,
      data: metricsStore.history.diskWrite.slice(-60),
      lineStyle: { color: '#f97316' },
    },
  ],
}))

// Advanced Metrics Chart Options
const perfEventsOptions = computed(() => ({
  grid: { left: 50, right: 10, top: 30, bottom: 30 },
  tooltip: { trigger: 'axis' },
  legend: { data: ['IPC', 'L1D Miss %', 'LLC Miss %'], top: 0, textStyle: { color: '#e2e8f0' } },
  xAxis: {
    type: 'category',
    data: trimmedTimestamps.value,
    axisLabel: { color: '#e2e8f0' },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  yAxis: [
    {
      type: 'value',
      name: 'IPC',
      position: 'left',
      max: 3,
      axisLabel: { formatter: '{value}', color: '#e2e8f0' },
      splitLine: { lineStyle: { color: '#334155' } },
      axisLine: { lineStyle: { color: '#475569' } },
    },
    {
      type: 'value',
      name: 'Miss %',
      position: 'right',
      max: 100,
      axisLabel: { formatter: '{value}%', color: '#e2e8f0' },
      splitLine: { show: false },
      axisLine: { lineStyle: { color: '#475569' } },
    },
  ],
  series: [
    {
      name: 'IPC',
      type: 'line',
      showSymbol: false,
      yAxisIndex: 0,
      data: metricsStore.history.ipc.slice(-60),
      lineStyle: { color: '#3b82f6' },
      areaStyle: { opacity: 0.1 },
    },
    {
      name: 'L1D Miss %',
      type: 'line',
      showSymbol: false,
      yAxisIndex: 1,
      data: metricsStore.history.l1dMissRate.slice(-60),
      lineStyle: { color: '#22c55e' },
    },
    {
      name: 'LLC Miss %',
      type: 'line',
      showSymbol: false,
      yAxisIndex: 1,
      data: metricsStore.history.llcMissRate.slice(-60),
      lineStyle: { color: '#f59e0b' },
    },
  ],
}))

const branchTlbOptions = computed(() => ({
  grid: { left: 50, right: 10, top: 30, bottom: 30 },
  tooltip: {
    trigger: 'axis',
    valueFormatter: (value) => value != null ? value.toFixed(3) + '%' : 'N/A',
  },
  legend: { data: ['Branch Miss %', 'DTLB Miss %'], top: 0, textStyle: { color: '#e2e8f0' } },
  xAxis: {
    type: 'category',
    data: trimmedTimestamps.value,
    axisLabel: { color: '#e2e8f0' },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  yAxis: {
    type: 'value',
    axisLabel: { formatter: '{value}%', color: '#e2e8f0' },
    splitLine: { lineStyle: { color: '#334155' } },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  series: [
    {
      name: 'Branch Miss %',
      type: 'line',
      showSymbol: false,
      data: metricsStore.history.branchMissRate.slice(-60),
      lineStyle: { color: '#f43f5e' },
      areaStyle: { opacity: 0.1 },
    },
    {
      name: 'DTLB Miss %',
      type: 'line',
      showSymbol: false,
      data: metricsStore.history.dtlbMissRate.slice(-60),
      lineStyle: { color: '#f59e0b' },
      areaStyle: { opacity: 0.1 },
    },
  ],
}))

const memoryBandwidthOptions = computed(() => ({
  grid: { left: 50, right: 10, top: 30, bottom: 30 },
  tooltip: {
    trigger: 'axis',
    valueFormatter: (value) => formatKB(value) + '/s',
  },
  legend: { data: ['Page In', 'Page Out'], top: 0, textStyle: { color: '#e2e8f0' } },
  xAxis: {
    type: 'category',
    data: trimmedTimestamps.value,
    axisLabel: { color: '#e2e8f0' },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  yAxis: {
    type: 'value',
    axisLabel: { formatter: (val) => formatKB(val), color: '#e2e8f0' },
    splitLine: { lineStyle: { color: '#334155' } },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  series: [
    {
      name: 'Page In',
      type: 'line',
      showSymbol: false,
      data: metricsStore.history.pageIn.slice(-60),
      lineStyle: { color: '#14b8a6' },
      areaStyle: { opacity: 0.1 },
    },
    {
      name: 'Page Out',
      type: 'line',
      showSymbol: false,
      data: metricsStore.history.pageOut.slice(-60),
      lineStyle: { color: '#f97316' },
      areaStyle: { opacity: 0.1 },
    },
  ],
}))

const swapOptions = computed(() => ({
  grid: { left: 50, right: 10, top: 30, bottom: 30 },
  tooltip: {
    trigger: 'axis',
    valueFormatter: (value) => (value != null ? value.toFixed(1) : '0') + ' pages/s',
  },
  legend: { data: ['Swap In', 'Swap Out'], top: 0, textStyle: { color: '#e2e8f0' } },
  xAxis: {
    type: 'category',
    data: trimmedTimestamps.value,
    axisLabel: { color: '#e2e8f0' },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  yAxis: {
    type: 'value',
    axisLabel: { formatter: '{value}', color: '#e2e8f0' },
    splitLine: { lineStyle: { color: '#334155' } },
    axisLine: { lineStyle: { color: '#475569' } },
  },
  series: [
    {
      name: 'Swap In',
      type: 'line',
      showSymbol: false,
      data: metricsStore.history.swapIn.slice(-60),
      lineStyle: { color: '#ec4899' },
      areaStyle: { opacity: 0.1 },
    },
    {
      name: 'Swap Out',
      type: 'line',
      showSymbol: false,
      data: metricsStore.history.swapOut.slice(-60),
      lineStyle: { color: '#8b5cf6' },
      areaStyle: { opacity: 0.1 },
    },
  ],
}))

function formatNumber(value, decimals = 1) {
  if (value === null || value === undefined) return null
  return Number(value).toFixed(decimals)
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

function formatThroughput(value) {
  if (value === null || value === undefined) return '0 B/s'
  return `${formatBytes(value)}/s`
}

function formatPercent(value) {
  if (value === null || value === undefined) return 'N/A'
  return (Number(value) * 100).toFixed(2) + '%'
}

function formatKB(value) {
  if (value === null || value === undefined) return 'N/A'
  const kb = Number(value)
  if (Number.isNaN(kb)) return 'N/A'
  if (kb === 0) return '0 KB'
  if (kb < 1024) return kb.toFixed(1) + ' KB'
  if (kb < 1024 * 1024) return (kb / 1024).toFixed(1) + ' MB'
  return (kb / (1024 * 1024)).toFixed(1) + ' GB'
}
</script>
