<template>
  <main class="layout">
    <!-- 지도 -->
    <div class="map-wrap">
      <KakaoMap
        ref="mapRef"
        :visibleCategories="visibleCategories"
        @markerClick="openEventDetail"
        @venueMarkerClick="openVenueDetail"
        @boundsChanged="mapBounds = $event"
      />

      <CategoryBar
        :visibleCategories="visibleCategories"
        @toggle="toggleCategory"
      ></CategoryBar>

      <div v-if="regionName" class="region-overlay">📍 {{ regionName }}</div>
    </div>


    <!-- 사이드바 -->
    <Sidebar
      :mapBounds="mapBounds"
      :visibleCategories="visibleCategories"
      @selectEvent="openEventDetail"
      @selectVenue="openVenueDetail"
      @dateFilterChange="handleDateFilter"
      @click="closeMapInfowindows"
    />
  </main>

  <!-- 이벤트 상세 모달 -->
  <EventDetailModal
    :visible="showEventDetail"
    :event="selectedEvent"
    @close="closeEventDetail"
  />

  <!-- 장소 상세 모달 -->
  <VenueDetailModal
    :visible="showVenueDetail"
    :venue="selectedVenue"
    @close="closeVenueDetail"
  />

  <!-- 온보딩 (첫 방문 시) -->
  <OnboardingOverlay
    @goEvents="handleOnboardingEvents"
    @goVenues="handleOnboardingVenues"
    @close="() => {}"
  />
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'
import { useEvents } from '../composables/useEvents.js'
import { useVenues } from '../composables/useVenues.js'

import Sidebar from '../components/Sidebar.vue'
import KakaoMap from '../components/KakaoMap.vue'
import EventDetailModal from '../components/EventDetailModal.vue'
import VenueDetailModal from '../components/VenueDetailModal.vue'
import CategoryBar from '../components/CategoryBar.vue'
import OnboardingOverlay from '../components/OnboardingOverlay.vue'

const route = useRoute()
const router = useRouter()
const { restoreSession } = useAuth()
const { events, loadEvents } = useEvents()
const { venues, loadVenues } = useVenues()

// refs
const mapRef = ref(null)
// 지도 영역
const mapBounds = ref(null)
const mapCenter = computed(() => {
  if (!mapBounds.value) return null
  return { lat: mapBounds.value.centerLat, lng: mapBounds.value.centerLng }
})

// 현재 지역명 (역지오코딩)
const regionName = ref('')
let geocoder = null
let geoTimer = null

watch(mapCenter, (center) => {
  if (!center) return
  if (!geocoder && window.kakao?.maps?.services) {
    geocoder = new window.kakao.maps.services.Geocoder()
  }
  if (!geocoder) return
  clearTimeout(geoTimer)
  geoTimer = setTimeout(() => {
    geocoder.coord2RegionCode(center.lng, center.lat, (result, status) => {
      if (status === window.kakao.maps.services.Status.OK) {
        const region = result.find(r => r.region_type === 'H') || result[0]
        if (region) {
          regionName.value = `${region.region_1depth_name} ${region.region_2depth_name}`
        }
      }
    })
  }, 500)
})

// 모달 상태
const showEventDetail = ref(false)
const showVenueDetail = ref(false)
const selectedEvent = ref(null)
const selectedVenue = ref(null)

// 모달 뒤로가기 처리
const anyModalOpen = computed(() =>
  showEventDetail.value || showVenueDetail.value
)

watch(anyModalOpen, (open) => {
  if (open) {
    history.pushState({ modal: true }, '')
  }
})

function handlePopState() {
  if (anyModalOpen.value) {
    showEventDetail.value = false
    showVenueDetail.value = false
  }
}

onMounted(() => {
  window.addEventListener('popstate', handlePopState)
})

onUnmounted(() => {
  window.removeEventListener('popstate', handlePopState)
})

// 카테고리 체크박스 상태
const visibleCategories = reactive({
  club: true,
  academy: true,
  practice_room: true,
  event: true,
})

// ── 날짜 필터 상태 ──
function toLocalDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const today = new Date()
const weekLater = new Date()
weekLater.setDate(today.getDate() + 7)
const currentFilters = ref({
  date_from: toLocalDate(today),
  date_to: toLocalDate(weekLater),
})

// ── 초기화 ──
onMounted(async () => {
  await restoreSession()
  await Promise.all([
    loadEvents(currentFilters.value),
    loadVenues()
  ])
  // 쿼리 파라미터로 이벤트/장소 선택
  if (route.query.eventId) {
    const res = await apiFetch(`/api/events/${route.query.eventId}`)
    if (res.ok) {
      const ev = await res.json()
      openEventDetail(ev)
    }
    router.replace({ path: '/', query: {} })
  } else if (route.query.venueId) {
    const res = await apiFetch(`/api/venues/${route.query.venueId}`)
    if (res.ok) {
      const v = await res.json()
      openVenueDetail(v)
    }
    router.replace({ path: '/', query: {} })
  }

  // 가상 키보드 감지
  const initialHeight = window.innerHeight
  window.visualViewport?.addEventListener('resize', () => {
    const isKeyboard = window.visualViewport.height < initialHeight * 0.75
    document.body.classList.toggle('keyboard-open', isKeyboard)
  })  
})

// ── 카테고리 토글 ──
function toggleCategory(key) {
  visibleCategories[key] = !visibleCategories[key]
}

// ── 장소 검색 → 지도 이동 ──
function handlePlaceSelect({ lat, lng }) {
  mapRef.value?.panTo(lat, lng)
}


// ── 이벤트 상세 ──
function openEventDetail(ev) {
  selectedEvent.value = ev
  showEventDetail.value = true
  mapRef.value?.panTo(ev.latitude, ev.longitude)
  mapRef.value?.selectMarkerById(ev.id, 'event')
}

async function closeEventDetail() {
  showEventDetail.value = false
  await loadEvents(currentFilters.value)
}

// ── 장소 상세 ──
function openVenueDetail(v) {
  selectedVenue.value = v
  showVenueDetail.value = true
  mapRef.value?.panTo(v.latitude, v.longitude)
  mapRef.value?.selectMarkerById(v.id, 'venue')
}

async function closeVenueDetail() {
  showVenueDetail.value = false
  await loadVenues()
}

function handleDateFilter({ date_from, date_to }) {
  currentFilters.value = { date_from, date_to }
  loadEvents(currentFilters.value)
}

function closeMapInfowindows() {
  window.__windycity_closeInfowindows?.()
}

// ── 온보딩 ──
function handleOnboardingEvents() {
  localStorage.setItem('onboarding_done', '1')
}

function handleOnboardingVenues() {
  localStorage.setItem('onboarding_done', '1')
}

defineExpose({ handlePlaceSelect })
</script>
