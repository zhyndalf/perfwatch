import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token')
      // Only redirect if not already on login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api

// Auth API functions
export const authApi = {
  login: (username, password) => {
    return api.post('/auth/login', { username, password })
  },

  me: () => api.get('/auth/me'),

  changePassword: (currentPassword, newPassword) =>
    api.put('/auth/password', {
      current_password: currentPassword,
      new_password: newPassword,
    }),
}

// History API functions
export const historyApi = {
  /**
   * Get historical metrics data
   * @param {string} metricType - One of: cpu, memory, network, disk, perf_events, memory_bandwidth
   * @param {string} startTime - ISO 8601 datetime string
   * @param {string} endTime - ISO 8601 datetime string
  * @param {number} [limit=1000] - Maximum number of results
  * @param {string} [interval] - Aggregation interval: 5s, 1m, 5m, 1h, auto
  * @returns {Promise} Response with data_points array
  */
  getMetrics(metricType, startTime, endTime, limit = 1000, interval) {
    return api.get('/history/metrics', {
      params: {
        metric_type: metricType,
        start_time: startTime,
        end_time: endTime,
        limit,
        interval,
      },
    })
  },

  /**
   * Get available metric types
   * @returns {Promise} Response with metric_types array
   */
  getMetricTypes() {
    return api.get('/history/metrics/types')
  },

  /**
   * Compare metrics for the current period vs a prior period
   * @param {string} metricType
   * @param {string} period - hour, day, week
   * @param {string} compareTo - yesterday, last_week
   * @param {number} [limit=1000]
   * @param {string} [interval]
   */
  compareMetrics(metricType, period, compareTo, limit = 1000, interval) {
    return api.get('/history/compare', {
      params: {
        metric_type: metricType,
        period,
        compare_to: compareTo,
        limit,
        interval,
      },
    })
  },
}

// Retention API functions
export const retentionApi = {
  getPolicy() {
    return api.get('/retention')
  },

  updatePolicy(payload) {
    return api.put('/retention', payload)
  },

  runCleanup() {
    return api.post('/retention/cleanup')
  },
}

// Config API functions
export const configApi = {
  getConfig() {
    return api.get('/config')
  },

  updateConfig(payload) {
    return api.put('/config', payload)
  },
}
