<template>
  <div id="app">
    <!-- Show layout for authenticated routes, raw view for login -->
    <Layout v-if="showLayout">
      <router-view />
    </Layout>
    <router-view v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '@/components/layout/Layout.vue'

const route = useRoute()

// Show layout for all routes except login
const showLayout = computed(() => {
  return route.name && route.name !== 'Login'
})
</script>
