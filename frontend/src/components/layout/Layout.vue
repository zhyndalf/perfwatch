<template>
  <div class="min-h-screen bg-gradient-to-br from-dark-bg to-dark-surface">
    <Header />
    <main class="flex-1">
      <slot />
    </main>
  </div>
</template>

<script setup>
import Header from './Header.vue'
</script>
