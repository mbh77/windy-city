<template>
  <div v-if="visible" class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="modal-close" @click="$emit('close')">✕</button>
      <h2>{{ editMode ? '이벤트 수정' : '이벤트 등록'}}</h2>
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

        <!-- 가격 정보 (접이식) -->
        <button type="button" class="collapsible-toggle" @click="showPrice = !showPrice">
          가격 정보
          <span class="collapse-arrow" :class="{ open: showPrice }">&#9662;</span>
        </button>
        <div v-show="showPrice" class="collapsible-body">
          <input v-model="form.price" type="text" placeholder="가격 (예: 20,000원)" />
          <input v-model="form.early_bird_price" type="text" placeholder="얼리버드 가격 (선택)" />
        </div>

        <!-- 유형별 추가 필드 (접이식) -->
        <template v-if="form.event_type === 'social'">
          <button type="button" class="collapsible-toggle" @click="showTypeInfo = !showTypeInfo">
            소셜 파티 정보
            <span class="collapse-arrow" :class="{ open: showTypeInfo }">&#9662;</span>
          </button>
          <div v-show="showTypeInfo" class="collapsible-body">
            <input v-model="form.dj_name" type="text" placeholder="DJ 이름 (선택)" />
            <input v-model="form.dress_code" type="text" placeholder="드레스코드 (선택)" />
            <div class="inline-checks">
              <label class="checkbox-label"><input v-model="form.has_pre_lesson" type="checkbox" /> 프리레슨 포함</label>
            </div>
          </div>
        </template>

        <template v-if="form.event_type === 'workshop' || form.event_type === 'regular_class'">
          <button type="button" class="collapsible-toggle" @click="showTypeInfo = !showTypeInfo">
            수업 정보
            <span class="collapse-arrow" :class="{ open: showTypeInfo }">&#9662;</span>
          </button>
          <div v-show="showTypeInfo" class="collapsible-body">
            <input v-model="form.instructor_name" type="text" placeholder="강사명 (선택)" />
            <select v-model="form.difficulty">
              <option value="">난이도 선택</option>
              <option v-for="opt in DIFFICULTY_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
            <input v-model.number="form.max_participants" type="number" placeholder="최대 정원 (선택)" />
            <div class="inline-checks">
              <label class="checkbox-label"><input v-model="form.requires_partner" type="checkbox" /> 파트너 필요</label>
            </div>
          </div>
        </template>

        <!-- 반복 이벤트 -->
        <template v-if="form.event_type === 'regular_class'">
          <div class="inline-checks" style="margin-top:8px">
            <label class="checkbox-label"><input v-model="form.is_recurring" type="checkbox" /> 반복 이벤트 (매주)</label>
          </div>
        </template>

        <!-- 이미지 첨부 (접이식) -->
        <button type="button" class="collapsible-toggle" @click="showImages = !showImages">
          이미지 첨부 ({{ uploadedImages.length }}/5)
          <span class="collapse-arrow" :class="{ open: showImages }">&#9662;</span>
        </button>
        <div v-show="showImages" class="collapsible-body">
          <div class="image-upload-area">
            <div v-for="(img, idx) in uploadedImages" :key="idx" class="image-thumb">
              <img :src="img.url" />
              <button type="button" class="image-remove" @click="removeImage(idx)">✕</button>
            </div>
            <label v-if="uploadedImages.length < 5" class="image-add">
              <input type="file" accept="image/jpeg,image/png,image/webp" @change="handleImageUpload" hidden />
              <span>+</span>
            </label>
          </div>
          <div v-if="uploadError" class="form-error">{{ uploadError }}</div>
        </div>        

        <button type="submit" class="btn-primary w100">
          {{ editMode ? '수정하기' : '등록하기' }}
        </button>
        <p class="form-error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue' // computed 추가
import { TYPE_OPTIONS, GENRE_OPTIONS, DIFFICULTY_OPTIONS } from '../utils/constants.js'
import { useEvents } from '../composables/useEvents.js'
import { apiFetch } from '../utils/api.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
  restoredForm: { type: Object, default: null },
  eventToEdit: { type: Object, default: null },
})
const emit = defineEmits(['close', 'pickLocation', 'created'])
const { createEvent, updateEvent } = useEvents()

const editMode = computed(() => !!props.eventToEdit)

// 접이식 섹션 상태
const showGenres = ref(false)
const showPrice = ref(false)
const showTypeInfo = ref(false)

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
  price: '',
  early_bird_price: '',
  dj_name: '',
  dress_code: '',
  has_pre_lesson: false,
  instructor_name: '',
  difficulty: '',
  max_participants: null,
  requires_partner: false,
  is_recurring: false,
})

const error = ref('')
const searchQuery = ref('')
const searchResults = ref([])
const searchStatus = ref('')

function resetForm() {
  Object.assign(form, {
    title: '', description: '', location_name: '', address: '',
    latitude: '', longitude: '', start_date: '', end_date: '',
    event_type: 'social', dance_genres: [],
    price: '', early_bird_price: '',
    dj_name: '', dress_code: '', has_pre_lesson: false,
    instructor_name: '', difficulty: '', max_participants: null,
    requires_partner: false, is_recurring: false,
  })
  error.value = ''
  searchQuery.value = ''
  searchResults.value = []
  searchStatus.value = ''
  showGenres.value = false
  showPrice.value = false
  showTypeInfo.value = false
  uploadedImages.value = []
  uploadError.value = ''
  showImages.value = false  
}

watch(() => props.visible, (v) => {
  if (v && props.eventToEdit) {
    // 수정 모드: 기존 데이터로 폼 채우기
    const e = props.eventToEdit
    Object.assign(form, {
      title: e.title || '',
      description: e.description || '',
      location_name: e.location_name || '',
      address: e.address || '',
      latitude: e.latitude || '',
      longitude: e.longitude || '',
      start_date: e.start_date ? e.start_date.slice(0, 16) : '',
      end_date: e.end_date ? e.end_date.slice(0, 16) : '',
      event_type: e.event_type || 'social',
      dance_genres: e.dance_genres || [],
      price: e.price || '',
      early_bird_price: e.early_bird_price || '',
      dj_name: e.dj_name || '',
      dress_code: e.dress_code || '',
      has_pre_lesson: e.has_pre_lesson || false,
      instructor_name: e.instructor_name || '',
      difficulty: e.difficulty || '',
      max_participants: e.max_participants || null,
      requires_partner: e.requires_partner || false,
      is_recurring: e.is_recurring || false,
    })
    // 기존 이미지 로드
    uploadedImages.value = (e.media || [])
      .filter(m => m.media_type === 'image')
      .map(m => ({ id: m.id, url: m.url }))
  } else if (v && props.restoredForm) {
    Object.assign(form, props.restoredForm)
  }
})

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
  if (!form.location_name) {
    form.location_name = place.place_name
  }
  searchResults.value = []
  searchQuery.value = ''
  searchStatus.value = ''

  emit('created', { panTo: { lat: place.y, lng: place.x } })
}

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
    price: form.price || null,
    early_bird_price: form.early_bird_price || null,
    dj_name: form.dj_name || null,
    dress_code: form.dress_code || null,
    has_pre_lesson: form.has_pre_lesson,
    instructor_name: form.instructor_name || null,
    difficulty: form.difficulty || null,
    max_participants: form.max_participants || null,
    requires_partner: form.requires_partner,
    is_recurring: form.is_recurring,
  }

  const eventId = editMode.value ? props.eventToEdit.id : null
  const result = editMode.value ? await updateEvent(eventId, body) : await createEvent(body)
  if (result.ok) {
    const savedId = eventId || result.eventId

    // 수정 모드: 삭제된 기존 이미지 제거
    if (editMode.value && props.eventToEdit.media) {
      const currentIds = uploadedImages.value.filter(img => img.id).map(img => img.id)
      for (const m of props.eventToEdit.media) {
        if (!currentIds.includes(m.id)) {
          await apiFetch(`/api/events/${savedId}/media/${m.id}`, { method: 'DELETE' })
        }
      }
    }

    // 새로 추가된 이미지 등록 (id가 없는 것만)
    const newImages = uploadedImages.value.filter(img => !img.id)
    for (let i = 0; i < newImages.length; i++) {
      await apiFetch(`/api/events/${savedId}/media`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          media_type: 'image',
          url: newImages[i].url,
          sort_order: i,
        }),
      })
    }

    resetForm()
    emit('close')
    emit('created')
  } else {
    error.value = result.error
  }
}

function getFormData() {
  return { ...form }
}

function setLocation(lat, lng, address) {
  form.latitude = parseFloat(lat).toFixed(6)
  form.longitude = parseFloat(lng).toFixed(6)
  if (address) form.address = address
}

const showImages = ref(false)
const uploadedImages = ref([])
const uploadError = ref('')

async function handleImageUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  uploadError.value = ''

  const formData = new FormData()
  formData.append('file', file)

  const res = await apiFetch('/api/upload/image', {
    method: 'POST',
    body: formData,
  })

  if (res.ok) {
    const data = await res.json()
    uploadedImages.value.push({ url: data.url })
  } else {
    const err = await res.json()
    uploadError.value = err.detail || '업로드에 실패했습니다'
  }
  e.target.value = ''
}

function removeImage(idx) {
  uploadedImages.value.splice(idx, 1)
}

defineExpose({ resetForm, getFormData, setLocation })
</script>
