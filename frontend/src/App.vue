<template>
  <div id="app">
    <template v-if="authStore.token">
      <SidebarLayout>
        <RouterView />
      </SidebarLayout>
    </template>
    <template v-else>
      <RouterView />
    </template>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SidebarLayout from '@/components/layouts/SidebarLayout.vue';

const authStore = useAuthStore()
</script>

<style>
/* Add some basic styling if needed */
</style>