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

      <!-- Data Retention -->
      <div class="bg-dark-surface/50 border border-dark-border rounded-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-accent-cyan font-semibold">Data Retention</h2>
          <span v-if="retentionLastRun" class="text-xs text-gray-400">
            Last cleanup: {{ formatDate(retentionLastRun) }}
          </span>
        </div>

        <div v-if="retentionLoading" class="text-gray-400 text-sm">Loading retention policy...</div>

        <div v-else class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-gray-300 text-sm mb-2">Retention Days</label>
              <input
                v-model.number="retentionDays"
                type="number"
                min="1"
                class="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-cyan transition-colors"
              />
            </div>

            <div>
              <label class="block text-gray-300 text-sm mb-2">Downsample After (days)</label>
              <input
                v-model.number="downsampleAfterDays"
                type="number"
                min="0"
                class="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-cyan transition-colors"
              />
            </div>

            <div>
              <label class="block text-gray-300 text-sm mb-2">Downsample Interval</label>
              <select
                v-model="downsampleInterval"
                class="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-accent-cyan transition-colors"
              >
                <option value="5s">5s</option>
                <option value="1m">1m</option>
                <option value="5m">5m</option>
                <option value="1h">1h</option>
              </select>
            </div>

            <div class="flex items-center gap-3">
              <input
                id="archiveEnabled"
                v-model="archiveEnabled"
                type="checkbox"
                class="h-4 w-4 rounded border-dark-border text-accent-cyan focus:ring-accent-cyan"
              />
              <label for="archiveEnabled" class="text-gray-300 text-sm">Enable cleanup</label>
            </div>

            <div>
              <label class="block text-gray-300 text-sm mb-2">Cleanup Interval (minutes)</label>
              <input
                v-model.number="cleanupIntervalMinutes"
                type="number"
                min="1"
                class="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-accent-cyan transition-colors"
              />
            </div>

            <div class="flex items-center gap-3">
              <input
                id="cleanupEnabled"
                v-model="cleanupEnabled"
                type="checkbox"
                class="h-4 w-4 rounded border-dark-border text-accent-cyan focus:ring-accent-cyan"
              />
              <label for="cleanupEnabled" class="text-gray-300 text-sm">Enable scheduled cleanup</label>
            </div>
          </div>

          <div v-if="retentionError" class="p-3 bg-accent-error/20 border border-accent-error/50 rounded-lg text-accent-error text-sm">
            {{ retentionError }}
          </div>

          <div v-if="retentionSuccess" class="p-3 bg-accent-green/20 border border-accent-green/50 rounded-lg text-accent-green text-sm">
            {{ retentionSuccess }}
          </div>

          <div class="flex flex-col sm:flex-row gap-3">
            <button
              type="button"
              class="px-6 py-2 bg-accent-cyan text-dark-bg font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
              :disabled="retentionSaving"
              @click="saveRetention"
            >
              {{ retentionSaving ? 'Saving...' : 'Save Policy' }}
            </button>
            <button
              type="button"
              class="px-6 py-2 bg-dark-bg border border-dark-border text-gray-200 rounded-lg hover:border-accent-cyan transition-colors disabled:opacity-50"
              :disabled="retentionSaving"
              @click="runCleanup"
            >
              Run Cleanup
            </button>
            <span v-if="cleanupSummary" class="text-sm text-gray-400 self-center">
              Deleted {{ cleanupSummary.deleted }} snapshots
            </span>
          </div>
        </div>
      </div>

      <!-- System Info -->
      <div class="bg-dark-surface/50 border border-dark-border rounded-xl p-6">
        <h2 class="text-accent-cyan font-semibold mb-4">System Info</h2>

        <div v-if="configLoading" class="text-gray-400 text-sm">
          Loading system info...
        </div>

        <div v-else class="space-y-3 text-sm text-gray-300">
          <div v-if="configError" class="p-3 bg-accent-error/20 border border-accent-error/50 rounded-lg text-accent-error">
            {{ configError }}
          </div>
          <div class="flex items-center justify-between">
            <span>Perf Events</span>
            <span class="text-white">
              {{ perfEventsEnabled ? 'Enabled' : 'Disabled' }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span>Sampling Interval</span>
            <span class="text-white">
              {{ samplingIntervalSeconds ? `${samplingIntervalSeconds}s` : 'N/A' }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span>App Version</span>
            <span class="text-white">
              {{ appVersion || 'N/A' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'
import { useRetentionStore } from '@/stores/retention'
import { useConfigStore } from '@/stores/config'

const authStore = useAuthStore()
const retentionStore = useRetentionStore()
const configStore = useConfigStore()
const {
  loading: retentionLoading,
  saving: retentionSaving,
  error: retentionError,
  success: retentionSuccess,
  retentionDays,
  downsampleAfterDays,
  downsampleInterval,
  archiveEnabled,
  cleanupEnabled,
  cleanupIntervalMinutes,
  lastArchiveRun: retentionLastRun,
  cleanupSummary,
} = storeToRefs(retentionStore)

const {
  loading: configLoading,
  error: configError,
  samplingIntervalSeconds,
  perfEventsEnabled,
  appVersion,
} = storeToRefs(configStore)

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

onMounted(async () => {
  await Promise.all([
    retentionStore.fetchPolicy(),
    configStore.fetchConfig(),
  ])
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

async function saveRetention() {
  await retentionStore.updatePolicy()
}

async function runCleanup() {
  await retentionStore.runCleanup()
}

function formatDate(value) {
  if (!value) return 'Never'
  return new Date(value).toLocaleString()
}
</script>
