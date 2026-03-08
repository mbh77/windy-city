<template>
  <!-- 상단 필터 바 -->
  <TopBar @search="handleSearch" @authClick="handleAuthClick" />

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
      @markerClick="openEventDetail"
      @locationPicked="handleLocationPicked"
    />

    <!-- 이벤트 목록 -->
    <Sidebar
      @addEvent="openCreateModal"
      @selectEvent="openEventDetail"
    />
  </main>

  <!-- 이벤트 상세 모달 -->
  <EventDetailModal
    :visible="showDetail"
    :event="selectedEvent"
    @close="closeDetail"
  />

  <!-- 로그인/회원가입 모달 -->
  <AuthModal
    :visible="showAuth"
    @close="showAuth = false"
  />

  <!-- 이벤트 등록 모달 -->
  <CreateEventModal
    ref="createRef"
    :visible="showCreate"
    :restoredForm="restoredFormData"
    @close="showCreate = false"
    @pickLocation="startPickLocation"
    @created="handleEventCreated"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from './composables/useAuth.js'
import { useEvents } from './composables/useEvents.js'

import TopBar from './components/TopBar.vue'
import Sidebar from './components/Sidebar.vue'
import KakaoMap from './components/KakaoMap.vue'
import PickLocationBar from './components/PickLocationBar.vue'
import EventDetailModal from './components/EventDetailModal.vue'
import AuthModal from './components/AuthModal.vue'
import CreateEventModal from './components/CreateEventModal.vue'

const { currentUser, restoreSession, logout } = useAuth()
const { events, loadEvents } = useEvents()

// refs
const mapRef = ref(null)
const createRef = ref(null)

// 모달 상태
const showDetail = ref(false)
const showAuth = ref(false)
const showCreate = ref(false)
const selectedEvent = ref(null)

// 위치 선택 상태
const isPicking = ref(false)
const pickMessage = ref('지도에서 위치를 클릭하세요')
const pickedLocation = ref(null)
const restoredFormData = ref(null)

// ── 초기화 ──
onMounted(async () => {
  await restoreSession()
  await loadEvents()
})

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
  showDetail.value = true
  mapRef.value?.panTo(ev.latitude, ev.longitude)
}

async function closeDetail() {
  showDetail.value = false
  await loadEvents()
}

// ── 이벤트 등록 ──
function openCreateModal() {
  restoredFormData.value = null
  createRef.value?.resetForm()
  showCreate.value = true
}

async function handleEventCreated(data) {
  if (data?.panTo) {
    mapRef.value?.panTo(data.panTo.lat, data.panTo.lng)
    return
  }
  await loadEvents()
}

// ── 위치 선택 모드 ──
function startPickLocation(formData) {
  restoredFormData.value = formData ? { ...formData } : null
  showCreate.value = false
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

  if (restoredFormData.value) {
    restoredFormData.value.latitude = pickedLocation.value.lat.toFixed(6)
    restoredFormData.value.longitude = pickedLocation.value.lng.toFixed(6)
    if (pickedLocation.value.address) {
      restoredFormData.value.address = pickedLocation.value.address
    }
  }
  showCreate.value = true
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
  showCreate.value = true
}
</script>
