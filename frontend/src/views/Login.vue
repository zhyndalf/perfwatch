<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-bg to-dark-surface">
    <div class="w-full max-w-md p-8">
      <!-- Logo/Header -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-accent-cyan to-accent-green bg-clip-text text-transparent">
          PerfWatch
        </h1>
        <p class="text-gray-400 mt-2">Real-time System Performance Monitor</p>
      </div>

      <!-- Login Card -->
      <div class="bg-dark-surface/50 backdrop-blur border border-dark-border rounded-xl p-8">
        <h2 class="text-xl font-semibold text-white mb-6">Sign In</h2>

        <!-- Error Message -->
        <div
          v-if="authStore.error"
          class="mb-4 p-3 bg-accent-error/20 border border-accent-error/50 rounded-lg text-accent-error text-sm"
        >
          {{ authStore.error }}
        </div>

        <form @submit.prevent="handleLogin">
          <!-- Username -->
          <div class="mb-4">
            <label for="username" class="block text-gray-300 text-sm mb-2">Username</label>
            <input
              id="username"
              v-model="username"
              type="text"
              class="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-cyan transition-colors"
              placeholder="Enter username"
              :disabled="authStore.loading"
              required
            />
          </div>

          <!-- Password -->
          <div class="mb-6">
            <label for="password" class="block text-gray-300 text-sm mb-2">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              class="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-cyan transition-colors"
              placeholder="Enter password"
              :disabled="authStore.loading"
              required
            />
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            class="w-full py-3 bg-gradient-to-r from-accent-cyan to-accent-green text-dark-bg font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="authStore.loading || !username || !password"
          >
            <span v-if="authStore.loading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Signing in...
            </span>
            <span v-else>Sign In</span>
          </button>
        </form>
      </div>

      <!-- Footer -->
      <p class="text-center text-gray-500 text-sm mt-6">
        PerfWatch v0.1.0
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')

async function handleLogin() {
  authStore.clearError()

  const success = await authStore.login(username.value, password.value)

  if (success) {
    router.push({ name: 'Dashboard' })
  }
}
</script>
