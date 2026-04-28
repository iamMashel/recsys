<script setup lang="ts">
const { isAuthenticated, logout } = useAuth()
</script>

<template>
  <header class="sticky top-0 z-50 bg-gray-950/90 backdrop-blur border-b border-gray-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
      <NuxtLink to="/" class="flex items-center gap-2">
        <span class="text-brand-500 text-2xl">◈</span>
        <span class="font-bold text-white text-lg tracking-tight">RecSys</span>
      </NuxtLink>

      <nav class="flex items-center gap-2">
        <template v-if="isAuthenticated">
          <NuxtLink to="/" class="btn-ghost text-sm">Home</NuxtLink>
          <button class="btn-ghost text-sm" @click="logout">Sign out</button>
        </template>
        <template v-else>
          <NuxtLink to="/login" class="btn-ghost text-sm">Sign in</NuxtLink>
          <NuxtLink to="/register" class="btn-primary text-sm">Get started</NuxtLink>
        </template>
      </nav>
    </div>
  </header>
</template>
