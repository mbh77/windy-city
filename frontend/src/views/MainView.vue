<template>
  <!-- 위치 선택 모드 오버레이 -->
  <PickLocationBar
    :visible="isPicking"
    :message="pickMessage"
    :hasLocation="!!pickedLocation"
    @confirm="confirmPick"
    @retry="retryPick"
    @cancel="cancelPick"
  />

  <main class="layout">
    <!-- 지도 -->
    <div class="map-wrap">
      <KakaoMap
        ref="mapRef"
        :isPicking="isPicking"
        :visibleCategories="visibleCategories"
        @markerClick="openEventDetail"
        @venueMarkerClick="openVenueDetail"
        @locationPicked="handleLocationPicked"
        @boundsChanged="mapBounds = $event"
      />

      <CategoryBar
        :visibleCategories="visibleCategories"
        @toggle="toggleCategory"
      ></CategoryBar>
    </div>


    <!-- 사이드바 -->
    <Sidebar
      :mapBounds="mapBounds"
      :visibleCategories="visibleCategories"
      @addEvent="openCreateEventModal"
      @selectEvent="openEventDetail"
      @addVenue="openCreateVenueModal"
      @selectVenue="openVenueDetail"
      @dateFilterChange="handleDateFilter"
    />
  </main>

  <!-- 이벤트 상세 모달 -->
  <EventDetailModal
    :visible="showEventDetail"
    :event="selectedEvent"
    @close="closeEventDetail"
    @edit="handleEditEvent"
  />

  <!-- 장소 상세 모달 -->
  <VenueDetailModal
    :visible="showVenueDetail"
    :venue="selectedVenue"
    @close="closeVenueDetail"
    @edit="handleEditVenue"
  />

  <!-- 로그인/회원가입 모달 -->
  <AuthModal
    :visible="showAuth"
    @close="showAuth = false"
  />

  <!-- 이벤트 등록 모달 -->
  <CreateEventModal
    ref="createEventRef"
    :visible="showCreateEvent"
    :restoredForm="restoredEventForm"
    :eventToEdit="eventToEdit"
    @close="showCreateEvent = false"
    @pickLocation="startPickLocation('event', $event)"
    @created="handleEventCreated"
  />

  <!-- 장소 등록 모달 -->
  <CreateVenueModal
    ref="createVenueRef"
    :visible="showCreateVenue"
    :restoredForm="restoredVenueForm"
    :venueToEdit="venueToEdit"
    @close="showCreateVenue = false"
    @pickLocation="startPickLocation('venue', $event)"
    @created="handleVenueCreated"
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
import { useAuth } from '../composables/useAuth.js'
import { useEvents } from '../composables/useEvents.js'
import { useVenues } from '../composables/useVenues.js'

import Sidebar from '../components/Sidebar.vue'
import KakaoMap from '../components/KakaoMap.vue'
import PickLocationBar from '../components/PickLocationBar.vue'
import EventDetailModal from '../components/EventDetailModal.vue'
import VenueDetailModal from '../components/VenueDetailModal.vue'
import AuthModal from '../components/AuthModal.vue'
import CreateEventModal from '../components/CreateEventModal.vue'
import CreateVenueModal from '../components/CreateVenueModal.vue'
import CategoryBar from '../components/CategoryBar.vue'
import OnboardingOverlay from '../components/OnboardingOverlay.vue'

const { currentUser, restoreSession, logout } = useAuth()
const { events, loadEvents } = useEvents()
const { venues, loadVenues } = useVenues()

// refs
const mapRef = ref(null)
const createEventRef = ref(null)
const createVenueRef = ref(null)

// 지도 영역
const mapBounds = ref(null)

// 모달 상태
const showEventDetail = ref(false)
const showVenueDetail = ref(false)
const showAuth = ref(false)
const showCreateEvent = ref(false)
const showCreateVenue = ref(false)
const selectedEvent = ref(null)
const selectedVenue = ref(null)
const eventToEdit = ref(null)
const venueToEdit = ref(null)

// 모달 뒤로가기 처리
const anyModalOpen = computed(() =>
  showEventDetail.value || showVenueDetail.value || showAuth.value || showCreateEvent.value || showCreateVenue.value
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
    showAuth.value = false
    showCreateEvent.value = false
    showCreateVenue.value = false
  }
}

onMounted(() => {
  window.addEventListener('popstate', handlePopState)
})

onUnmounted(() => {
  window.removeEventListener('popstate', handlePopState)
})

// 위치 선택 상태
const isPicking = ref(false)
const pickMessage = ref('지도에서 위치를 클릭하세요')
const pickedLocation = ref(null)
const pickTarget = ref('event')
const restoredEventForm = ref(null)
const restoredVenueForm = ref(null)

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

// ── 검색 ──
function handleSearch(filters) {
  loadEvents(filters)
}

// ── 인증 ──
function handleAuthClick() {
  if (currentUser.value) {
    logout()
  } else {
    showAuth.value = true
  }
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

// ── 이벤트 등록 ──
function openCreateEventModal() {
  restoredEventForm.value = null
  eventToEdit.value = null
  createEventRef.value?.resetForm()
  showCreateEvent.value = true
}

function handleEditEvent(event) {
  eventToEdit.value = event
  showEventDetail.value = false
  showCreateEvent.value = true
}

async function handleEventCreated(data) {
  if (data?.panTo) {
    mapRef.value?.panTo(data.panTo.lat, data.panTo.lng)
    return
  }
  // 생성/수정된 이벤트의 날짜 기준으로 필터 조정
  if (data?.startDate) {
    const eventDate = new Date(data.startDate)
    const weekAfter = new Date(eventDate)
    weekAfter.setDate(eventDate.getDate() + 7)
    currentFilters.value = {
      date_from: toLocalDate(eventDate),
      date_to: toLocalDate(weekAfter),
    }
  }
  await loadEvents(currentFilters.value)
}

// ── 장소 등록 ──
function openCreateVenueModal() {
  restoredVenueForm.value = null
  venueToEdit.value = null
  createVenueRef.value?.resetForm()
  showCreateVenue.value = true
}

function handleEditVenue(venue) {
  venueToEdit.value = venue
  showVenueDetail.value = false
  showCreateVenue.value = true
}

async function handleVenueCreated(data) {
  if (data?.panTo) {
    mapRef.value?.panTo(data.panTo.lat, data.panTo.lng)
    return
  }
  await loadVenues()
}

// ── 위치 선택 모드 (이벤트/장소 공용) ──
function startPickLocation(target, formData) {
  pickTarget.value = target
  if (target === 'event') {
    restoredEventForm.value = formData ? { ...formData } : null
    showCreateEvent.value = false
  } else {
    restoredVenueForm.value = formData ? { ...formData } : null
    showCreateVenue.value = false
  }
  isPicking.value = true
  pickMessage.value = '지도에서 위치를 클릭하세요'
  pickedLocation.value = null
}

function handleLocationPicked(loc) {
  pickedLocation.value = loc
  pickMessage.value = loc.address || '주소를 찾을 수 없습니다'
}

function confirmPick() {
  if (!pickedLocation.value) return
  isPicking.value = false

  const loc = pickedLocation.value
  if (pickTarget.value === 'event') {
    if (restoredEventForm.value) {
      restoredEventForm.value.latitude = loc.lat.toFixed(6)
      restoredEventForm.value.longitude = loc.lng.toFixed(6)
      if (loc.address) restoredEventForm.value.address = loc.address
    }
    showCreateEvent.value = true
  } else {
    if (restoredVenueForm.value) {
      restoredVenueForm.value.latitude = loc.lat.toFixed(6)
      restoredVenueForm.value.longitude = loc.lng.toFixed(6)
      if (loc.address) restoredVenueForm.value.address = loc.address
    }
    showCreateVenue.value = true
  }
  pickedLocation.value = null
}

function retryPick() {
  mapRef.value?.clearTempMarker()
  pickedLocation.value = null
  pickMessage.value = '지도에서 위치를 클릭하세요'
}

function cancelPick() {
  isPicking.value = false
  pickedLocation.value = null
  if (pickTarget.value === 'event') {
    showCreateEvent.value = true
  } else {
    showCreateVenue.value = true
  }
}

function handleDateFilter({ date_from, date_to }) {
  currentFilters.value = { date_from, date_to }
  loadEvents(currentFilters.value)
}

// ── 온보딩 ──
function handleOnboardingEvents() {
  localStorage.setItem('onboarding_done', '1')
}

function handleOnboardingVenues() {
  localStorage.setItem('onboarding_done', '1')
}

defineExpose({ handleAuthClick, handlePlaceSelect })
</script>
