<script setup lang="ts">
const props = defineProps<{ itemId: string }>()
const emit = defineEmits<{ rated: [rating: number] }>()

const { recordInteraction } = useApi()
const hovered = ref(0)
const selected = ref(0)

async function rate(value: number) {
  selected.value = value
  await recordInteraction(props.itemId, "rating", value)
  emit("rated", value)
}
</script>

<template>
  <div class="flex items-center gap-1">
    <button
      v-for="star in 5"
      :key="star"
      @click="rate(star)"
      @mouseenter="hovered = star"
      @mouseleave="hovered = 0"
      class="transition-colors"
      :class="star <= (hovered || selected) ? 'text-yellow-400' : 'text-gray-700'"
    >
      <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
      </svg>
    </button>
    <span v-if="selected" class="text-sm text-gray-400 ml-1">{{ selected }}/5</span>
  </div>
</template>
