<template>
  <div v-if="visible" class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="modal-close" @click="$emit('close')">✕</button>
      <h2>이벤트 등록</h2>
      <form @submit.prevent="handleSubmit">
        <input v-model="form.title" type="text" placeholder="이벤트 제목" required />
        <textarea v-model="form.description" placeholder="설명 (선택)"></textarea>
        <input v-model="form.location_name" type="text" placeholder="장소명" required />

        <label class="form-label">위치 지정</label>
        <div class="location-search-row">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="주소 또는 장소명 검색"
            autocomplete="off"
            @keydown.enter.prevent="searchLocation"
          />
          <button type="button" class="btn-ghost" @click="searchLocation">검색</button>
          <button type="button" class="btn-ghost" @click="$emit('pickLocation', form)">지도</button>
        </div>

        <!-- 검색 결과 -->
        <ul v-if="searchResults.length > 0 || searchStatus" class="search-results">
          <li v-if="searchStatus" :class="searchStatus === '검색 중...' ? 'search-loading' : 'search-empty'">
            {{ searchStatus }}
          </li>
          <li v-for="place in searchResults" :key="place.id" @click="selectPlace(place)">
            <div class="search-place-name">{{ place.place_name }}</div>
            <div class="search-place-addr">{{ place.road_address_name || place.address_name }}</div>
          </li>
        </ul>

        <div class="location-pick-row">
          <span class="picked-address" :class="{ 'has-value': form.latitude }">
            {{ form.latitude ? (form.address || '위치 선택됨') : '위치를 선택해 주세요' }}
          </span>
        </div>

        <div class="date-row">
          <input v-model="form.start_date" type="datetime-local" required />
          <input v-model="form.end_date" type="datetime-local" />
        </div>

        <label class="form-label">이벤트 유형</label>
        <select v-model="form.event_type">
          <option v-for="opt in TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>

        <label class="form-label">춤 종류 (복수 선택)</label>
        <div class="genre-checkboxes">
          <label v-for="opt in GENRE_OPTIONS" :key="opt.value" class="checkbox-label">
            <input v-model="form.dance_genres" type="checkbox" :value="opt.value" />
            {{ opt.label }}
          </label>
        </div>

        <button type="submit" class="btn-primary w100">등록하기</button>
        <p class="form-error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { TYPE_OPTIONS, GENRE_OPTIONS } from '../utils/constants.js'
import { useEvents } from '../composables/useEvents.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
  // 위치 선택 후 복원할 폼 데이터
  restoredForm: { type: Object, default: null },
})
const emit = defineEmits(['close', 'pickLocation', 'created'])
const { createEvent } = useEvents()

const form = reactive({
  title: '',
  description: '',
  location_name: '',
  address: '',
  latitude: '',
  longitude: '',
  start_date: '',
  end_date: '',
  event_type: 'social',
  dance_genres: [],
})

const error = ref('')
const searchQuery = ref('')
const searchResults = ref([])
const searchStatus = ref('')

// 폼 초기화
function resetForm() {
  Object.assign(form, {
    title: '', description: '', location_name: '', address: '',
    latitude: '', longitude: '', start_date: '', end_date: '',
    event_type: 'social', dance_genres: [],
  })
  error.value = ''
  searchQuery.value = ''
  searchResults.value = []
  searchStatus.value = ''
}

// 모달 열릴 때: 복원 데이터가 있으면 적용
watch(() => props.visible, (v) => {
  if (v && props.restoredForm) {
    Object.assign(form, props.restoredForm)
  }
})

// 장소 검색
function searchLocation() {
  const query = searchQuery.value.trim()
  if (!query) return

  searchResults.value = []
  searchStatus.value = '검색 중...'

  const places = new window.kakao.maps.services.Places()
  places.keywordSearch(query, (data, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      searchResults.value = data.slice(0, 5)
      searchStatus.value = ''
    } else if (status === window.kakao.maps.services.Status.ZERO_RESULT) {
      searchStatus.value = '검색 결과가 없습니다'
    } else {
      searchStatus.value = '검색에 실패했습니다'
    }
  })
}

// 검색 결과 선택
function selectPlace(place) {
  form.latitude = parseFloat(place.y).toFixed(6)
  form.longitude = parseFloat(place.x).toFixed(6)
  form.address = place.road_address_name || place.address_name
  if (!form.location_name) {
    form.location_name = place.place_name
  }
  searchResults.value = []
  searchQuery.value = ''
  searchStatus.value = ''

  // 지도 이동은 App에서 처리
  emit('created', { panTo: { lat: place.y, lng: place.x } })
}

// 이벤트 등록
async function handleSubmit() {
  error.value = ''
  if (!form.latitude || !form.longitude) {
    error.value = '지도에서 위치를 선택해 주세요'
    return
  }

  const body = {
    title: form.title,
    description: form.description || null,
    location_name: form.location_name,
    address: form.address || null,
    latitude: parseFloat(form.latitude),
    longitude: parseFloat(form.longitude),
    start_date: new Date(form.start_date).toISOString(),
    end_date: form.end_date ? new Date(form.end_date).toISOString() : null,
    event_type: form.event_type,
    dance_genres: form.dance_genres,
  }

  const result = await createEvent(body)
  if (result.ok) {
    resetForm()
    emit('close')
    emit('created')
  } else {
    error.value = result.error
  }
}

// 외부에서 폼 데이터 가져오기 (위치 선택 시)
function getFormData() {
  return { ...form }
}

// 외부에서 위치 설정
function setLocation(lat, lng, address) {
  form.latitude = parseFloat(lat).toFixed(6)
  form.longitude = parseFloat(lng).toFixed(6)
  if (address) form.address = address
}

defineExpose({ resetForm, getFormData, setLocation })
</script>
