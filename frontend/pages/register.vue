<script setup lang="ts">
const { register, isAuthenticated } = useAuth()
if (isAuthenticated.value) navigateTo("/")

const email = ref("")
const password = ref("")
const fullName = ref("")
const error = ref<string | null>(null)
const loading = ref(false)

async function submit() {
  error.value = null
  loading.value = true
  try {
    await register(email.value, password.value, fullName.value || undefined)
    navigateTo("/")
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="w-full max-w-sm space-y-6">
      <div class="text-center">
        <span class="text-brand-500 text-4xl">◈</span>
        <h1 class="text-2xl font-bold text-white mt-2">Create account</h1>
        <p class="text-gray-500 text-sm mt-1">Start getting personalized movie recommendations</p>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Full name <span class="text-gray-600">(optional)</span></label>
          <input v-model="fullName" type="text" class="input" placeholder="Jane Doe" autocomplete="name" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Email</label>
          <input v-model="email" type="email" class="input" placeholder="you@example.com" required autocomplete="email" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Password <span class="text-gray-600">(min 8 chars)</span></label>
          <input v-model="password" type="password" class="input" placeholder="••••••••" required minlength="8" autocomplete="new-password" />
        </div>

        <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? "Creating account…" : "Get started" }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-500">
        Already have an account?
        <NuxtLink to="/login" class="text-brand-400 hover:text-brand-300 font-medium">Sign in</NuxtLink>
      </p>
    </div>
  </div>
</template>
