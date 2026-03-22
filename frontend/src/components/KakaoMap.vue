<template>
  <div id="map" :class="{ picking: isPicking }"></div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useEvents } from '../composables/useEvents.js'
import { useVenues } from '../composables/useVenues.js'
import { formatDate } from '../utils/api.js'
import { VENUE_TYPE_LABELS, GENRE_LABELS } from '../utils/constants.js'
import markerClubImg from '@/assets/maker_club.png'
import markerSchoolImg from '@/assets/maker_shcool.png'
import markerPracticeImg from '@/assets/maker_practice.png'
import markerEventImg from '@/assets/maker_event.png'

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

// 카테고리별 마커 이미지 매핑
const markerImageSrc = {
  club: markerClubImg,
  academy: markerSchoolImg,
  practice_room: markerPracticeImg,
  event: markerEventImg,
}

// 색상→타입 매핑
const colorToType = {
  '#2E6EB5': 'club', '#D4A84C': 'academy', '#4EA89E': 'practice_room', '#7B2D8E': 'event',
}

// 원형 마커 이미지를 Canvas로 생성
function createCircleMarkerImage(src, size) {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = size
      canvas.height = size
      const ctx = canvas.getContext('2d')
      // 원형 클리핑
      ctx.beginPath()
      ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2)
      ctx.closePath()
      ctx.clip()
      // 이미지 그리기
      ctx.drawImage(img, 0, 0, size, size)
      // 원형 테두리
      ctx.beginPath()
      ctx.arc(size / 2, size / 2, size / 2 - 1, 0, Math.PI * 2)
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 2
      ctx.stroke()

      resolve(new window.kakao.maps.MarkerImage(
        canvas.toDataURL(),
        new window.kakao.maps.Size(size, size),
        { offset: new window.kakao.maps.Point(size / 2, size / 2) }
      ))
    }
    img.src = src
  })
}

// 마커 이미지 캐시 (비동기 로드)
const markerImages = {}
const markerImagePromises = {}

function preloadMarkerImages() {
  const sizes = { small: 40, large: 55 }
  for (const [type, src] of Object.entries(markerImageSrc)) {
    for (const [sizeName, sizeVal] of Object.entries(sizes)) {
      const key = `${type}_${sizeName}`
      markerImagePromises[key] = createCircleMarkerImage(src, sizeVal).then(img => {
        markerImages[key] = img
      })
    }
  }
}

function getMarkerImage(colorOrType, size = 'small') {
  const type = colorToType[colorOrType] || colorOrType
  const key = `${type}_${size}`
  return markerImages[key] || null
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
const venueColors = { club: '#2E6EB5', academy: '#D4A84C', practice_room: '#4EA89E' }
const eventColor = '#7B2D8E'

// 지도 초기화
onMounted(async () => {
  if (window.kakao && window.kakao.maps) {
    await new Promise(resolve => window.kakao.maps.load(resolve))
  }

  // 마커 이미지 프리로드
  preloadMarkerImages()
  await Promise.all(Object.values(markerImagePromises))

  const container = document.getElementById('map')
  map = new window.kakao.maps.Map(container, {
    center: new window.kakao.maps.LatLng(37.5665, 126.9780),
    level: 7,
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
  eventMarkers.forEach(m => m.setMap(cats.event ? map : null))
  venueMarkers.forEach(m => m.setMap(cats[m._venueType] ? map : null))
}, { deep: true })

function renderEventMarkers(evts) {
  eventMarkers.forEach(m => m.setMap(null))
  eventMarkers = []

  evts.forEach(ev => {
    const pos = new window.kakao.maps.LatLng(ev.latitude, ev.longitude)
    const marker = new window.kakao.maps.Marker({
      position: pos,
      image: getMarkerImage(eventColor),
    })

    const thumb = ev.media?.[0]?.url
    const genres = (ev.dance_genres || []).map(g => GENRE_LABELS[g] || g).join(' · ')
    const infoContent = `
      <div style="display:flex;align-items:center;gap:8px;padding:8px 10px;font-size:13px;white-space:nowrap">
        ${thumb ? `<img src="${thumb}" style="width:50px;height:50px;border-radius:6px;object-fit:cover;" />` : ''}
        <div>
          <strong>${ev.title}</strong><br/>
          <span style="color:#888;font-size:11px">${formatDate(ev.start_date)}</span>
          ${genres ? `<br/><span style="font-size:10px;color:#5BA89E">${genres}</span>` : ''}
        </div>
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

    if (props.visibleCategories.event) marker.setMap(map)
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
      image: getMarkerImage(color),
    })
    marker._venueType = v.venue_type

    const typeLabel = VENUE_TYPE_LABELS[v.venue_type] || ''
    const thumb = v.media?.[0]?.url
    const vGenres = (v.dance_genres || []).map(g => GENRE_LABELS[g] || g).join(' · ')
    const infoContent = `
      <div style="display:flex;align-items:center;gap:8px;padding:8px 10px;font-size:13px;white-space:nowrap">
        ${thumb ? `<img src="${thumb}" style="width:50px;height:50px;border-radius:6px;object-fit:cover;" />` : ''}
        <div>
          <span style="color:${color};font-size:11px;font-weight:600">${typeLabel}</span><br/>
          <strong>${v.name}</strong>
          ${vGenres ? `<br/><span style="font-size:10px;color:#5BA89E">${vGenres}</span>` : ''}
        </div>
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

    if (props.visibleCategories[v.venue_type]) marker.setMap(map)
    venueMarkers.push(marker)
  })
}

// 위치 선택 모드 전환 시 마커 숨김/복원
watch(() => props.isPicking, (picking) => {
  if (picking) {
    eventMarkers.forEach(m => m.setMap(null))
    venueMarkers.forEach(m => m.setMap(null))
  } else {
    const cats = props.visibleCategories
    eventMarkers.forEach(m => m.setMap(cats.event ? map : null))
    venueMarkers.forEach(m => m.setMap(cats[m._venueType] ? map : null))
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
