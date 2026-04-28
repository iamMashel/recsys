import type { RecommendationResponse } from "~/types"

export const useApi = () => {
  const config = useRuntimeConfig()
  const { token } = useAuth()

  const authHeaders = computed(() =>
    token.value ? { Authorization: `Bearer ${token.value}` } : {}
  )

  async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${config.public.apiBase}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...authHeaders.value,
        ...options.headers,
      },
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Request failed" }))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    return res.json()
  }

  const getRecommendations = (): Promise<RecommendationResponse> =>
    apiFetch("/api/v1/recommendations/me")

  const getItems = (offset = 0, limit = 20) =>
    apiFetch<{ items: any[]; total: number }>(`/api/v1/items/?offset=${offset}&limit=${limit}`)

  const getItem = (id: string) => apiFetch<any>(`/api/v1/items/${id}`)

  const recordInteraction = (itemId: string, eventType: string, rating?: number) =>
    apiFetch("/api/v1/interactions/", {
      method: "POST",
      body: JSON.stringify({ item_id: itemId, event_type: eventType, rating }),
    })

  return { getRecommendations, getItems, getItem, recordInteraction }
}
