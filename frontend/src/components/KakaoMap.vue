<template>
  <div id="map" :class="{ picking: isPicking }"></div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useEvents } from '../composables/useEvents.js'
import { useVenues } from '../composables/useVenues.js'
import { formatDate } from '../utils/api.js'
import { VENUE_TYPE_LABELS } from '../utils/constants.js'

const emit = defineEmits(['markerClick', 'venueMarkerClick', 'locationPicked'])
const props = defineProps({
  isPicking: { type: Boolean, default: false },
  visibleCategories: {
    type: Object,
    default: () => ({ club: true, academy: true, practice_room: true, event: true }),
  },
})

const { events } = useEvents()
const { venues } = useVenues()

// 카카오맵 인스턴스
let map = null
let eventMarkers = []
let venueMarkers = []
let tempMarker = null

// 커스텀 마커 SVG 생성
function createMarkerImage(color) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="40" viewBox="0 0 28 40">
    <path d="M14 0C6.3 0 0 6.3 0 14c0 10.5 14 26 14 26s14-15.5 14-26C28 6.3 21.7 0 14 0z" fill="${color}"/>
    <circle cx="14" cy="14" r="6" fill="white" opacity="0.9"/>
  </svg>`
  const size = new window.kakao.maps.Size(28, 40)
  const opt = { offset: new window.kakao.maps.Point(14, 40) }
  return new window.kakao.maps.MarkerImage(
    'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg),
    size, opt
  )
}

// 마커 이미지 캐시
const markerImages = {}
function getMarkerImage(color) {
  if (!markerImages[color]) markerImages[color] = createMarkerImage(color)
  return markerImages[color]
}

// 유형별 색상
const venueColors = { club: '#9b59b6', academy: '#3498db', practice_room: '#2ecc71' }
const eventColor = '#e74c3c'

// 지도 초기화
onMounted(async () => {
  if (window.kakao && window.kakao.maps) {
    await new Promise(resolve => window.kakao.maps.load(resolve))
  }

  const container = document.getElementById('map')
  map = new window.kakao.maps.Map(container, {
    center: new window.kakao.maps.LatLng(37.5665, 126.9780),
    level: 7,
  })

  // 지도 클릭 → 위치 선택 모드
  window.kakao.maps.event.addListener(map, 'click', (mouseEvent) => {
    if (!props.isPicking) return
    const latlng = mouseEvent.latLng

    if (tempMarker) tempMarker.setMap(null)
    tempMarker = new window.kakao.maps.Marker({ position: latlng, map })

    const geocoder = new window.kakao.maps.services.Geocoder()
    geocoder.coord2Address(latlng.getLng(), latlng.getLat(), (result, status) => {
      let address = ''
      if (status === window.kakao.maps.services.Status.OK && result[0]) {
        address = result[0].road_address
          ? result[0].road_address.address_name
          : result[0].address.address_name
      }
      emit('locationPicked', { lat: latlng.getLat(), lng: latlng.getLng(), address })
    })
  })
})

// 이벤트 마커 렌더링
watch(events, (evts) => {
  renderEventMarkers(evts)
}, { immediate: false })

// 장소 마커 렌더링
watch(venues, (vns) => {
  renderVenueMarkers(vns)
}, { immediate: false })

// 카테고리 표시/숨김
watch(() => props.visibleCategories, (cats) => {
  eventMarkers.forEach(m => m.setMap(cats.event ? map : null))
  venueMarkers.forEach(m => {
    m.setMap(cats[m._venueType] ? map : null)
  })
}, { deep: true })

function renderEventMarkers(evts) {
  eventMarkers.forEach(m => m.setMap(null))
  eventMarkers = []

  evts.forEach(ev => {
    const pos = new window.kakao.maps.LatLng(ev.latitude, ev.longitude)
    const marker = new window.kakao.maps.Marker({
      position: pos,
      map: props.visibleCategories.event ? map : null,
      image: getMarkerImage(eventColor),
    })

    const infoContent = `
      <div style="padding:6px 10px;font-size:13px;white-space:nowrap">
        <strong>${ev.title}</strong><br/>
        <span style="color:#888;font-size:11px">${formatDate(ev.start_date)}</span>
      </div>`
    const infowindow = new window.kakao.maps.InfoWindow({ content: infoContent })

    window.kakao.maps.event.addListener(marker, 'mouseover', () => infowindow.open(map, marker))
    window.kakao.maps.event.addListener(marker, 'mouseout', () => infowindow.close())
    window.kakao.maps.event.addListener(marker, 'click', () => emit('markerClick', ev))

    eventMarkers.push(marker)
  })
}

function renderVenueMarkers(vns) {
  venueMarkers.forEach(m => m.setMap(null))
  venueMarkers = []

  vns.forEach(v => {
    const pos = new window.kakao.maps.LatLng(v.latitude, v.longitude)
    const color = venueColors[v.venue_type] || '#999'
    const marker = new window.kakao.maps.Marker({
      position: pos,
      map: props.visibleCategories[v.venue_type] ? map : null,
      image: getMarkerImage(color),
    })
    marker._venueType = v.venue_type

    const typeLabel = VENUE_TYPE_LABELS[v.venue_type] || ''
    const infoContent = `
      <div style="padding:6px 10px;font-size:13px;white-space:nowrap">
        <span style="color:${color};font-size:11px;font-weight:600">${typeLabel}</span><br/>
        <strong>${v.name}</strong>
      </div>`
    const infowindow = new window.kakao.maps.InfoWindow({ content: infoContent })

    window.kakao.maps.event.addListener(marker, 'mouseover', () => infowindow.open(map, marker))
    window.kakao.maps.event.addListener(marker, 'mouseout', () => infowindow.close())
    window.kakao.maps.event.addListener(marker, 'click', () => emit('venueMarkerClick', v))

    venueMarkers.push(marker)
  })
}

// 위치 선택 모드 전환 시 마커 숨김/복원
watch(() => props.isPicking, (picking) => {
  if (picking) {
    eventMarkers.forEach(m => m.setMap(null))
    venueMarkers.forEach(m => m.setMap(null))
  } else {
    eventMarkers.forEach(m => {
      if (props.visibleCategories.event) m.setMap(map)
    })
    venueMarkers.forEach(m => {
      if (props.visibleCategories[m._venueType]) m.setMap(map)
    })
    if (tempMarker) { tempMarker.setMap(null); tempMarker = null }
  }
})

function panTo(lat, lng) {
  if (map) map.panTo(new window.kakao.maps.LatLng(lat, lng))
}

function clearTempMarker() {
  if (tempMarker) { tempMarker.setMap(null); tempMarker = null }
}

defineExpose({ panTo, clearTempMarker, renderEventMarkers, renderVenueMarkers })
</script>
