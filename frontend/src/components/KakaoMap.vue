<template>
  <div id="map" :class="{ picking: isPicking }"></div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useEvents } from '../composables/useEvents.js'
import { useVenues } from '../composables/useVenues.js'
import { formatDate } from '../utils/api.js'
import { VENUE_TYPE_LABELS } from '../utils/constants.js'

const emit = defineEmits(['markerClick', 'venueMarkerClick', 'locationPicked', 'boundsChanged'])
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
let activeInfowindow = null
let eventClusterer = null
let venueClusterer = null

// 커스텀 마커 SVG 생성 (small: 기본, large: 선택됨)
function createMarkerImage(color, size = 'small') {
  const w = size === 'large' ? 36 : 24
  const h = size === 'large' ? 52 : 34
  const cx = w / 2
  const cy = Math.floor(w / 2)
  const r = size === 'large' ? 8 : 5
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
    <path d="M${cx} 0C${cx * 0.45} 0 0 ${cy * 0.45} 0 ${cy}c0 ${Math.floor(h * 0.375)} ${cx} ${h - cy} ${cx} ${h - cy}s${cx}-${Math.floor(h * 0.554)} ${cx}-${h - cy}C${w} ${cy * 0.45} ${cx * 1.55} 0 ${cx} 0z" fill="${color}" stroke="${size === 'large' ? '#fff' : 'none'}" stroke-width="${size === 'large' ? 2 : 0}"/>
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="white" opacity="0.9"/>
  </svg>`
  const imgSize = new window.kakao.maps.Size(w, h)
  const opt = { offset: new window.kakao.maps.Point(cx, h) }
  return new window.kakao.maps.MarkerImage(
    'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg),
    imgSize, opt
  )
}

// 마커 이미지 캐시
const markerImages = {}
function getMarkerImage(color, size = 'small') {
  const key = `${color}_${size}`
  if (!markerImages[key]) markerImages[key] = createMarkerImage(color, size)
  return markerImages[key]
}

// 선택된 마커 추적
let selectedMarker = null
let selectedMarkerColor = null
let selectedMarkerId = null
let selectedMarkerType = null  // 'event' or 'venue'

function selectMarker(marker, color, id, type) {
  // 이전 선택 해제
  if (selectedMarker) {
    selectedMarker.setImage(getMarkerImage(selectedMarkerColor, 'small'))
  }
  // 새 마커 선택
  selectedMarker = marker
  selectedMarkerColor = color
  selectedMarkerId = id
  selectedMarkerType = type
  marker.setImage(getMarkerImage(color, 'large'))
}

function deselectMarker() {
  if (selectedMarker) {
    selectedMarker.setImage(getMarkerImage(selectedMarkerColor, 'small'))
  }
  selectedMarker = null
  selectedMarkerColor = null
  selectedMarkerId = null
  selectedMarkerType = null
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

  // 클러스터러 생성
  eventClusterer = new window.kakao.maps.MarkerClusterer({
    map: map,
    averageCenter: true,
    minLevel: 4,
    styles: [{
      width: '36px', height: '36px',
      background: '#e74c3c', color: '#fff',
      borderRadius: '18px', textAlign: 'center', lineHeight: '36px',
      fontSize: '13px', fontWeight: 'bold'
    }]
  })

  venueClusterer = new window.kakao.maps.MarkerClusterer({
    map: map,
    averageCenter: true,
    minLevel: 4,
    styles: [{
      width: '36px', height: '36px',
      background: '#9b59b6', color: '#fff',
      borderRadius: '18px', textAlign: 'center', lineHeight: '36px',
      fontSize: '13px', fontWeight: 'bold'
    }]
  })

  // 지도 영역 변경 시 bounds 전달
  function emitBounds() {
    const bounds = map.getBounds()
    const sw = bounds.getSouthWest()
    const ne = bounds.getNorthEast()
    const center = map.getCenter()
    emit('boundsChanged', {
      swLat: sw.getLat(), swLng: sw.getLng(),
      neLat: ne.getLat(), neLng: ne.getLng(),
      centerLat: center.getLat(), centerLng: center.getLng(),
    })
  }
  window.kakao.maps.event.addListener(map, 'idle', emitBounds)
  // 초기 bounds 전달 (타일 로드 후)
  window.kakao.maps.event.addListener(map, 'tilesloaded', function onTiles() {
    emitBounds()
    window.kakao.maps.event.removeListener(map, 'tilesloaded', onTiles)
  })

  // 지도 클릭/드래그 시 입력 포커스 해제
  window.kakao.maps.event.addListener(map, 'dragstart', () => {
    document.activeElement.blur()
  })

  // 지도 클릭 → 위치 선택 모드
  window.kakao.maps.event.addListener(map, 'click', (mouseEvent) => {
    document.activeElement.blur()
    if (activeInfowindow) { activeInfowindow.close(); activeInfowindow = null }
    deselectMarker()
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
  if (events.value.length) renderEventMarkers(events.value)
  if (venues.value.length) renderVenueMarkers(venues.value)
})

// 이벤트 마커 렌더링
watch(events, (evts) => {
  if (map) renderEventMarkers(evts)
}, { immediate: true })

// 장소 마커 렌더링
watch(venues, (vns) => {
  if (map) renderVenueMarkers(vns)
}, { immediate: true })

// 카테고리 표시/숨김
watch(() => props.visibleCategories, (cats) => {
  if (eventClusterer) {
    eventClusterer.clear()
    if (cats.event) eventClusterer.addMarkers(eventMarkers)
  }
  if (venueClusterer) {
    venueClusterer.clear()
    const visibleMarkers = venueMarkers.filter(m => cats[m._venueType])
    venueClusterer.addMarkers(visibleMarkers)
  }
}, { deep: true })

function renderEventMarkers(evts) {
  eventMarkers.forEach(m => m.setMap(null))
  if (eventClusterer) eventClusterer.clear()
  eventMarkers = []

  evts.forEach(ev => {
    const pos = new window.kakao.maps.LatLng(ev.latitude, ev.longitude)
    const marker = new window.kakao.maps.Marker({
      position: pos,
      image: getMarkerImage(eventColor),
    })

    const infoContent = `
      <div style="padding:6px 10px;font-size:13px;white-space:nowrap">
        <strong>${ev.title}</strong><br/>
        <span style="color:#888;font-size:11px">${formatDate(ev.start_date)}</span>
      </div>`
    const infowindow = new window.kakao.maps.InfoWindow({ content: infoContent })

    window.kakao.maps.event.addListener(marker, 'mouseover', () => {
      if (!('ontouchstart' in window)) {
        infowindow.open(map, marker)
      }
    })
    window.kakao.maps.event.addListener(marker, 'mouseout', () => {
      if (!('ontouchstart' in window)) {
        infowindow.close()
      }
    })
    window.kakao.maps.event.addListener(marker, 'click', () => {
      document.activeElement.blur()
      selectMarker(marker, eventColor, ev.id, 'event')

      if ('ontouchstart' in window) {
        if (activeInfowindow === infowindow) {
          emit('markerClick', ev)
          infowindow.close()
          activeInfowindow = null
        } else {
          if (activeInfowindow) activeInfowindow.close()
          infowindow.open(map, marker)
          activeInfowindow = infowindow
        }
      } else {
        emit('markerClick', ev)
      }
    })

    // 선택 상태 복원
    if (selectedMarkerType === 'event' && selectedMarkerId === ev.id) {
      marker.setImage(getMarkerImage(eventColor, 'large'))
      selectedMarker = marker
      selectedMarkerColor = eventColor
    }

    eventMarkers.push(marker)
  })

  if (eventClusterer && props.visibleCategories.event) {
    eventClusterer.addMarkers(eventMarkers)
  }
}

function renderVenueMarkers(vns) {
  venueMarkers.forEach(m => m.setMap(null))
  if (venueClusterer) venueClusterer.clear()
  venueMarkers = []

  vns.forEach(v => {
    const pos = new window.kakao.maps.LatLng(v.latitude, v.longitude)
    const color = venueColors[v.venue_type] || '#999'
    const marker = new window.kakao.maps.Marker({
      position: pos,
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

    window.kakao.maps.event.addListener(marker, 'mouseover', () => {
      if (!('ontouchstart' in window)) {
        infowindow.open(map, marker)
      }
    })
    window.kakao.maps.event.addListener(marker, 'mouseout', () => {
      if (!('ontouchstart' in window)) {
        infowindow.close()
      }
    })
    window.kakao.maps.event.addListener(marker, 'click', () => {
      document.activeElement.blur()
      selectMarker(marker, color, v.id, 'venue')

      if ('ontouchstart' in window) {
        if (activeInfowindow === infowindow) {
          emit('venueMarkerClick', v)
          infowindow.close()
          activeInfowindow = null
        } else {
          if (activeInfowindow) activeInfowindow.close()
          infowindow.open(map, marker)
          activeInfowindow = infowindow
        }
      } else {
        emit('venueMarkerClick', v)
      }
    })

    // 선택 상태 복원
    if (selectedMarkerType === 'venue' && selectedMarkerId === v.id) {
      marker.setImage(getMarkerImage(color, 'large'))
      selectedMarker = marker
      selectedMarkerColor = color
    }

    venueMarkers.push(marker)
  })

  if (venueClusterer) {
    const visibleMarkers = venueMarkers.filter(m => props.visibleCategories[m._venueType])
    venueClusterer.addMarkers(visibleMarkers)
  }
}

// 위치 선택 모드 전환 시 마커 숨김/복원
watch(() => props.isPicking, (picking) => {
  if (picking) {
    if (eventClusterer) eventClusterer.clear()
    if (venueClusterer) venueClusterer.clear()
  } else {
    if (eventClusterer && props.visibleCategories.event) {
      eventClusterer.addMarkers(eventMarkers)
    }
    if (venueClusterer) {
      const visibleMarkers = venueMarkers.filter(m => props.visibleCategories[m._venueType])
      venueClusterer.addMarkers(visibleMarkers)
    }
    if (tempMarker) { tempMarker.setMap(null); tempMarker = null }
  }
})

function panTo(lat, lng) {
  if (map) map.panTo(new window.kakao.maps.LatLng(lat, lng))
}

function clearTempMarker() {
  if (tempMarker) { tempMarker.setMap(null); tempMarker = null }
}

function selectMarkerById(id, type) {
  const markers = type === 'event' ? eventMarkers : venueMarkers
  const color = type === 'event' ? eventColor : null
  // 이벤트 목록이나 장소 목록에서 해당 항목 찾기
  const items = type === 'event' ? events.value : venues.value
  const idx = items.findIndex(item => item.id === id)
  if (idx >= 0 && markers[idx]) {
    const c = type === 'event' ? eventColor : (venueColors[items[idx].venue_type] || '#999')
    selectMarker(markers[idx], c, id, type)
  }
}

defineExpose({ panTo, clearTempMarker, renderEventMarkers, renderVenueMarkers, selectMarkerById })
</script>
