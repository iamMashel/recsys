<script setup lang="ts">
definePageMeta({ middleware: "auth" })

const route = useRoute()
const { getItem, recordInteraction } = useApi()

const item = ref<any>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const ratingDone = ref(false)

async function load() {
  loading.value = true
  error.value = null
  try {
    item.value = await getItem(route.params.id as string)
    await recordInteraction(route.params.id as string, "view")
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function onRated(rating: number) {
  ratingDone.value = true
}

onMounted(load)

const genreList = computed(() =>
  item.value?.genres?.split(",").map((g: string) => g.trim()).filter(Boolean) ?? []
)
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <!-- Back -->
    <NuxtLink to="/" class="inline-flex items-center gap-1.5 text-gray-400 hover:text-white text-sm mb-8 transition-colors">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      Back to recommendations
    </NuxtLink>

    <div v-if="loading" class="space-y-4 animate-pulse">
      <div class="h-8 bg-gray-800 rounded w-2/3" />
      <div class="h-4 bg-gray-800 rounded w-1/3" />
      <div class="h-24 bg-gray-800 rounded" />
    </div>

    <div v-else-if="error" class="text-red-400">{{ error }}</div>

    <div v-else-if="item" class="space-y-6">
      <div>
        <h1 class="text-3xl font-bold text-white leading-tight">{{ item.title }}</h1>
        <p v-if="item.release_year" class="text-gray-500 mt-1">{{ item.release_year }}</p>
      </div>

      <div class="flex flex-wrap gap-2">
        <span
          v-for="genre in genreList"
          :key="genre"
          class="text-sm px-3 py-1 rounded-full bg-gray-800 text-gray-300 border border-gray-700"
        >
          {{ genre }}
        </span>
      </div>

      <div class="flex items-center gap-4 text-sm">
        <div class="flex items-center gap-1 text-yellow-400">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          <span class="font-semibold text-white">{{ item.avg_rating.toFixed(1) }}</span>
          <span class="text-gray-500">({{ item.rating_count }} ratings)</span>
        </div>
      </div>

      <div v-if="item.description" class="text-gray-300 leading-relaxed">
        {{ item.description }}
      </div>

      <!-- Rate this movie -->
      <div class="card p-5 space-y-3">
        <p class="text-sm font-medium text-gray-300">Rate this movie</p>
        <StarRating :item-id="item.id" @rated="onRated" />
        <p v-if="ratingDone" class="text-xs text-brand-400">
          Thanks! Your rating improves future recommendations.
        </p>
      </div>
    </div>
  </div>
</template>
