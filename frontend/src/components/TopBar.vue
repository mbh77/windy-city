<template>
  <header class="topbar">
    <!-- 1단: 로고 + 장소 검색 + 로그인 -->
    <div class="topbar-row topbar-main">
      <div class="logo">바람난 도시</div>

      <div class="place-search" ref="searchWrapRef">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="장소/주소 검색 (예: 강남역, 홍대)"
          class="place-search-input"
          @input="onSearchInput"
          @keydown.down.prevent="moveHighlight(1)"
          @keydown.up.prevent="moveHighlight(-1)"
          @keydown.enter.prevent="selectHighlighted"
          @keydown.escape="closeResults"
          @focus="showResults = searchResults.length > 0"
        />
        <ul v-if="showResults && searchResults.length > 0" class="place-search-results">
          <li
            v-for="(place, idx) in searchResults"
            :key="place.id"
            :class="{ highlighted: idx === highlightIdx }"
            @mousedown.prevent="selectPlace(place)"
          >
            <span class="place-name">{{ place.place_name }}</span>
            <span class="place-addr">{{ place.address_name }}</span>
          </li>
        </ul>
      </div>

      <div class="auth-area">
        <button class="btn-ghost" @click="$emit('authClick')">
          {{ currentUser ? `${currentUser.nickname} 로그아웃` : '로그인' }}
        </button>
      </div>
    </div>

    <!-- 2단: 카테고리 체크박스 + 이벤트 필터 -->
    <div class="topbar-row topbar-filters">
      <div class="category-filters">
        <label v-for="cat in MAP_CATEGORIES" :key="cat.key" class="category-check">
          <input
            type="checkbox"
            :checked="visibleCategories[cat.key]"
            @change="toggleCategory(cat.key)"
          />
          <span class="cat-dot" :style="{ background: cat.color }"></span>
          {{ cat.label }}
        </label>
      </div>

      <div class="filter-divider"></div>

      <div class="filters">
        <input type="date" v-model="filterDate" />
        <select v-model="filterType">
          <option value="">전체 유형</option>
          <option v-for="opt in TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
        <select v-model="filterGenre">
          <option value="">전체 장르</option>
          <option v-for="opt in GENRE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
        <button class="btn-primary" @click="handleSearch">검색</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { TYPE_OPTIONS, GENRE_OPTIONS, MAP_CATEGORIES } from '../utils/constants.js'
import { useAuth } from '../composables/useAuth.js'

const emit = defineEmits(['search', 'authClick', 'toggleCategory', 'placeSelect'])
const props = defineProps({
  visibleCategories: {
    type: Object,
    default: () => ({ club: true, academy: true, practice_room: true, event: true }),
  },
})

const { currentUser } = useAuth()

const filterDate = ref('')
const filterType = ref('')
const filterGenre = ref('')

// 장소 검색 상태
const searchQuery = ref('')
const searchResults = ref([])
const showResults = ref(false)
const highlightIdx = ref(-1)
const searchWrapRef = ref(null)
let places = null
let geocoder = null
let debounceTimer = null

// 카카오 Places + Geocoder 서비스 초기화
onMounted(() => {
  function initServices() {
    places = new window.kakao.maps.services.Places()
    geocoder = new window.kakao.maps.services.Geocoder()
  }
  if (window.kakao?.maps?.services) {
    initServices()
  } else {
    const check = setInterval(() => {
      if (window.kakao?.maps?.services) {
        initServices()
        clearInterval(check)
      }
    }, 500)
    setTimeout(() => clearInterval(check), 10000)
  }
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 외부 클릭 시 결과 닫기
function handleClickOutside(e) {
  if (searchWrapRef.value && !searchWrapRef.value.contains(e.target)) {
    showResults.value = false
  }
}

// 검색 입력 (디바운스 적용)
function onSearchInput() {
  highlightIdx.value = -1
  clearTimeout(debounceTimer)
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    showResults.value = false
    return
  }
  debounceTimer = setTimeout(() => {
    if (!places || !geocoder) return
    const query = searchQuery.value.trim()

    // 키워드 검색 + 주소 검색 병렬 실행
    Promise.all([
      new Promise(resolve => {
        places.keywordSearch(query, (data, status) => {
          if (status === window.kakao.maps.services.Status.OK) {
            resolve(data.slice(0, 5).map(p => ({
              id: p.id,
              place_name: p.place_name,
              address_name: p.address_name,
              y: p.y,
              x: p.x,
            })))
          } else {
            resolve([])
          }
        })
      }),
      new Promise(resolve => {
        geocoder.addressSearch(query, (data, status) => {
          if (status === window.kakao.maps.services.Status.OK) {
            resolve(data.slice(0, 3).map(a => ({
              id: `addr_${a.x}_${a.y}`,
              place_name: a.address_name,
              address_name: a.address?.region_3depth_name
                ? `${a.address.region_1depth_name} ${a.address.region_2depth_name} ${a.address.region_3depth_name}`
                : (a.address_type === 'REGION' ? '지역' : '주소'),
              y: a.y,
              x: a.x,
            })))
          } else {
            resolve([])
          }
        })
      }),
    ]).then(([placeResults, addrResults]) => {
      // 키워드 결과 우선, 주소 결과 중 중복 제거 후 합치기
      const seen = new Set(placeResults.map(p => `${p.y},${p.x}`))
      const merged = [...placeResults]
      for (const a of addrResults) {
        if (!seen.has(`${a.y},${a.x}`)) merged.push(a)
      }
      searchResults.value = merged.slice(0, 7)
      showResults.value = merged.length > 0
    })
  }, 300)
}

// 키보드 네비게이션
function moveHighlight(dir) {
  if (!searchResults.value.length) return
  highlightIdx.value = Math.max(-1, Math.min(
    searchResults.value.length - 1,
    highlightIdx.value + dir
  ))
}

function selectHighlighted() {
  if (highlightIdx.value >= 0 && highlightIdx.value < searchResults.value.length) {
    selectPlace(searchResults.value[highlightIdx.value])
  }
}

// 장소 선택 → 지도 이동
function selectPlace(place) {
  searchQuery.value = place.place_name
  showResults.value = false
  highlightIdx.value = -1
  emit('placeSelect', {
    lat: parseFloat(place.y),
    lng: parseFloat(place.x),
    name: place.place_name,
  })
}

function closeResults() {
  showResults.value = false
  highlightIdx.value = -1
}

function handleSearch() {
  emit('search', {
    date: filterDate.value,
    eventType: filterType.value,
    danceGenre: filterGenre.value,
  })
}

function toggleCategory(key) {
  emit('toggleCategory', key)
}
</script>
