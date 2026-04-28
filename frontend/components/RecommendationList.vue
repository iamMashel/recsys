<script setup lang="ts">
import type { RecommendedItem } from "~/types"

defineProps<{
  items: RecommendedItem[]
  loading: boolean
  error: string | null
}>()
</script>

<template>
  <div>
    <!-- Loading skeleton -->
    <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      <div
        v-for="i in 10"
        :key="i"
        class="card p-4 flex flex-col gap-3 animate-pulse"
      >
        <div class="h-4 bg-gray-800 rounded w-2/3" />
        <div class="h-5 bg-gray-800 rounded w-full" />
        <div class="h-5 bg-gray-800 rounded w-4/5" />
        <div class="flex gap-1 mt-auto">
          <div class="h-5 bg-gray-800 rounded-full w-16" />
          <div class="h-5 bg-gray-800 rounded-full w-12" />
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-16">
      <p class="text-gray-400 mb-4">{{ error }}</p>
      <p class="text-sm text-gray-600">Try refreshing the page.</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="items.length === 0" class="text-center py-16">
      <p class="text-gray-400 mb-2">No recommendations yet.</p>
      <p class="text-sm text-gray-600">
        Browse some movies and interact with them — the system will learn your taste.
      </p>
    </div>

    <!-- Grid -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      <MovieCard v-for="item in items" :key="item.item_id" :movie="item" />
    </div>
  </div>
</template>
