<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-white mb-6">Settings</h1>

    <div class="max-w-2xl space-y-6">
      <!-- Account Settings -->
      <div class="bg-dark-surface/50 border border-dark-border rounded-xl p-6">
        <h2 class="text-accent-cyan font-semibold mb-4">Account</h2>

        <div class="space-y-4">
          <div>
            <label class="block text-gray-300 text-sm mb-1">Username</label>
            <p class="text-white">{{ authStore.user?.username || 'Loading...' }}</p>
          </div>

          <div>
            <label class="block text-gray-300 text-sm mb-1">Last Login</label>
            <p class="text-white">{{ formatLastLogin }}</p>
          </div>
        </div>
      </div>

      <!-- Change Password -->
      <div class="bg-dark-surface/50 border border-dark-border rounded-xl p-6">
        <h2 class="text-accent-cyan font-semibold mb-4">Change Password</h2>

        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label for="currentPassword" class="block text-gray-300 text-sm mb-2">Current Password</label>
            <input
              id="currentPassword"
              v-model="currentPassword"
              type="password"
              class="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-cyan transition-colors"
              placeholder="Enter current password"
            />
          </div>

          <div>
            <label for="newPassword" class="block text-gray-300 text-sm mb-2">New Password</label>
            <input
              id="newPassword"
              v-model="newPassword"
              type="password"
              class="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-cyan transition-colors"
              placeholder="Enter new password"
            />
          </div>

          <div>
            <label for="confirmPassword" class="block text-gray-300 text-sm mb-2">Confirm Password</label>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              class="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-cyan transition-colors"
              placeholder="Confirm new password"
            />
          </div>

          <!-- Error/Success Messages -->
          <div v-if="error" class="p-3 bg-accent-error/20 border border-accent-error/50 rounded-lg text-accent-error text-sm">
            {{ error }}
          </div>

          <div v-if="success" class="p-3 bg-accent-green/20 border border-accent-green/50 rounded-lg text-accent-green text-sm">
            {{ success }}
          </div>

          <button
            type="submit"
            class="px-6 py-2 bg-accent-cyan text-dark-bg font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
            :disabled="loading || !currentPassword || !newPassword || !confirmPassword"
          >
            {{ loading ? 'Updating...' : 'Update Password' }}
          </button>
        </form>
      </div>

      <!-- Application Settings Placeholder -->
      <div class="bg-dark-surface/50 border border-dark-border rounded-xl p-6">
        <h2 class="text-accent-cyan font-semibold mb-4">Application Settings</h2>
        <p class="text-gray-400 text-sm">
          Configuration options for data retention, collection intervals, and more will be available in T010.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'

const authStore = useAuthStore()

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const formatLastLogin = computed(() => {
  if (!authStore.user?.last_login) return 'Never'
  return new Date(authStore.user.last_login).toLocaleString()
})

async function handleChangePassword() {
  error.value = ''
  success.value = ''

  if (newPassword.value !== confirmPassword.value) {
    error.value = 'New passwords do not match'
    return
  }

  if (newPassword.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  loading.value = true

  try {
    await authApi.changePassword(currentPassword.value, newPassword.value)
    success.value = 'Password updated successfully'
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update password'
  } finally {
    loading.value = false
  }
}
</script>
