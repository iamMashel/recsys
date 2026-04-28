<script setup lang="ts">
import type { RecommendedItem } from "~/types"

const props = defineProps<{
  movie: RecommendedItem
}>()

const { recordInteraction } = useApi()
const liked = ref(false)

const reasonLabel: Record<string, string> = {
  collaborative: "Picked for you",
  semantic: "Similar taste",
  popular: "Trending",
  hybrid: "Top pick",
}

const genreList = computed(() =>
  props.movie.genres?.split(",").map((g) => g.trim()).filter(Boolean) ?? []
)

async function handleLike() {
  liked.value = !liked.value
  await recordInteraction(props.movie.item_id, liked.value ? "like" : "dislike")
}

async function handleView() {
  await recordInteraction(props.movie.item_id, "click")
}
</script>

<template>
  <NuxtLink
    :to="`/item/${movie.item_id}`"
    class="card group flex flex-col gap-3 p-4 hover:border-gray-700 hover:bg-gray-800/50 transition-all cursor-pointer"
    @click="handleView"
  >
    <!-- Score badge -->
    <div class="flex items-start justify-between gap-2">
      <span
        class="text-xs font-medium px-2 py-0.5 rounded-full bg-brand-900/60 text-brand-400 border border-brand-800"
      >
        {{ reasonLabel[movie.reason] ?? movie.reason }}
      </span>
      <span class="text-xs text-gray-500 tabular-nums">
        {{ (movie.score * 100).toFixed(0) }}%
      </span>
    </div>

    <!-- Title -->
    <h3 class="font-semibold text-white leading-snug group-hover:text-brand-400 transition-colors line-clamp-2">
      {{ movie.title }}
    </h3>

    <!-- Genres -->
    <div class="flex flex-wrap gap-1 mt-auto">
      <span
        v-for="genre in genreList.slice(0, 3)"
        :key="genre"
        class="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 border border-gray-700"
      >
        {{ genre }}
      </span>
    </div>

    <!-- Like button -->
    <button
      class="self-end text-gray-500 hover:text-red-400 transition-colors"
      :class="{ 'text-red-400': liked }"
      @click.prevent="handleLike"
      :aria-label="liked ? 'Unlike' : 'Like'"
    >
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path
          fill-rule="evenodd"
          d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"
          clip-rule="evenodd"
        />
      </svg>
    </button>
  </NuxtLink>
</template>
