import { ref } from 'vue'
import { apiFetch, apiJson } from '../utils/api.js'

// 전역 이벤트 상태
const events = ref([])

export function useEvents() {
  // 이벤트 목록 로드
  async function loadEvents(filters = {}) {
    const params = new URLSearchParams()
    if (filters.date) {
      params.set('date_from', new Date(filters.date).toISOString())
      const end = new Date(filters.date)
      end.setDate(end.getDate() + 1)
      params.set('date_to', end.toISOString())
    }
    if (filters.eventType) params.set('event_type', filters.eventType)
    if (filters.danceGenre) params.set('dance_genre', filters.danceGenre)

    const res = await apiFetch(`/api/events/?${params}`)
    events.value = await res.json()
  }

  // 이벤트 등록
  async function createEvent(eventData) {
    const res = await apiJson('/api/events/', {
      method: 'POST',
      body: JSON.stringify(eventData),
    })
    if (res.ok) {
      return { ok: true }
    } else {
      const err = await res.json()
      return { ok: false, error: err.detail || '등록에 실패했습니다' }
    }
  }

  // 이벤트 삭제
  async function deleteEvent(id) {
    const res = await apiFetch(`/api/events/${id}`, { method: 'DELETE' })
    return res.ok
  }

  return {
    events,
    loadEvents,
    createEvent,
    deleteEvent,
  }
}
