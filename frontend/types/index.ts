export interface Item {
  id: string
  title: string
  genres: string | null
  description: string | null
  release_year: number | null
  avg_rating: number
  rating_count: number
  created_at: string
}

export interface RecommendedItem {
  item_id: string
  title: string
  genres: string | null
  score: number
  reason: "collaborative" | "semantic" | "popular" | "hybrid"
}

export interface RecommendationResponse {
  user_id: string
  results: RecommendedItem[]
  total: number
}
