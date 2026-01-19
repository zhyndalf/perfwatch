import { defineStore } from 'pinia'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    username: (state) => state.user?.username || null,
  },

  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null

      try {
        const response = await authApi.login(username, password)
        const { access_token } = response.data

        // Store token
        this.token = access_token
        localStorage.setItem('token', access_token)

        // Fetch user info
        await this.fetchUser()

        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async fetchUser() {
      if (!this.token) return null

      try {
        const response = await authApi.me()
        this.user = response.data
        return this.user
      } catch (error) {
        // Token might be invalid
        this.logout()
        return null
      }
    },

    logout() {
      this.token = null
      this.user = null
      this.error = null
      localStorage.removeItem('token')
    },

    clearError() {
      this.error = null
    },
  },
})
