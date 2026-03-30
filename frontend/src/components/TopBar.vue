<template>
  <header class="topbar">
    <!-- 1단: 로고 + 장소 검색 + 로그인 -->
    <div class="topbar-row topbar-main">
      <div class="logo-area">
        <div class="nav-menu" ref="navMenuRef">
          <button class="nav-menu-btn" @click="showNavMenu = !showNavMenu" title="메뉴">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <div v-if="showNavMenu" class="nav-dropdown">
            <router-link to="/board?category=notice" class="nav-dropdown-item" @click="showNavMenu = false">📢 공지사항</router-link>
            <router-link to="/board?category=free" class="nav-dropdown-item" @click="showNavMenu = false">💬 열린 플로어 (자유게시판)</router-link>
            <router-link to="/events" class="nav-dropdown-item" @click="showNavMenu = false">💃 클래스·이벤트</router-link>
            <router-link to="/venues" class="nav-dropdown-item" @click="showNavMenu = false">🎭 댄스바·동호회·연습실</router-link>
            <router-link to="/about" class="nav-dropdown-item" @click="showNavMenu = false">ℹ️ About</router-link>
            <router-link to="/feedback" class="nav-dropdown-item" @click="showNavMenu = false">💡 제보/제안</router-link>
            <router-link v-if="currentUser?.is_admin" to="/admin" class="nav-dropdown-item" @click="showNavMenu = false">⚙️ 관리자</router-link>
          </div>
        </div>
        <router-link to="/" class="logo"><img src="@/assets/windycity_logo.png" alt="바람난 도시" class="logo-img" /></router-link>
      </div>

      <div v-if="showSearch" class="place-search" ref="searchWrapRef">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="지역 이동 (예: 강남역)"
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

      <!-- PC 가로 메뉴 -->
      <nav class="nav-links">
        <router-link to="/board?category=notice">공지사항</router-link>
        <router-link to="/board?category=free">열린 플로어</router-link>
        <router-link to="/events">클래스·이벤트</router-link>
        <router-link to="/venues">댄스바·동호회·연습실</router-link>
        <router-link to="/about">About</router-link>
        <router-link to="/feedback">제보/제안</router-link>
        <router-link v-if="currentUser?.is_admin" to="/admin">관리자</router-link>
      </nav>

      <div class="auth-area">
        <!-- 로그아웃 상태: 로그인 아이콘 -->
        <button v-if="!currentUser" class="auth-icon-btn" @click="$emit('authClick')" title="로그인">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </button>
        <!-- 로그인 상태: 이름 약자 아바타 -->
        <div v-else class="user-menu" ref="userMenuRef">
          <button class="user-avatar" @click="showUserMenu = !showUserMenu">
            {{ currentUser.nickname?.charAt(0)?.toUpperCase() || 'U' }}
          </button>
          <div v-if="showUserMenu" class="user-dropdown">
            <div class="user-dropdown-name">{{ currentUser.nickname }}</div>
            <button class="user-dropdown-item" @click="handleLogout">로그아웃</button>
            <button v-if="!currentUser.is_admin" class="user-dropdown-item user-dropdown-danger" @click="handleWithdraw">회원 탈퇴</button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useAuth } from '../composables/useAuth.js'

const emit = defineEmits(['authClick', 'placeSelect'])
const props = defineProps({
  showSearch: { type: Boolean, default: true },
})

const { currentUser, withdraw } = useAuth()

// 네비게이션 메뉴
const showNavMenu = ref(false)
const navMenuRef = ref(null)

// 유저 메뉴
const showUserMenu = ref(false)
const userMenuRef = ref(null)

function handleLogout() {
  showUserMenu.value = false
  emit('authClick')
}

async function handleWithdraw() {
  if (!confirm('정말 탈퇴하시겠습니까?\n작성한 글과 댓글은 유지되며, 작성자는 "탈퇴한 사용자"로 표시됩니다.')) return
  const result = await withdraw()
  if (result.ok) {
    showUserMenu.value = false
    alert('회원 탈퇴가 완료되었습니다.')
    window.location.href = '/'
  } else {
    alert(result.error)
  }
}

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
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    showUserMenu.value = false
  }
  if (navMenuRef.value && !navMenuRef.value.contains(e.target)) {
    showNavMenu.value = false
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
</script>
