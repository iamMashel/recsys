<script setup lang="ts">
const { login, isAuthenticated } = useAuth()
if (isAuthenticated.value) navigateTo("/")

const email = ref("")
const password = ref("")
const error = ref<string | null>(null)
const loading = ref(false)

async function submit() {
  error.value = null
  loading.value = true
  try {
    await login(email.value, password.value)
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
        <h1 class="text-2xl font-bold text-white mt-2">Welcome back</h1>
        <p class="text-gray-500 text-sm mt-1">Sign in to get your recommendations</p>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Email</label>
          <input
            v-model="email"
            type="email"
            class="input"
            placeholder="you@example.com"
            required
            autocomplete="email"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Password</label>
          <input
            v-model="password"
            type="password"
            class="input"
            placeholder="••••••••"
            required
            autocomplete="current-password"
          />
        </div>

        <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? "Signing in…" : "Sign in" }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-500">
        No account?
        <NuxtLink to="/register" class="text-brand-400 hover:text-brand-300 font-medium">
          Create one
        </NuxtLink>
      </p>
    </div>
  </div>
</template>
