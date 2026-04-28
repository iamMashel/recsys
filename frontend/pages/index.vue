<script setup lang="ts">
import type { RecommendedItem } from "~/types"

definePageMeta({ middleware: "auth" })

const { getRecommendations, getItems } = useApi()

const recs = ref<RecommendedItem[]>([])
const recsLoading = ref(true)
const recsError = ref<string | null>(null)

const browseItems = ref<any[]>([])
const browseLoading = ref(true)
const browseOffset = ref(0)

async function fetchRecs() {
  recsLoading.value = true
  recsError.value = null
  try {
    const data = await getRecommendations()
    recs.value = data.results
  } catch (e: any) {
    recsError.value = e.message
  } finally {
    recsLoading.value = false
  }
}

async function fetchBrowse() {
  browseLoading.value = true
  try {
    const data = await getItems(browseOffset.value, 20)
    browseItems.value = [...browseItems.value, ...data.items]
  } finally {
    browseLoading.value = false
  }
}

function loadMore() {
  browseOffset.value += 20
  fetchBrowse()
}

onMounted(() => {
  fetchRecs()
  fetchBrowse()
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-14">
    <!-- Recommendations section -->
    <section>
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-white">For you</h1>
          <p class="text-sm text-gray-500 mt-0.5">
            Personalized with collaborative filtering + semantic AI
          </p>
        </div>
        <button
          class="btn-ghost text-sm flex items-center gap-1"
          @click="fetchRecs"
          :disabled="recsLoading"
        >
          <svg class="w-4 h-4" :class="{ 'animate-spin': recsLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
      <RecommendationList :items="recs" :loading="recsLoading" :error="recsError" />
    </section>

    <!-- Browse all section -->
    <section>
      <h2 class="text-xl font-bold text-white mb-6">Browse movies</h2>
      <div v-if="browseLoading && browseItems.length === 0" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <div v-for="i in 10" :key="i" class="card p-4 animate-pulse space-y-3">
          <div class="h-4 bg-gray-800 rounded w-3/4" />
          <div class="h-4 bg-gray-800 rounded w-full" />
          <div class="h-3 bg-gray-800 rounded w-1/2" />
        </div>
      </div>
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <NuxtLink
          v-for="item in browseItems"
          :key="item.id"
          :to="`/item/${item.id}`"
          class="card p-4 hover:border-gray-700 hover:bg-gray-800/50 transition-all group"
        >
          <h3 class="font-medium text-white group-hover:text-brand-400 transition-colors text-sm line-clamp-2 mb-2">
            {{ item.title }}
          </h3>
          <p class="text-xs text-gray-500">{{ item.genres }}</p>
          <div class="flex items-center gap-1 mt-3 text-yellow-400 text-xs">
            <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span class="text-gray-400">{{ item.avg_rating.toFixed(1) }}</span>
            <span class="text-gray-600">({{ item.rating_count }})</span>
          </div>
        </NuxtLink>
      </div>
      <div class="mt-8 text-center">
        <button
          class="btn-ghost"
          @click="loadMore"
          :disabled="browseLoading"
        >
          {{ browseLoading ? "Loading…" : "Load more" }}
        </button>
      </div>
    </section>
  </div>
</template>
