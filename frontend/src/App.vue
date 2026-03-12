<template>
  <!-- 상단 필터 바 -->
  <TopBar
    :visibleCategories="visibleCategories"
    @search="handleSearch"
    @authClick="handleAuthClick"
    @toggleCategory="toggleCategory"
    @placeSelect="handlePlaceSelect"
  />

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
    <KakaoMap
      ref="mapRef"
      :isPicking="isPicking"
      :visibleCategories="visibleCategories"
      @markerClick="openEventDetail"
      @venueMarkerClick="openVenueDetail"
      @locationPicked="handleLocationPicked"
      @boundsChanged="mapBounds = $event"
    />

    <!-- 사이드바 -->
    <Sidebar
      :mapBounds="mapBounds"
      :visibleCategories="visibleCategories"
      @addEvent="openCreateEventModal"
      @selectEvent="openEventDetail"
      @addVenue="openCreateVenueModal"
      @selectVenue="openVenueDetail"
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
    @close="showCreateVenue = false"
    @pickLocation="startPickLocation('venue', $event)"
    @created="handleVenueCreated"
  />
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuth } from './composables/useAuth.js'
import { useEvents } from './composables/useEvents.js'
import { useVenues } from './composables/useVenues.js'

import TopBar from './components/TopBar.vue'
import Sidebar from './components/Sidebar.vue'
import KakaoMap from './components/KakaoMap.vue'
import PickLocationBar from './components/PickLocationBar.vue'
import EventDetailModal from './components/EventDetailModal.vue'
import VenueDetailModal from './components/VenueDetailModal.vue'
import AuthModal from './components/AuthModal.vue'
import CreateEventModal from './components/CreateEventModal.vue'
import CreateVenueModal from './components/CreateVenueModal.vue'

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

// ── 초기화 ──
onMounted(async () => {
  await restoreSession()
  await Promise.all([loadEvents(), loadVenues()])
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
}

async function closeEventDetail() {
  showEventDetail.value = false
  await loadEvents()
}

// ── 장소 상세 ──
function openVenueDetail(v) {
  selectedVenue.value = v
  showVenueDetail.value = true
  mapRef.value?.panTo(v.latitude, v.longitude)
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
  await loadEvents()
}

// ── 장소 등록 ──
function openCreateVenueModal() {
  restoredVenueForm.value = null
  createVenueRef.value?.resetForm()
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
</script>
