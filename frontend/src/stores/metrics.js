import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

const MAX_POINTS = 120 // ~10 minutes at 5s interval

function createHistory() {
  return {
    timestamps: [],
    cpuUsage: [],
    memoryUsage: [],
    networkUp: [],
    networkDown: [],
    diskRead: [],
    diskWrite: [],
    // Advanced metrics - perf_events
    ipc: [],
    l1dMissRate: [],
    llcMissRate: [],
    branchMissRate: [],
    dtlbMissRate: [],
    // Advanced metrics - memory_bandwidth
    pageIn: [],
    pageOut: [],
    swapIn: [],
    swapOut: [],
  }
}

export const useMetricsStore = defineStore('metrics', {
  state: () => ({
    status: 'disconnected', // disconnected | connecting | connected | reconnecting
    lastUpdate: null,
    error: null,
    socket: null,
    reconnectTimer: null,
    pingTimer: null,
    metrics: {
      cpu: null,
      memory: null,
      network: null,
      disk: null,
      perf_events: null,
      memory_bandwidth: null,
    },
    history: createHistory(),
  }),

  getters: {
    isConnected: (state) => state.status === 'connected',
  },

  actions: {
    connect() {
      const authStore = useAuthStore()
      const token = authStore.token

      if (!token) {
        this.error = 'Missing auth token'
        this.status = 'disconnected'
        return
      }

      if (this.socket && (this.status === 'connected' || this.status === 'connecting')) {
        return
      }

      this.status = this.status === 'disconnected' ? 'connecting' : 'reconnecting'
      this.error = null

      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const host = window.location.host
      const url = `${protocol}://${host}/api/ws/metrics?token=${token}`

      try {
        const ws = new WebSocket(url)
        this.socket = ws

        ws.onopen = () => {
          this.status = 'connected'
          this.error = null
          this._startPing()
        }

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            if (message.type === 'metrics') {
              this._handleMetrics(message)
            } else if (message.type === 'pong') {
              // no-op
            }
          } catch (err) {
            console.warn('Failed to parse WS message', err)
          }
        }

        ws.onerror = () => {
          this.error = 'WebSocket error'
        }

        ws.onclose = () => {
          this._stopPing()
          this.status = 'reconnecting'
          this._scheduleReconnect()
        }
      } catch (err) {
        this.error = 'Failed to connect WebSocket'
        this.status = 'disconnected'
      }
    },

    disconnect() {
      this._stopPing()
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer)
        this.reconnectTimer = null
      }
      if (this.socket) {
        this.socket.close()
        this.socket = null
      }
      this.status = 'disconnected'
    },

    _scheduleReconnect() {
      if (this.reconnectTimer) return
      this.reconnectTimer = setTimeout(() => {
        this.reconnectTimer = null
        this.connect()
      }, 3000)
    },

    _startPing() {
      this._stopPing()
      this.pingTimer = setInterval(() => {
        if (this.socket && this.status === 'connected') {
          try {
            this.socket.send(JSON.stringify({ type: 'ping' }))
          } catch {
            // ignore send failures
          }
        }
      }, 15000)
    },

    _stopPing() {
      if (this.pingTimer) {
        clearInterval(this.pingTimer)
        this.pingTimer = null
      }
    },

    _handleMetrics(message) {
      const { timestamp, data } = message
      this.metrics = {
        cpu: data.cpu || null,
        memory: data.memory || null,
        network: data.network || null,
        disk: data.disk || null,
        perf_events: data.perf_events || null,
        memory_bandwidth: data.memory_bandwidth || null,
      }
      this.lastUpdate = timestamp

      this._appendHistory(timestamp, data)
    },

    _appendHistory(timestamp, data) {
      const ts = timestamp || new Date().toISOString()
      const { history } = this

      history.timestamps.push(ts)
      history.cpuUsage.push(data.cpu?.usage_percent ?? null)
      history.memoryUsage.push(data.memory?.usage_percent ?? null)
      history.networkUp.push(data.network?.bytes_sent_per_sec ?? null)
      history.networkDown.push(data.network?.bytes_recv_per_sec ?? null)
      history.diskRead.push(data.disk?.io?.read_bytes_per_sec ?? null)
      history.diskWrite.push(data.disk?.io?.write_bytes_per_sec ?? null)

      // Advanced metrics - perf_events (convert rates to percentages for display)
      const perf = data.perf_events
      history.ipc.push(perf?.ipc ?? null)
      history.l1dMissRate.push(perf?.l1d_miss_rate != null ? perf.l1d_miss_rate * 100 : null)
      history.llcMissRate.push(perf?.llc_miss_rate != null ? perf.llc_miss_rate * 100 : null)
      history.branchMissRate.push(perf?.branch_miss_rate != null ? perf.branch_miss_rate * 100 : null)
      history.dtlbMissRate.push(perf?.dtlb_miss_rate != null ? perf.dtlb_miss_rate * 100 : null)

      // Advanced metrics - memory_bandwidth (KB/sec)
      const membw = data.memory_bandwidth
      history.pageIn.push(membw?.pgpgin_per_sec ?? null)
      history.pageOut.push(membw?.pgpgout_per_sec ?? null)
      history.swapIn.push(membw?.pswpin_per_sec ?? null)
      history.swapOut.push(membw?.pswpout_per_sec ?? null)

      if (history.timestamps.length > MAX_POINTS) {
        Object.keys(history).forEach((key) => {
          history[key].shift()
        })
      }
    },
  },
})
