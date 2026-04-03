<template>
  <div id="map" :class="{ picking: isPicking }"></div>
  <button class="my-location-btn" :class="{ locating: isLocating }" @click="goToMyLocation" title="내 위치" :disabled="isLocating">{{ isLocating ? '⏳' : '📍' }}</button>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useEvents } from '../composables/useEvents.js'
import { useVenues } from '../composables/useVenues.js'
import { formatDate } from '../utils/api.js'
import { VENUE_TYPE_LABELS, GENRE_LABELS } from '../utils/constants.js'
import markerClubImg from '@/assets/maker_club.png'
import markerSchoolImg from '@/assets/maker_shcool.png'
import markerPracticeImg from '@/assets/maker_practice.png'
import markerEventImg from '@/assets/maker_event.png'
import defaultThumbImg from '@/assets/camera.png'

const emit = defineEmits(['markerClick', 'venueMarkerClick', 'locationPicked', 'boundsChanged'])
const props = defineProps({
  isPicking: { type: Boolean, default: false },
  visibleCategories: {
    type: Object,
    default: () => ({ club: true, academy: true, practice_room: true, event: true }),
  },
  selectedGenres: {
    type: Array,
    default: () => [],
  },
  selectedDays: {
    type: Array,
    default: () => [],
  },
  selectedEventTypes: {
    type: Array,
    default: () => [],
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

// 말풍선 클릭 → 상세 보기 (글로벌 함수)
const infoItemStore = {}
function closeAllInfowindows() {
  const evts = [...eventInfowindows]
  const vens = [...venueInfowindows]
  activeInfowindow = null
  evts.forEach(iw => iw.close())
  vens.forEach(iw => iw.close())
}
window.__windycity_closeInfowindows = closeAllInfowindows

window.__windycity_infoClick = (key) => {
  const item = infoItemStore[key]
  if (!item) return
  closeAllInfowindows()
  if (item.type === 'event') emit('markerClick', item.data)
  else emit('venueMarkerClick', item.data)
}

window.__windycity_badgeClick = (key) => {
  const item = infoItemStore[key]
  if (!item || item.type !== 'badge') return
  closeAllInfowindows()
  const { group, lat, lng } = item
  const listItems = group.map(e => {
    const listKey = `event_${e.id}`
    infoItemStore[listKey] = { type: 'event', data: e }
    const listThumb = e.media?.[0]?.url
    return `<div onclick="window.__windycity_infoClick('${listKey}')" style="display:flex;align-items:center;gap:8px;padding:6px 0;cursor:pointer;border-bottom:1px solid #EDE5DB;">
      <img src="${listThumb || defaultThumbImg}" style="width:36px;height:36px;border-radius:4px;object-fit:cover;background:#EDE5DB;" />
      <div style="min-width:0;flex:1;overflow:hidden;">
        <strong style="font-size:12px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${e.title}</strong>
        <span style="color:#888;font-size:10px">${formatDate(e.event_date)}</span>
      </div>
    </div>`
  }).join('')
  const groupContent = `
    <div style="padding:8px 10px;font-size:13px;width:180px;overflow:hidden;">
    <div style="font-weight:700;margin-bottom:6px;font-size:12px;color:#7B2D8E;">📍 이 위치 강습·행사 ${group.length}건</div>
    <div style="max-height:160px;overflow-y:auto;">
      ${listItems}
    </div>
    <div style="height:1px;"></div>
  </div>`
  const anchorMarker = eventMarkers.find(m => {
    const mp = m.getPosition()
    return mp.getLat().toFixed(6) === lat.toFixed(6) && mp.getLng().toFixed(6) === lng.toFixed(6)
  })
  const groupInfowindow = new window.kakao.maps.InfoWindow({ content: groupContent })
  groupInfowindow.open(map, anchorMarker || map)
  activeInfowindow = groupInfowindow
  eventInfowindows.push(groupInfowindow)
}

window.__windycity_venueBadgeClick = (key) => {
  const item = infoItemStore[key]
  if (!item || item.type !== 'venue_badge') return
  closeAllInfowindows()
  const { group, lat, lng } = item
  const listItems = group.map(v => {
    const listKey = `venue_${v.id}`
    infoItemStore[listKey] = { type: 'venue', data: v }
    const listThumb = v.media?.[0]?.url
    const typeLabel = VENUE_TYPE_LABELS[v.venue_type] || ''
    const typeColor = venueColors[v.venue_type] || '#999'
    return `<div onclick="window.__windycity_infoClick('${listKey}')" style="display:flex;align-items:center;gap:8px;padding:6px 0;cursor:pointer;border-bottom:1px solid #EDE5DB;">
      <img src="${listThumb || defaultThumbImg}" style="width:36px;height:36px;border-radius:4px;object-fit:cover;background:#EDE5DB;" />
      <div style="min-width:0;flex:1;overflow:hidden;">
        <span style="color:${typeColor};font-size:10px;font-weight:600">${typeLabel}</span>
        <strong style="font-size:12px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${v.name}</strong>
      </div>
    </div>`
  }).join('')
  const groupContent = `
    <div style="padding:8px 10px;font-size:13px;width:180px;overflow:hidden;">
    <div style="font-weight:700;margin-bottom:6px;font-size:12px;color:#FF8C00;">📍 이 위치 장소 ${group.length}건</div>
    <div style="max-height:160px;overflow-y:auto;">
      ${listItems}
    </div>
    <div style="height:1px;"></div>
  </div>`
  const anchorMarker = venueMarkers.find(m => {
    const mp = m.getPosition()
    return mp.getLat().toFixed(6) === lat.toFixed(6) && mp.getLng().toFixed(6) === lng.toFixed(6)
  })
  const groupInfowindow = new window.kakao.maps.InfoWindow({ content: groupContent })
  groupInfowindow.open(map, anchorMarker || map)
  activeInfowindow = groupInfowindow
  venueInfowindows.push(groupInfowindow)
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
  const saved = JSON.parse(localStorage.getItem('mapPosition') || 'null')
  map = new window.kakao.maps.Map(container, {
    center: new window.kakao.maps.LatLng(saved?.lat || 37.4979, saved?.lng || 127.0276),
    level: saved?.level || 7,
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
  window.kakao.maps.event.addListener(map, 'idle', () => {
    emitBounds()
    const center = map.getCenter()
    localStorage.setItem('mapPosition', JSON.stringify({
      lat: center.getLat(), lng: center.getLng(), level: map.getLevel()
    }))
  })
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
    closeAllInfowindows()
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

// 장르 필터 매칭
function matchesGenreFilter(genres) {
  if (props.selectedGenres.length === 0) return true
  return props.selectedGenres.some(g => genres.includes(g))
}

// 행사 종류 필터 매칭 (이벤트만 해당)
function matchesEventTypeFilter(ev) {
  if (props.selectedEventTypes.length === 0) return true
  return props.selectedEventTypes.includes(ev.event_type)
}

// 요일 필터 매칭 (이벤트만 해당)
const WEEKDAY_TO_DAY = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
function matchesDayFilter(ev) {
  if (props.selectedDays.length === 0) return true
  if (ev.is_recurring && ev.recurrence_rule?.days) {
    return ev.recurrence_rule.days.some(d => props.selectedDays.includes(d))
  }
  const weekday = new Date(ev.event_date).getDay()
  const dayKey = WEEKDAY_TO_DAY[weekday === 0 ? 6 : weekday - 1]
  return props.selectedDays.includes(dayKey)
}

// 카테고리+장르 표시/숨김
function updateMarkerVisibility() {
  const cats = props.visibleCategories
  eventMarkers.forEach(m => {
    const visible = cats.event && matchesGenreFilter(m._genres) && matchesDayFilter(m._event) && matchesEventTypeFilter(m._event)
    m.setMap(visible ? map : null)
  })
  venueMarkers.forEach(m => {
    const visible = cats[m._venueType] && matchesGenreFilter(m._genres)
    m.setMap(visible ? map : null)
  })
  renderBadges()
}

watch(() => props.visibleCategories, () => updateMarkerVisibility(), { deep: true })
watch(() => props.selectedGenres, () => updateMarkerVisibility(), { deep: true })
watch(() => props.selectedDays, () => updateMarkerVisibility(), { deep: true })
watch(() => props.selectedEventTypes, () => updateMarkerVisibility(), { deep: true })

let eventInfowindows = []
let venueInfowindows = []
let eventBadgeOverlays = []
let venueBadgeOverlays = []

function renderEventMarkers(evts) {
  eventMarkers.forEach(m => m.setMap(null))
  eventBadgeOverlays.forEach(o => o.setMap(null))
  eventInfowindows.forEach(iw => iw.close())
  eventMarkers = []
  eventInfowindows = []
  eventBadgeOverlays = []

  // 좌표별 이벤트 그룹핑
  const coordMap = {}
  evts.forEach(ev => {
    const key = `${ev.latitude.toFixed(6)}_${ev.longitude.toFixed(6)}`
    if (!coordMap[key]) coordMap[key] = []
    coordMap[key].push(ev)
  })

  evts.forEach(ev => {
    const pos = new window.kakao.maps.LatLng(ev.latitude, ev.longitude)
    const marker = new window.kakao.maps.Marker({
      position: pos,
      image: getMarkerImage(eventColor),
    })

    const thumb = ev.media?.[0]?.url
    const genres = (ev.dance_genres || []).map(g => GENRE_LABELS[g] || g).join(' · ')
    const infoKey = `event_${ev.id}`
    infoItemStore[infoKey] = { type: 'event', data: ev }
    const infoContent = `
      <div onclick="window.__windycity_infoClick('${infoKey}')" style="display:flex;align-items:flex-start;gap:8px;padding:8px 10px;font-size:13px;max-width:250px;cursor:pointer">
        <img src="${thumb || defaultThumbImg}" style="width:50px;height:50px;border-radius:6px;object-fit:cover;background:#EDE5DB;flex-shrink:0" />
        <div style="min-width:0">
          <strong style="display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${ev.title}</strong>
          <span style="color:#888;font-size:11px">${formatDate(ev.event_date)}</span>
          ${genres ? `<br/><span style="font-size:10px;color:#5BA89E">${genres}</span>` : ''}
        </div>
      </div>`
    const infowindow = new window.kakao.maps.InfoWindow({ content: infoContent })
    eventInfowindows.push(infowindow)

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
    // 동일 좌표 그룹 정보
    const coordKey = `${ev.latitude.toFixed(6)}_${ev.longitude.toFixed(6)}`
    const group = coordMap[coordKey]

    window.kakao.maps.event.addListener(marker, 'click', () => {
      document.activeElement.blur()
      selectMarker(marker, eventColor, ev.id, 'event')

      if (group.length >= 2) {
        // 동일 좌표 이벤트 목록 말풍선
        closeAllInfowindows()
        const listItems = group.map(e => {
          const listKey = `event_${e.id}`
          infoItemStore[listKey] = { type: 'event', data: e }
          const listThumb = e.media?.[0]?.url
          return `<div onclick="window.__windycity_infoClick('${listKey}')" style="display:flex;align-items:center;gap:8px;padding:6px 0;cursor:pointer;border-bottom:1px solid #EDE5DB;">
            <img src="${listThumb || defaultThumbImg}" style="width:36px;height:36px;border-radius:4px;object-fit:cover;background:#EDE5DB;" />
            <div style="min-width:0;flex:1;overflow:hidden;">
              <strong style="font-size:12px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${e.title}</strong>
              <span style="color:#888;font-size:10px">${formatDate(e.event_date)}</span>
            </div>
          </div>`
        }).join('')
        const groupContent = `
        <div style="padding:8px 10px;font-size:13px;width:180px;overflow:hidden;">
          <div style="font-weight:700;margin-bottom:6px;font-size:12px;color:#7B2D8E;">📍 이 위치 강습·행사 ${group.length}건</div>
          <div style="max-height:160px;overflow-y:auto;">
            ${listItems}
          </div>          
          <div style="height: 1px;"></div>
        </div>`
        const groupInfowindow = new window.kakao.maps.InfoWindow({ content: groupContent })
        groupInfowindow.open(map, marker)
        activeInfowindow = groupInfowindow
        eventInfowindows.push(groupInfowindow)
      } else {
        if ('ontouchstart' in window) {
          if (activeInfowindow === infowindow) {
            closeAllInfowindows()
            emit('markerClick', ev)
          } else {
            closeAllInfowindows()
            infowindow.open(map, marker)
            activeInfowindow = infowindow
          }
        } else {
          closeAllInfowindows()
          emit('markerClick', ev)
        }
      }
    })

    // 선택 상태 복원
    if (selectedMarkerType === 'event' && selectedMarkerId === ev.id) {
      marker.setImage(getMarkerImage(eventColor, 'large'))
      selectedMarker = marker
      selectedMarkerColor = eventColor
    }

    marker._genres = ev.dance_genres || []
    marker._event = ev
    if (props.visibleCategories.event && matchesGenreFilter(marker._genres) && matchesDayFilter(ev) && matchesEventTypeFilter(ev)) marker.setMap(map)
    eventMarkers.push(marker)
  })

  // 뱃지는 renderBadges()에서 통합 처리
  renderBadges()
}

function renderVenueMarkers(vns) {
  venueMarkers.forEach(m => m.setMap(null))
  venueBadgeOverlays.forEach(o => o.setMap(null))
  venueInfowindows.forEach(iw => iw.close())
  venueMarkers = []
  venueBadgeOverlays = []
  venueInfowindows = []

  // 좌표별 장소 그룹핑
  const venueCoordMap = {}
  vns.forEach(v => {
    const key = `${v.latitude.toFixed(6)}_${v.longitude.toFixed(6)}`
    if (!venueCoordMap[key]) venueCoordMap[key] = []
    venueCoordMap[key].push(v)
  })

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
    const infoKey = `venue_${v.id}`
    infoItemStore[infoKey] = { type: 'venue', data: v }
    const infoContent = `
      <div onclick="window.__windycity_infoClick('${infoKey}')" style="display:flex;align-items:flex-start;gap:8px;padding:8px 10px;font-size:13px;max-width:250px;cursor:pointer">
        <img src="${thumb || defaultThumbImg}" style="width:50px;height:50px;border-radius:6px;object-fit:cover;background:#EDE5DB;flex-shrink:0" />
        <div style="min-width:0">
          <span style="color:${color};font-size:11px;font-weight:600">${typeLabel}</span><br/>
          <strong style="display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${v.name}</strong>
          ${vGenres ? `<span style="font-size:10px;color:#5BA89E">${vGenres}</span>` : ''}
        </div>
      </div>`
    const infowindow = new window.kakao.maps.InfoWindow({ content: infoContent })
    venueInfowindows.push(infowindow)

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
    // 동일 좌표 그룹 정보
    const venueCoordKey = `${v.latitude.toFixed(6)}_${v.longitude.toFixed(6)}`
    const venueGroup = venueCoordMap[venueCoordKey]

    window.kakao.maps.event.addListener(marker, 'click', () => {
      document.activeElement.blur()
      selectMarker(marker, color, v.id, 'venue')

      if (venueGroup.length >= 2) {
        // 동일 좌표 장소 목록 말풍선
        closeAllInfowindows()
        const listItems = venueGroup.map(vv => {
          const listKey = `venue_${vv.id}`
          infoItemStore[listKey] = { type: 'venue', data: vv }
          const listThumb = vv.media?.[0]?.url
          const tLabel = VENUE_TYPE_LABELS[vv.venue_type] || ''
          const tColor = venueColors[vv.venue_type] || '#999'
          return `<div onclick="window.__windycity_infoClick('${listKey}')" style="display:flex;align-items:center;gap:8px;padding:6px 0;cursor:pointer;border-bottom:1px solid #EDE5DB;">
            <img src="${listThumb || defaultThumbImg}" style="width:36px;height:36px;border-radius:4px;object-fit:cover;background:#EDE5DB;" />
            <div style="min-width:0;flex:1;overflow:hidden;">
              <span style="color:${tColor};font-size:10px;font-weight:600">${tLabel}</span>
              <strong style="font-size:12px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${vv.name}</strong>
            </div>
          </div>`
        }).join('')
        const groupContent = `
        <div style="padding:8px 10px;font-size:13px;width:180px;overflow:hidden;">
          <div style="font-weight:700;margin-bottom:6px;font-size:12px;color:#FF8C00;">📍 이 위치 장소 ${venueGroup.length}건</div>
          <div style="max-height:160px;overflow-y:auto;">
            ${listItems}
          </div>
          <div style="height:1px;"></div>
        </div>`
        const groupInfowindow = new window.kakao.maps.InfoWindow({ content: groupContent })
        groupInfowindow.open(map, marker)
        activeInfowindow = groupInfowindow
        venueInfowindows.push(groupInfowindow)
      } else {
        if ('ontouchstart' in window) {
          if (activeInfowindow === infowindow) {
            closeAllInfowindows()
            emit('venueMarkerClick', v)
          } else {
            closeAllInfowindows()
            infowindow.open(map, marker)
            activeInfowindow = infowindow
          }
        } else {
          closeAllInfowindows()
          emit('venueMarkerClick', v)
        }
      }
    })

    // 선택 상태 복원
    if (selectedMarkerType === 'venue' && selectedMarkerId === v.id) {
      marker.setImage(getMarkerImage(color, 'large'))
      selectedMarker = marker
      selectedMarkerColor = color
    }

    marker._genres = v.dance_genres || []
    if (props.visibleCategories[v.venue_type] && matchesGenreFilter(marker._genres)) marker.setMap(map)
    venueMarkers.push(marker)
  })

  // 뱃지는 renderBadges()에서 통합 처리
  renderBadges()
}

// 이벤트·장소 좌표 충돌을 고려한 통합 뱃지 렌더링
function renderBadges() {
  eventBadgeOverlays.forEach(o => o.setMap(null))
  venueBadgeOverlays.forEach(o => o.setMap(null))
  eventBadgeOverlays = []
  venueBadgeOverlays = []

  // 좌표별 이벤트/장소 그룹핑 (장르+요일 필터 적용)
  const eventCoords = {}
  events.value.forEach(ev => {
    if (!matchesGenreFilter(ev.dance_genres || []) || !matchesDayFilter(ev) || !matchesEventTypeFilter(ev)) return
    const key = `${ev.latitude.toFixed(6)}_${ev.longitude.toFixed(6)}`
    if (!eventCoords[key]) eventCoords[key] = []
    eventCoords[key].push(ev)
  })
  const venueCoords = {}
  venues.value.forEach(v => {
    if (!matchesGenreFilter(v.dance_genres || [])) return
    const key = `${v.latitude.toFixed(6)}_${v.longitude.toFixed(6)}`
    if (!venueCoords[key]) venueCoords[key] = []
    venueCoords[key].push(v)
  })

  // 모든 좌표 키 수집
  const allKeys = new Set([...Object.keys(eventCoords), ...Object.keys(venueCoords)])

  allKeys.forEach(key => {
    const evGroup = eventCoords[key] || []
    const vnGroup = venueCoords[key] || []
    const hasOverlap = evGroup.length > 0 && vnGroup.length > 0
    const lat = evGroup[0]?.latitude ?? vnGroup[0]?.latitude
    const lng = evGroup[0]?.longitude ?? vnGroup[0]?.longitude
    const pos = new window.kakao.maps.LatLng(lat, lng)

    // 이벤트 뱃지: 같은 좌표 이벤트 2개+ OR 장소와 좌표 겹침
    if (evGroup.length >= 2 || hasOverlap) {
      const badgeKey = `badge_${key}`
      infoItemStore[badgeKey] = { type: 'badge', group: evGroup, lat, lng }
      const badge = new window.kakao.maps.CustomOverlay({
        position: pos,
        content: `<div onclick="window.__windycity_badgeClick('${badgeKey}')" style="background:#E74C3C;color:#fff;border-radius:50%;width:20px;height:20px;text-align:center;line-height:20px;font-size:11px;font-weight:700;border:2px solid #fff;transform:translate(12px,-12px);cursor:pointer;">${evGroup.length}</div>`,
        yAnchor: 1,
        xAnchor: 0,
        zIndex: 10,
      })
      if (props.visibleCategories.event) badge.setMap(map)
      eventBadgeOverlays.push(badge)
    }

    // 장소 뱃지: 같은 좌표 장소 2개+ OR 이벤트와 좌표 겹침
    if (vnGroup.length >= 2 || hasOverlap) {
      const badgeKey = `venue_badge_${key}`
      infoItemStore[badgeKey] = { type: 'venue_badge', group: vnGroup, lat, lng }
      const badge = new window.kakao.maps.CustomOverlay({
        position: pos,
        content: `<div onclick="window.__windycity_venueBadgeClick('${badgeKey}')" style="background:#FF8C00;color:#fff;border-radius:50%;width:20px;height:20px;text-align:center;line-height:20px;font-size:11px;font-weight:700;border:2px solid #fff;transform:translate(-12px,-12px);cursor:pointer;">${vnGroup.length}</div>`,
        yAnchor: 1,
        xAnchor: 1,
        zIndex: 10,
      })
      badge._venueTypes = vnGroup.map(vv => vv.venue_type)
      const anyVisible = vnGroup.some(vv => props.visibleCategories[vv.venue_type])
      if (anyVisible) badge.setMap(map)
      venueBadgeOverlays.push(badge)
    }
  })
}

// 위치 선택 모드 전환 시 마커 숨김/복원
watch(() => props.isPicking, (picking) => {
  if (picking) {
    eventMarkers.forEach(m => m.setMap(null))
    eventBadgeOverlays.forEach(o => o.setMap(null))
    venueMarkers.forEach(m => m.setMap(null))
    venueBadgeOverlays.forEach(o => o.setMap(null))
  } else {
    updateMarkerVisibility()
    if (tempMarker) { tempMarker.setMap(null); tempMarker = null }
  }
})

function panTo(lat, lng) {
  if (!map) return
  if (map.getLevel() > 5) map.setLevel(5)
  map.panTo(new window.kakao.maps.LatLng(lat, lng))
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

const isLocating = ref(false)

function goToMyLocation() {
  if (!navigator.geolocation) {
    alert('이 브라우저에서는 위치 서비스를 지원하지 않습니다')
    return
  }
  isLocating.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      isLocating.value = false
      const lat = pos.coords.latitude
      const lng = pos.coords.longitude
      if (map) {
        map.setLevel(4)
        map.panTo(new window.kakao.maps.LatLng(lat, lng))
      }
    },
    () => {
      isLocating.value = false
      alert('위치 정보를 가져올 수 없습니다. 위치 권한을 확인해주세요.')
    },
    { enableHighAccuracy: false, timeout: 5000, maximumAge: 300000 }
  )
}

defineExpose({ panTo, clearTempMarker, renderEventMarkers, renderVenueMarkers, selectMarkerById })
</script>
