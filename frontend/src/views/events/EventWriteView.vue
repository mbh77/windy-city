<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn">지도</router-link>
      <a class="page-nav-btn" @click="$router.back()">뒤로</a>
      <h1 class="page-title">{{ editMode ? '이벤트 수정' : '이벤트 등록' }}</h1>
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
          <input v-model="form.title" placeholder="이벤트 제목 *" class="write-title" required />

          <input v-model="form.location_name" type="text" placeholder="장소명 *" required />

          <!-- 위치 검색 -->
          <label class="form-label">위치 지정 *</label>
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
          <div class="location-pick-row">
            <span class="picked-address" :class="{ 'has-value': form.latitude }">
              {{ form.latitude ? (form.address || '위치 선택됨') : '지도를 클릭하거나 검색으로 위치를 선택하세요' }}
            </span>
          </div>
          <input v-model="form.address_detail" type="text" placeholder="상세 주소 (층수, 호수 등)" />

          <!-- 날짜 (필수) -->
          <label class="form-label">이벤트 날짜 *</label>
          <div class="date-row">
            <input v-model="form.event_date" type="date" required />
            <input v-model="form.event_end_date" type="date" placeholder="종료일 (선택)" />
          </div>

          <!-- 시간 (옵션) -->
          <label class="form-label">시간 (선택)</label>
          <div class="date-row">
            <input v-model="form.start_time" type="time" />
            <input v-model="form.end_time" type="time" />
          </div>

          <!-- 이벤트 유형 -->
          <label class="form-label">이벤트 유형 *</label>
          <select v-model="form.event_type">
            <option v-for="opt in TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>

          <div class="step-actions">
            <button type="button" class="btn-primary w100" @click="goStep2">
              다음: 상세 정보 →
            </button>
            <button type="submit" class="btn-ghost w100" style="margin-top:8px;">
              상세 정보 건너뛰고 바로 {{ editMode ? '수정' : '등록' }}
            </button>
          </div>
        </div>

        <!-- ========== 2단계: 상세 정보 ========== -->
        <div v-show="step === 2">

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
                    placeholder="이벤트 설명 (마크다운 지원)" rows="8"></textarea>
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

          <!-- 유형별 추가 필드 -->
          <!-- 기존 CreateEventModal.vue 82~112행의 소셜/워크샵 블록 그대로 가져오기 -->
          <!-- 단, collapsible-toggle 제거하고 바로 노출 -->

          <!-- 반복 이벤트 -->
          <!-- 기존 CreateEventModal.vue 114~161행 그대로 가져오기 -->
          <!-- 단, collapsible-toggle 제거하고 바로 노출 -->

          <!-- 이미지 첨부 -->
          <label class="form-label">이미지 첨부 ({{ uploadedImages.length }}/5)</label>
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

          <div class="step-actions">
            <button type="button" class="btn-ghost" @click="step = 1">← 이전</button>
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
  form.latitude = parseFloat(place.y).toFixed(6)
  form.longitude = parseFloat(place.x).toFixed(6)
  form.address = place.road_address_name || place.address_name
  if (!form.location_name) form.location_name = place.place_name
  clearSearch()
  moveMinimap(place.y, place.x)
}

// ===== 스텝 이동 =====
function goStep2() {
  if (!form.title.trim()) { error.value = '제목을 입력해 주세요'; return }
  if (!form.location_name.trim()) { error.value = '장소명을 입력해 주세요'; return }
  if (!form.latitude) { error.value = '위치를 선택해 주세요'; return }
  if (!form.event_date) { error.value = '이벤트 날짜를 선택해 주세요'; return }
  error.value = ''
  step.value = 2
}

// ===== 제출 =====
async function handleSubmit() {
  error.value = ''
  if (!form.latitude || !form.longitude) { error.value = '위치를 선택해 주세요'; return }
  if (!form.event_date) { error.value = '이벤트 날짜를 선택해 주세요'; return }

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
/* 미니맵 */
.minimap {
  width: 100%;
  height: 250px;
  border-radius: 8px;
  border: 1px solid #E0D5C8;
  margin: 8px 0;
}

/* 스텝 인디케이터 */
.step-indicator {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 0.9rem;
  color: #8B7B6B;
}
.step-indicator .active {
  color: #5BA89E;
  font-weight: 700;
}
.step-actions {
  margin-top: 16px;
}

.write-title { width: 100%; background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 10px; font-size: 1rem; margin-bottom: 8px; }

/* 작성/미리보기 탭 */
.write-tabs { display: flex; gap: 4px; margin-bottom: 8px; }
.write-tabs button { padding: 4px 12px; border: 1px solid #E0D5C8; background: transparent; color: #8B7B6B; border-radius: 6px 6px 0 0; font-size: 0.8rem; cursor: pointer; }
.write-tabs button.active { background: #FFFFFF; color: #3D3029; border-bottom-color: #FFFFFF; }

/* 마크다운 툴바 */
.write-toolbar { display: flex; gap: 4px; margin-bottom: 4px; }
.write-toolbar button { padding: 4px 10px; background: #FFFFFF; border: 1px solid #E0D5C8; color: #5A4A3A; border-radius: 4px; font-size: 0.8rem; cursor: pointer; }
.write-toolbar button:hover { background: #EDE5DB; color: #3D3029; }

/* 미리보기 */
.write-preview { background: #FFFFFF; border: 1px solid #E0D5C8; border-radius: 0 6px 6px 6px; padding: 10px; font-size: 0.9rem; min-height: 150px; line-height: 1.6; }

/* 마크다운 렌더링 */
.markdown-body :deep(h1) { font-size: 1.3rem; margin: 16px 0 8px; }
.markdown-body :deep(h2) { font-size: 1.15rem; margin: 14px 0 6px; }
.markdown-body :deep(h3) { font-size: 1.05rem; margin: 12px 0 4px; }
.markdown-body :deep(p) { margin: 0 0 8px; }
.markdown-body :deep(a) { color: #5BA89E; text-decoration: underline; }
.markdown-body :deep(code) { background: #F0E8DE; padding: 1px 5px; border-radius: 3px; font-size: 0.85em; }
.markdown-body :deep(pre) { background: #F0E8DE; padding: 12px; border-radius: 6px; overflow-x: auto; margin: 8px 0; }
.markdown-body :deep(pre code) { background: none; padding: 0; }
.markdown-body :deep(blockquote) { border-left: 3px solid #E0D5C8; padding-left: 12px; color: #8B7B6B; margin: 8px 0; }
.markdown-body :deep(ul), .markdown-body :deep(ol) { padding-left: 20px; margin: 8px 0; }
.markdown-body :deep(img) { max-width: 100%; border-radius: 6px; }
.markdown-body :deep(hr) { border: none; border-top: 1px solid #EDE5DB; margin: 16px 0; }

/* 미디어 임베드 */
.markdown-body :deep(.embed-video) { position: relative; width: 100%; padding-bottom: 56.25%; margin: 12px 0; }
.markdown-body :deep(.embed-video iframe) { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 8px; }

/* 영상 URL 다이얼로그 */
.dialog-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog-box { background: #FFFFFF; border: 1px solid #E0D5C8; border-radius: 10px; padding: 20px; width: 90%; max-width: 400px; }
.dialog-box h4 { margin: 0 0 8px; font-size: 1rem; }
.dialog-hint { font-size: 0.75rem; color: #8B7B6B; margin-bottom: 12px; }
.dialog-box input { width: 100%; background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 8px; font-size: 0.85rem; margin-bottom: 12px; box-sizing: border-box; }
.dialog-actions { display: flex; gap: 8px; justify-content: flex-end; }
</style>