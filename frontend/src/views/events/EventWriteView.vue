<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn">지도</router-link>
      <a class="page-nav-btn" @click="$router.back()">뒤로</a>
      <h1 class="page-title">{{ editMode ? '강습·행사 수정' : '강습·행사 등록' }}</h1>
    </header>

    <main class="page-body">
      <!-- 스텝 인디케이터 -->
      <div class="step-indicator">
        <span :class="{ active: step === 1 }">1. 기본 정보</span>
        <span :class="{ active: step === 2 }">2. 상세 정보</span>
      </div>

      <form @submit.prevent="handleSubmit">

        <!-- ========== 1단계: 필수 정보 ========== -->
        <div v-show="step === 1">
          <input v-model="form.title" placeholder="강습·행사 제목 (필수)" class="write-title" required />

          <!-- 이미지 첨부 -->
          <label class="form-label">이미지 첨부 ({{ uploadedImages.length }}/5) (선택)</label>
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
          <div class="upload-hint">JPG/WEBP 3MB 이하 · PNG는 자동 변환 (10MB 이하)</div>

          <input v-model="form.location_name" type="text" placeholder="장소명 (선택)" required />

          <!-- 위치 검색 -->
          <label class="form-label">위치 지정 (필수) : 검색하거나 지도에서 선택</label>
          <div class="location-search-row">
            <input v-model="searchQuery" type="text" placeholder="주소 또는 장소명 검색"
                   autocomplete="off" @keydown.enter.prevent="searchLocation" />
            <button type="button" class="btn-ghost" @click="searchLocation">검색</button>
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

          <!-- 미니맵 -->
          <div ref="minimapContainer" class="minimap"></div>
          <div class="address-row">
            <div class="location-pick-row">
              <span class="picked-address" :class="{ 'has-value': form.latitude }">
                {{ form.latitude ? (form.address || '위치 선택됨') : '지도를 클릭하거나 검색으로 위치를 선택하세요' }}
              </span>
            </div>
            <input v-model="form.address_detail" type="text" placeholder="상세 주소 (층수, 호수 등)" />
          </div>

          <!-- 날짜 (필수) -->
          <label class="form-label">강습·행사 날짜 (필수)</label>
          <input v-model="form.event_date" type="date" required />

          <!-- 이벤트 유형 -->
          <label class="form-label">강습·행사 유형 (필수)</label>
          <select v-model="form.event_type">
            <option v-for="opt in TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>

          <div class="step-actions">
            <button type="button" class="btn-primary w100" @click="goStep2">
              다음: 상세 정보 →
            </button>
            <button type="submit" class="btn-ghost w100">
              상세 정보 건너뛰고 바로 {{ editMode ? '수정' : '등록' }}
            </button>
          </div>
        </div>

        <!-- ========== 2단계: 상세 정보 ========== -->
        <div v-show="step === 2">

          <!-- 종료일 (선택) -->
          <label class="form-label">종료일 (선택)</label>
          <input v-model="form.event_end_date" type="date" />

          <!-- 시간 (선택) -->
          <label class="form-label">시간 (선택)</label>
          <div class="date-row">
            <input v-model="form.start_time" type="time" />
            <input v-model="form.end_time" type="time" />
          </div>

          <!-- 설명 (마크다운 + 툴바) -->
          <label class="form-label">설명</label>
          <div class="write-tabs">
            <button type="button" :class="{ active: !descPreview }" @click="descPreview = false">작성</button>
            <button type="button" :class="{ active: descPreview }" @click="descPreview = true">미리보기</button>
          </div>
          <div class="write-toolbar" v-if="!descPreview">
            <button type="button" @click="insertBold" title="굵게">B</button>
            <button type="button" @click="insertItalic" title="기울임"><em>I</em></button>
            <button type="button" @click="insertLink" title="링크">🔗</button>
            <button type="button" @click="triggerDescImage" title="이미지">📷</button>
            <button type="button" @click="showVideoDialog = true" title="영상">▶️</button>
            <input type="file" ref="descImageInput" accept="image/*" style="display:none" @change="uploadDescImage" />
          </div>
          <textarea v-if="!descPreview" ref="descArea" v-model="form.description"
                    placeholder="강습·행사 설명 (마크다운 지원)" rows="8"></textarea>
          <div v-else class="write-preview markdown-body" v-html="renderMarkdown(form.description)"></div>

          <!-- 영상 URL 다이얼로그 (PostWriteView 참고) -->
          <div class="dialog-overlay" v-if="showVideoDialog" @click.self="showVideoDialog = false">
            <div class="dialog-box">
              <h4>영상 URL 입력</h4>
              <p class="dialog-hint">YouTube 또는 Instagram 영상 URL을 입력하세요</p>
              <input v-model="videoUrl" type="text" placeholder="https://youtube.com/watch?v=..." />
              <div class="dialog-actions">
                <button type="button" class="btn-ghost" @click="showVideoDialog = false">취소</button>
                <button type="button" class="btn-primary" @click="insertVideo">삽입</button>
              </div>
            </div>
          </div>

          <!-- 춤 종류 -->
          <label class="form-label">춤 종류 (복수 선택)</label>
          <div class="genre-checkboxes">
            <label v-for="opt in GENRE_OPTIONS" :key="opt.value" class="checkbox-label">
              <input v-model="form.dance_genres" type="checkbox" :value="opt.value" />
              {{ opt.label }}
            </label>
          </div>

          <!-- 가격 -->
          <label class="form-label">가격 정보</label>
          <input v-model="form.price" type="text" placeholder="가격 (예: 20,000원)" />
          <input v-model="form.early_bird_price" type="text" placeholder="얼리버드 가격 (선택)" />

          <!-- 유형별 추가 필드: 소셜 파티 -->
          <template v-if="form.event_type === 'social'">
            <label class="form-label">소셜 파티 정보</label>
            <input v-model="form.dj_name" type="text" placeholder="DJ 이름 (선택)" />
            <input v-model="form.dress_code" type="text" placeholder="드레스코드 (선택)" />
            <div class="inline-checks">
              <label class="checkbox-label"><input v-model="form.has_pre_lesson" type="checkbox" /> 프리레슨 포함</label>
            </div>
          </template>

          <!-- 유형별 추가 필드: 워크샵/강습 -->
          <template v-if="form.event_type === 'workshop' || form.event_type === 'regular_class'">
            <label class="form-label">수업 정보</label>
            <input v-model="form.instructor_name" type="text" placeholder="강사명 (선택)" />
            <select v-model="form.difficulty">
              <option value="">난이도 선택</option>
              <option v-for="opt in DIFFICULTY_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
            <input v-model.number="form.max_participants" type="number" placeholder="최대 정원 (선택)" />
          </template>

          <!-- 반복 설정 -->
          <label class="form-label">반복 설정</label>
          <div class="inline-checks">
            <label class="checkbox-label"><input v-model="form.is_recurring" type="checkbox" /> 반복 강습·행사</label>
          </div>
          <template v-if="form.is_recurring">
            <label class="form-label">주기</label>
            <select v-model="form.recurrence_frequency">
              <option value="weekly">매주</option>
              <option value="biweekly">격주</option>
            </select>
            <label class="form-label">반복 요일</label>
            <div class="genre-checkboxes">
              <label v-for="day in DAY_OPTIONS" :key="day.value" class="checkbox-label">
                <input v-model="form.recurrence_days" type="checkbox" :value="day.value" />
                {{ day.label }}
              </label>
            </div>
            <label class="form-label">휴강일</label>
            <div class="skip-date-row">
              <input v-model="newSkipDate" type="date" />
              <button type="button" class="btn-ghost" @click="addSkipDate">추가</button>
            </div>
            <div v-if="form.skip_dates.length > 0" class="date-tag-list">
              <span v-for="(d, idx) in form.skip_dates" :key="idx" class="date-tag">
                {{ d }} <button type="button" @click="form.skip_dates.splice(idx, 1)">✕</button>
              </span>
            </div>
            <label class="form-label">보강일</label>
            <div class="skip-date-row">
              <input v-model="newExtraDate" type="date" />
              <button type="button" class="btn-ghost" @click="addExtraDate">추가</button>
            </div>
            <div v-if="form.extra_dates.length > 0" class="date-tag-list">
              <span v-for="(d, idx) in form.extra_dates" :key="idx" class="date-tag">
                {{ d }} <button type="button" @click="form.extra_dates.splice(idx, 1)">✕</button>
              </span>
            </div>
          </template>

          <div class="step-actions">
            <button type="button" class="btn-ghost w100" @click="step = 1">← 이전</button>
            <button type="submit" class="btn-primary w100">
              {{ editMode ? '수정하기' : '등록하기' }}
            </button>
          </div>
        </div>

        <p class="form-error">{{ error }}</p>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '@/utils/api.js'
import { TYPE_OPTIONS, GENRE_OPTIONS, DIFFICULTY_OPTIONS } from '@/utils/constants.js'
import { useAuth } from '@/composables/useAuth.js'
import { useEvents } from '@/composables/useEvents.js'
import { useImageUpload } from '@/composables/useImageUpload.js'
import { useLocationSearch } from '@/composables/useLocationSearch.js'
import { useMarkdownEditor } from '@/composables/useMarkdownEditor.js'
import { renderMarkdown } from '@/utils/markdown.js'

const route = useRoute()
const router = useRouter()
const { currentUser } = useAuth()
const { createEvent, updateEvent } = useEvents()

// ===== 공통 composables =====
const { uploadedImages, uploadError, handleImageUpload, removeImage, setExistingMedia, saveMedia } = useImageUpload()
const { searchQuery, searchResults, searchStatus, searchLocation, clearSearch } = useLocationSearch()
const {
  descPreview, descArea, descImageInput, showVideoDialog, videoUrl,
  insertBold, insertItalic, insertLink, triggerDescImage, uploadDescImage, insertVideo,
} = useMarkdownEditor(
  () => form.description,
  (v) => { form.description = v },
)

// ===== 수정 모드 판별 =====
const editId = computed(() => route.params.id || null)
const editMode = computed(() => !!editId.value)

// ===== 2단계 스텝 =====
const step = ref(1)

// ===== form 데이터 =====
const form = reactive({
  title: '',
  description: '',
  location_name: '',
  address: '',
  address_detail: '',
  latitude: '',
  longitude: '',
  event_date: '',
  event_end_date: '',
  start_time: '',
  end_time: '',
  event_type: 'regular_class',
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
  recurrence_frequency: 'weekly',
  recurrence_days: [],
  skip_dates: [],
  extra_dates: [],
})

const error = ref('')

const DAY_OPTIONS = [
  { value: 'mon', label: '월' },
  { value: 'tue', label: '화' },
  { value: 'wed', label: '수' },
  { value: 'thu', label: '목' },
  { value: 'fri', label: '금' },
  { value: 'sat', label: '토' },
  { value: 'sun', label: '일' },
]

const newSkipDate = ref('')
const newExtraDate = ref('')

function addSkipDate() {
  if (newSkipDate.value && !form.skip_dates.includes(newSkipDate.value)) {
    form.skip_dates.push(newSkipDate.value)
    form.skip_dates.sort()
    newSkipDate.value = ''
  }
}

function addExtraDate() {
  if (newExtraDate.value && !form.extra_dates.includes(newExtraDate.value)) {
    form.extra_dates.push(newExtraDate.value)
    form.extra_dates.sort()
    newExtraDate.value = ''
  }
}

// ===== 미니맵 =====
const minimapContainer = ref(null)
let minimap = null
let minimapMarker = null

function initMinimap() {
  if (!minimapContainer.value || !window.kakao?.maps) return
  const lat = parseFloat(form.latitude) || 37.5665
  const lng = parseFloat(form.longitude) || 126.978
  const level = form.latitude ? 3 : 5
  const position = new window.kakao.maps.LatLng(lat, lng)
  minimap = new window.kakao.maps.Map(minimapContainer.value, { center: position, level })

  if (form.latitude) {
    minimapMarker = new window.kakao.maps.Marker({ position, map: minimap })
  }

  window.kakao.maps.event.addListener(minimap, 'click', (mouseEvent) => {
    const latlng = mouseEvent.latLng
    form.latitude = latlng.getLat().toFixed(6)
    form.longitude = latlng.getLng().toFixed(6)
    if (minimapMarker) {
      minimapMarker.setPosition(latlng)
    } else {
      minimapMarker = new window.kakao.maps.Marker({ position: latlng, map: minimap })
    }
    const geocoder = new window.kakao.maps.services.Geocoder()
    geocoder.coord2Address(latlng.getLng(), latlng.getLat(), (result, status) => {
      if (status === window.kakao.maps.services.Status.OK && result[0]) {
        form.address = result[0].road_address?.address_name || result[0].address?.address_name || ''
      }
    })
  })
}

function moveMinimap(lat, lng) {
  if (!minimap) return
  const pos = new window.kakao.maps.LatLng(lat, lng)
  minimap.setCenter(pos)
  minimap.setLevel(3)
  if (minimapMarker) {
    minimapMarker.setPosition(pos)
  } else {
    minimapMarker = new window.kakao.maps.Marker({ position: pos, map: minimap })
  }
}

// ===== 장소 선택 (검색 결과 클릭) =====
function selectPlace(place) {
  form.address = place.road_address_name || place.address_name
  if (!form.location_name) form.location_name = place.place_name
  clearSearch()

  // 주소 기반 좌표 보정 (Geocoder가 keywordSearch보다 정확)
  const geocoder = new window.kakao.maps.services.Geocoder()
  geocoder.addressSearch(form.address, (result, status) => {
    if (status === window.kakao.maps.services.Status.OK && result.length > 0) {
      form.latitude = parseFloat(result[0].y).toFixed(6)
      form.longitude = parseFloat(result[0].x).toFixed(6)
      moveMinimap(result[0].y, result[0].x)
    } else {
      // Geocoder 실패 시 키워드 검색 좌표 사용
      form.latitude = parseFloat(place.y).toFixed(6)
      form.longitude = parseFloat(place.x).toFixed(6)
      moveMinimap(place.y, place.x)
    }
  })
}

// ===== 스텝 이동 =====
function goStep2() {
  if (!form.title.trim()) { error.value = '제목을 입력해 주세요'; return }
  if (!form.location_name.trim()) { error.value = '장소명을 입력해 주세요'; return }
  if (!form.latitude) { error.value = '위치를 선택해 주세요'; return }
  if (!form.event_date) { error.value = '강습·행사 날짜를 선택해 주세요'; return }
  error.value = ''
  step.value = 2
}

// ===== 제출 =====
async function handleSubmit() {
  error.value = ''
  if (!form.latitude || !form.longitude) { error.value = '위치를 선택해 주세요'; return }
  if (!form.event_date) { error.value = '강습·행사 날짜를 선택해 주세요'; return }

  const body = {
    title: form.title,
    description: form.description || null,
    location_name: form.location_name,
    address: form.address || null,
    address_detail: form.address_detail || null,
    latitude: parseFloat(form.latitude),
    longitude: parseFloat(form.longitude),
    event_date: form.event_date,
    event_end_date: form.event_end_date || null,
    start_time: form.start_time || null,
    end_time: form.end_time || null,
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
    recurrence_rule: form.is_recurring ? {
      frequency: form.recurrence_frequency,
      days: form.recurrence_days,
      skip_dates: form.skip_dates,
      extra_dates: form.extra_dates,
    } : null,
  }

  let savedId
  if (editMode.value) {
    const result = await updateEvent(editId.value, body)
    if (!result.ok) { error.value = result.error; return }
    savedId = editId.value
  } else {
    const result = await createEvent(body)
    if (!result.ok) { error.value = result.error; return }
    savedId = result.eventId
  }

  await saveMedia('events', savedId)
  router.push(`/events/${savedId}`)
}

// ===== 수정 모드: 기존 데이터 로드 =====
async function loadEvent() {
  const res = await apiFetch(`/api/events/${editId.value}`)
  if (!res.ok) { router.push('/'); return }
  const e = await res.json()
  Object.assign(form, {
    title: e.title || '',
    description: e.description || '',
    location_name: e.location_name || '',
    address: e.address || '',
    address_detail: e.address_detail || '',
    latitude: e.latitude || '',
    longitude: e.longitude || '',
    event_date: e.event_date || '',
    event_end_date: e.event_end_date || '',
    start_time: e.start_time || '',
    end_time: e.end_time || '',
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
    recurrence_frequency: e.recurrence_rule?.frequency || 'weekly',
    recurrence_days: e.recurrence_rule?.days || [],
    skip_dates: e.recurrence_rule?.skip_dates || [],
    extra_dates: e.recurrence_rule?.extra_dates || [],
  })
  setExistingMedia(e.media)
}

// ===== URL 쿼리에서 위치 로드 =====
function loadFromQuery() {
  const q = route.query
  if (q.lat && q.lng) {
    form.latitude = q.lat
    form.longitude = q.lng
    if (q.address) form.address = q.address
  }
}

// ===== onMounted =====
onMounted(() => {
  if (!currentUser.value) { router.push('/'); return }
  loadFromQuery()
  if (editMode.value) {
    loadEvent().then(() => window.kakao.maps.load(initMinimap))
  } else {
    window.kakao.maps.load(initMinimap)
  }
})
</script>

<style scoped>
.minimap { width: 100%; height: 250px; border-radius: 8px; border: 1px solid #E0D5C8; margin: 8px 0; }
.step-indicator { display: flex; gap: 16px; margin-bottom: 16px; font-size: 0.9rem; color: #8B7B6B; }
.step-indicator .active { color: #5BA89E; font-weight: 700; }
.step-actions { display: flex; gap: 8px; margin-top: 16px; }
.step-actions button { flex: 1; }
@media (max-width: 768px) {
  .step-actions { flex-direction: column; }
}
</style>