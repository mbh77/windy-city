<template>
  <div id="map" :class="{ picking: isPicking }"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useEvents } from '../composables/useEvents.js'
import { formatDate } from '../utils/api.js'

const emit = defineEmits(['markerClick', 'locationPicked'])
const props = defineProps({
  isPicking: { type: Boolean, default: false },
})

const { events } = useEvents()

// 카카오맵 인스턴스 (컴포넌트 내부 상태)
let map = null
let markers = []
let tempMarker = null

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

  // 지도 클릭 → 위치 선택 모드일 때만 동작
  window.kakao.maps.event.addListener(map, 'click', (mouseEvent) => {
    if (!props.isPicking) return
    const latlng = mouseEvent.latLng

    // 기존 임시 마커 제거
    if (tempMarker) tempMarker.setMap(null)

    // 빨간 마커 생성
    tempMarker = new window.kakao.maps.Marker({ position: latlng, map })

    // 역지오코딩으로 주소 가져오기
    const geocoder = new window.kakao.maps.services.Geocoder()
    geocoder.coord2Address(latlng.getLng(), latlng.getLat(), (result, status) => {
      let address = ''
      if (status === window.kakao.maps.services.Status.OK && result[0]) {
        address = result[0].road_address
          ? result[0].road_address.address_name
          : result[0].address.address_name
      }
      emit('locationPicked', {
        lat: latlng.getLat(),
        lng: latlng.getLng(),
        address,
      })
    })
  })
})

// 이벤트 목록 변경 시 마커 갱신
watch(events, (evts) => {
  renderMarkers(evts)
}, { immediate: false })

function renderMarkers(evts) {
  // 기존 마커 제거
  markers.forEach(m => m.setMap(null))
  markers = []

  evts.forEach(ev => {
    const pos = new window.kakao.maps.LatLng(ev.latitude, ev.longitude)
    const marker = new window.kakao.maps.Marker({ position: pos, map })

    const infoContent = `
      <div style="padding:6px 10px;font-size:13px;white-space:nowrap">
        <strong>${ev.title}</strong><br/>
        <span style="color:#888;font-size:11px">${formatDate(ev.start_date)}</span>
      </div>`
    const infowindow = new window.kakao.maps.InfoWindow({ content: infoContent })

    window.kakao.maps.event.addListener(marker, 'mouseover', () => infowindow.open(map, marker))
    window.kakao.maps.event.addListener(marker, 'mouseout', () => infowindow.close())
    window.kakao.maps.event.addListener(marker, 'click', () => emit('markerClick', ev))

    markers.push(marker)
  })
}

// 위치 선택 모드 전환 시 마커 숨김/복원
watch(() => props.isPicking, (picking) => {
  if (picking) {
    markers.forEach(m => m.setMap(null))
  } else {
    markers.forEach(m => m.setMap(map))
    if (tempMarker) { tempMarker.setMap(null); tempMarker = null }
  }
})

// 외부에서 호출할 수 있는 메서드
function panTo(lat, lng) {
  if (map) map.panTo(new window.kakao.maps.LatLng(lat, lng))
}

function clearTempMarker() {
  if (tempMarker) { tempMarker.setMap(null); tempMarker = null }
}

defineExpose({ panTo, clearTempMarker, renderMarkers })
</script>
