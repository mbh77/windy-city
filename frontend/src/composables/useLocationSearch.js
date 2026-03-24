import { ref } from 'vue'

export function useLocationSearch() {
  const searchQuery = ref('')
  const searchResults = ref([])
  const searchStatus = ref('')

  function searchLocation() {
    const query = searchQuery.value.trim()
    if (!query) return
    searchResults.value = []
    searchStatus.value = '검색 중...'
    const places = new window.kakao.maps.services.Places()
    places.keywordSearch(query, (data, status) => {
      if (status === window.kakao.maps.services.Status.OK) {
        searchResults.value = data.slice(0, 5)
        searchStatus.value = ''
      } else if (status === window.kakao.maps.services.Status.ZERO_RESULT) {
        searchStatus.value = '검색 결과가 없습니다'
      } else {
        searchStatus.value = '검색에 실패했습니다'
      }
    })
  }

  function clearSearch() {
    searchQuery.value = ''
    searchResults.value = []
    searchStatus.value = ''
  }

  return { searchQuery, searchResults, searchStatus, searchLocation, clearSearch }
}
