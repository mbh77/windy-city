import { ref } from 'vue'
import { apiFetch, apiJson } from '../utils/api.js'

// 전역 북마크 상태 (로그인한 사용자의 북마크 목록)
const bookmarks = ref([])

export function useBookmarks() {

  // 내 북마크 목록 조회
  async function fetchBookmarks() {
    try {
      const res = await apiFetch('/api/bookmarks/me')
      if (res.ok) {
        bookmarks.value = await res.json()
      }
    } catch {
      bookmarks.value = []
    }
  }

  // 북마크 여부 확인
  function isBookmarked(entityType, entityId) {
    return bookmarks.value.some(
      b => b.entity_type === entityType && b.entity_id === entityId
    )
  }

  // 북마크 토글 (추가/삭제)
  async function toggleBookmark(entityType, entityId) {
    if (isBookmarked(entityType, entityId)) {
      const res = await apiFetch(`/api/bookmarks/${entityType}/${entityId}`, {
        method: 'DELETE',
      })
      if (res.ok) {
        bookmarks.value = bookmarks.value.filter(
          b => !(b.entity_type === entityType && b.entity_id === entityId)
        )
      }
      return false
    } else {
      const res = await apiJson(`/api/bookmarks/${entityType}/${entityId}`, {
        method: 'POST',
      })
      if (res.ok) {
        const data = await res.json()
        bookmarks.value.push(data)
      }
      return true
    }
  }

  // 북마크 초기화 (로그아웃 시)
  function clearBookmarks() {
    bookmarks.value = []
  }

  return {
    bookmarks,
    fetchBookmarks,
    isBookmarked,
    toggleBookmark,
    clearBookmarks,
  }
}
