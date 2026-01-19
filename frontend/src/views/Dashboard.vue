<template>
  <div class="p-6 space-y-6">
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

const cpuOptions = computed(() => ({
  grid: { left: 40, right: 10, top: 20, bottom: 30 },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: trimmedTimestamps.value },
  yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
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
  xAxis: { type: 'category', data: trimmedTimestamps.value },
  yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
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
  legend: { data: ['Upload', 'Download'] },
  xAxis: { type: 'category', data: trimmedTimestamps.value },
  yAxis: { type: 'value', axisLabel: { formatter: (val) => `${formatThroughput(val)}` } },
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
  legend: { data: ['Read', 'Write'] },
  xAxis: { type: 'category', data: trimmedTimestamps.value },
  yAxis: { type: 'value', axisLabel: { formatter: (val) => `${formatThroughput(val)}` } },
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

function formatNumber(value) {
  if (value === null || value === undefined) return null
  return Number(value).toFixed(1)
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
</script>
