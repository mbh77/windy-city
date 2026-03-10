import { ref } from 'vue'
import { apiFetch, apiJson } from '../utils/api.js'

// 전역 장소 상태
const venues = ref([])

export function useVenues() {
  // 장소 목록 로드
  async function loadVenues(filters = {}) {
    const params = new URLSearchParams()
    if (filters.venueType) params.set('venue_type', filters.venueType)
    if (filters.danceGenre) params.set('dance_genre', filters.danceGenre)

    const res = await apiFetch(`/api/venues/?${params}`)
    venues.value = await res.json()
  }

  // 장소 등록
  async function createVenue(venueData) {
    const res = await apiJson('/api/venues/', {
      method: 'POST',
      body: JSON.stringify(venueData),
    })
    if (res.ok) {
      return { ok: true }
    } else {
      const err = await res.json()
      return { ok: false, error: err.detail || '등록에 실패했습니다' }
    }
  }

  // 장소 수정
  async function updateVenue(id, venueData) {
    const res = await apiJson(`/api/venues/${id}`, {
      method: 'PUT',
      body: JSON.stringify(venueData),
    })
    if (res.ok) {
      return { ok: true }
    } else {
      const err = await res.json()
      return { ok: false, error: err.detail || '수정에 실패했습니다' }
    }
  }

  // 장소 삭제
  async function deleteVenue(id) {
    const res = await apiFetch(`/api/venues/${id}`, { method: 'DELETE' })
    return res.ok
  }

  return {
    venues,
    loadVenues,
    createVenue,
    updateVenue,
    deleteVenue,
  }
}
