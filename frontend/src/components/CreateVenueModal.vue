<template>
  <div v-if="visible" class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="modal-close" @click="$emit('close')">✕</button>
      <h2>장소 등록</h2>
      <form @submit.prevent="handleSubmit">
        <!-- 장소 유형 -->
        <label class="form-label">장소 유형</label>
        <select v-model="form.venue_type" required>
          <option v-for="opt in VENUE_TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>

        <input v-model="form.name" type="text" placeholder="장소명" required />
        <textarea v-model="form.description" placeholder="상세 설명 (선택)"></textarea>

        <!-- 위치 검색 -->
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

        <!-- 연락처 -->
        <input v-model="form.phone" type="text" placeholder="전화번호 (선택)" />
        <input v-model="form.website" type="text" placeholder="홈페이지 URL (선택)" />

        <!-- 춤 종류 (접이식) -->
        <button type="button" class="collapsible-toggle" @click="showGenres = !showGenres">
          춤 종류 (복수 선택)
          <span class="collapse-arrow" :class="{ open: showGenres }">&#9662;</span>
        </button>
        <div v-show="showGenres" class="collapsible-body">
          <div class="genre-checkboxes">
            <label v-for="opt in GENRE_OPTIONS" :key="opt.value" class="checkbox-label">
              <input v-model="form.dance_genres" type="checkbox" :value="opt.value" />
              {{ opt.label }}
            </label>
          </div>
        </div>

        <!-- 유형별 추가 필드 (접이식) -->
        <template v-if="form.venue_type === 'club'">
          <button type="button" class="collapsible-toggle" @click="showTypeInfo = !showTypeInfo">
            클럽 정보
            <span class="collapse-arrow" :class="{ open: showTypeInfo }">&#9662;</span>
          </button>
          <div v-show="showTypeInfo" class="collapsible-body">
            <input v-model="form.cover_charge" type="text" placeholder="입장료 (예: 20,000원)" />
            <div class="inline-checks">
              <label class="checkbox-label"><input v-model="form.has_bar" type="checkbox" /> 바/주류 판매</label>
            </div>
          </div>
        </template>

        <template v-if="form.venue_type === 'academy'">
          <button type="button" class="collapsible-toggle" @click="showTypeInfo = !showTypeInfo">
            학원 정보
            <span class="collapse-arrow" :class="{ open: showTypeInfo }">&#9662;</span>
          </button>
          <div v-show="showTypeInfo" class="collapsible-body">
            <div class="inline-checks">
              <label class="checkbox-label"><input v-model="form.has_trial_class" type="checkbox" /> 체험 수업 가능</label>
            </div>
            <input v-if="form.has_trial_class" v-model="form.trial_class_fee" type="text" placeholder="체험 수업비 (예: 10,000원)" />
          </div>
        </template>

        <template v-if="form.venue_type === 'practice_room'">
          <button type="button" class="collapsible-toggle" @click="showTypeInfo = !showTypeInfo">
            연습실 정보
            <span class="collapse-arrow" :class="{ open: showTypeInfo }">&#9662;</span>
          </button>
          <div v-show="showTypeInfo" class="collapsible-body">
            <input v-model="form.rental_fee" type="text" placeholder="대관료 (예: 시간당 20,000원)" />
            <input v-model.number="form.area_sqm" type="number" placeholder="면적 (㎡)" />
            <div class="inline-checks">
              <label class="checkbox-label"><input v-model="form.has_mirror" type="checkbox" /> 거울</label>
              <label class="checkbox-label"><input v-model="form.has_sound_system" type="checkbox" /> 음향 시설</label>
            </div>
          </div>
        </template>

        <!-- 공통 시설 (접이식) -->
        <button type="button" class="collapsible-toggle" @click="showFacility = !showFacility">
          시설 정보
          <span class="collapse-arrow" :class="{ open: showFacility }">&#9662;</span>
        </button>
        <div v-show="showFacility" class="collapsible-body">
          <input v-model="form.floor_type" type="text" placeholder="플로어 타입 (예: 우드)" />
          <input v-model.number="form.capacity" type="number" placeholder="수용 인원" />
          <div class="inline-checks">
            <label class="checkbox-label"><input v-model="form.has_parking" type="checkbox" /> 주차 가능</label>
          </div>
          <input v-if="form.has_parking" v-model="form.parking_info" type="text" placeholder="주차 정보 (예: 건물 지하 주차장)" />
        </div>

        <button type="submit" class="btn-primary w100">등록하기</button>
        <p class="form-error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { VENUE_TYPE_OPTIONS, GENRE_OPTIONS } from '../utils/constants.js'
import { useVenues } from '../composables/useVenues.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
  restoredForm: { type: Object, default: null },
})
const emit = defineEmits(['close', 'pickLocation', 'created'])
const { createVenue } = useVenues()

// 접이식 섹션 상태
const showGenres = ref(false)
const showTypeInfo = ref(false)
const showFacility = ref(false)

const form = reactive({
  venue_type: 'club',
  name: '',
  description: '',
  address: '',
  latitude: '',
  longitude: '',
  phone: '',
  website: '',
  dance_genres: [],
  // 클럽
  cover_charge: '',
  has_bar: false,
  // 학원
  has_trial_class: false,
  trial_class_fee: '',
  // 연습실
  rental_fee: '',
  area_sqm: null,
  has_mirror: false,
  has_sound_system: false,
  // 공통 시설
  floor_type: '',
  capacity: null,
  has_parking: false,
  parking_info: '',
})

const error = ref('')
const searchQuery = ref('')
const searchResults = ref([])
const searchStatus = ref('')

function resetForm() {
  Object.assign(form, {
    venue_type: 'club', name: '', description: '', address: '',
    latitude: '', longitude: '', phone: '', website: '',
    dance_genres: [], cover_charge: '', has_bar: false,
    has_trial_class: false, trial_class_fee: '',
    rental_fee: '', area_sqm: null, has_mirror: false, has_sound_system: false,
    floor_type: '', capacity: null, has_parking: false, parking_info: '',
  })
  error.value = ''
  searchQuery.value = ''
  searchResults.value = []
  searchStatus.value = ''
  showGenres.value = false
  showTypeInfo.value = false
  showFacility.value = false
}

// 모달 열릴 때: 복원 데이터 적용
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

function selectPlace(place) {
  form.latitude = parseFloat(place.y).toFixed(6)
  form.longitude = parseFloat(place.x).toFixed(6)
  form.address = place.road_address_name || place.address_name
  if (!form.name) {
    form.name = place.place_name
  }
  searchResults.value = []
  searchQuery.value = ''
  searchStatus.value = ''

  emit('created', { panTo: { lat: place.y, lng: place.x } })
}

async function handleSubmit() {
  error.value = ''
  if (!form.latitude || !form.longitude) {
    error.value = '위치를 선택해 주세요'
    return
  }

  const body = {
    venue_type: form.venue_type,
    name: form.name,
    description: form.description || null,
    address: form.address || null,
    latitude: parseFloat(form.latitude),
    longitude: parseFloat(form.longitude),
    phone: form.phone || null,
    website: form.website || null,
    dance_genres: form.dance_genres,
    floor_type: form.floor_type || null,
    capacity: form.capacity || null,
    has_parking: form.has_parking,
    parking_info: form.has_parking ? (form.parking_info || null) : null,
    cover_charge: form.cover_charge || null,
    has_bar: form.has_bar,
    rental_fee: form.rental_fee || null,
    area_sqm: form.area_sqm || null,
    has_mirror: form.has_mirror,
    has_sound_system: form.has_sound_system,
    has_trial_class: form.has_trial_class,
    trial_class_fee: form.has_trial_class ? (form.trial_class_fee || null) : null,
  }

  const result = await createVenue(body)
  if (result.ok) {
    resetForm()
    emit('close')
    emit('created')
  } else {
    error.value = result.error
  }
}

defineExpose({ resetForm })
</script>
