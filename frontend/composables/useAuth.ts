export const useAuth = () => {
  const token = useCookie<string | null>("auth_token", { maxAge: 3600, sameSite: "lax" })
  const config = useRuntimeConfig()

  const isAuthenticated = computed(() => !!token.value)

  async function login(email: string, password: string): Promise<void> {
    const body = new URLSearchParams({ username: email, password })
    const res = await fetch(`${config.public.apiBase}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }))
      throw new Error(err.detail || "Login failed")
    }
    const data = await res.json()
    token.value = data.access_token
  }

  async function register(email: string, password: string, fullName?: string): Promise<void> {
    const res = await fetch(`${config.public.apiBase}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name: fullName }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Registration failed" }))
      throw new Error(err.detail || "Registration failed")
    }
    await login(email, password)
  }

  function logout(): void {
    token.value = null
    navigateTo("/login")
  }

  return { token, isAuthenticated, login, register, logout }
}
