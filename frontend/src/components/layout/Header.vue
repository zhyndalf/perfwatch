<template>
  <header class="bg-dark-surface/50 border-b border-dark-border px-6 py-4">
    <div class="flex items-center justify-between">
      <!-- Logo -->
      <div class="flex items-center space-x-6">
        <h1 class="text-xl font-bold bg-gradient-to-r from-accent-cyan to-accent-green bg-clip-text text-transparent">
          PerfWatch
        </h1>

        <!-- Navigation -->
        <nav class="flex space-x-4">
          <router-link
            to="/"
            class="px-3 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="$route.name === 'Dashboard' ? 'bg-accent-cyan/20 text-accent-cyan' : 'text-gray-400 hover:text-white'"
          >
            Dashboard
          </router-link>
          <router-link
            to="/history"
            class="px-3 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="$route.name === 'History' ? 'bg-accent-cyan/20 text-accent-cyan' : 'text-gray-400 hover:text-white'"
          >
            History
          </router-link>
          <router-link
            to="/settings"
            class="px-3 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="$route.name === 'Settings' ? 'bg-accent-cyan/20 text-accent-cyan' : 'text-gray-400 hover:text-white'"
          >
            Settings
          </router-link>
        </nav>
      </div>

      <!-- User Menu -->
      <div class="flex items-center space-x-4">
        <span class="text-gray-400 text-sm">
          {{ authStore.username }}
        </span>
        <button
          @click="handleLogout"
          class="px-4 py-2 text-sm text-gray-400 hover:text-white border border-dark-border rounded-lg hover:border-accent-error hover:text-accent-error transition-colors"
        >
          Logout
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push({ name: 'Login' })
}
</script>
