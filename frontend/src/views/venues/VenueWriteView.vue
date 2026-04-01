<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn">지도</router-link>
      <a class="page-nav-btn" @click="$router.back()">뒤로</a>
      <h1 class="page-title">{{ editMode ? '장소 수정' : '장소 등록' }}</h1>
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
          <input v-model="form.name" placeholder="장소명 (필수)" class="write-title" required />

          <!-- 이미지 첨부 -->
          <label class="form-label">이미지 첨부 ({{ uploadedImages.length }}/10) (선택)</label>
          <div class="image-upload-area">
            <div v-for="(img, idx) in uploadedImages" :key="idx" class="image-thumb">
              <img :src="img.url" />
              <button type="button" class="image-remove" @click="removeImage(idx)">✕</button>
            </div>
            <label v-if="uploadedImages.length < 10" class="image-add">
              <input type="file" accept="image/jpeg,image/png,image/webp" @change="handleImageUpload" hidden />
              <span>+</span>
            </label>
          </div>
          <div v-if="uploadError" class="form-error">{{ uploadError }}</div>
          <div class="upload-hint">JPG/WEBP 3MB 이하 · PNG는 자동 변환 (10MB 이하)</div>

          <!-- 장소 유형 -->
          <label class="form-label">장소 유형 (필수)</label>
          <select v-model="form.venue_type" required>
            <option v-for="opt in VENUE_TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>

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
                    placeholder="장소 설명 (마크다운 지원)" rows="8"></textarea>
          <div v-else class="write-preview markdown-body" v-html="renderMarkdown(form.description)"></div>

          <!-- 영상 URL 다이얼로그 -->
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

          <!-- 연락처 -->
          <label class="form-label">연락처</label>
          <input v-model="form.phone" type="text" placeholder="전화번호 (선택)" />
          <input v-model="form.website" type="text" placeholder="홈페이지 URL (선택)" />

          <!-- 춤 종류 -->
          <label class="form-label">춤 종류 (복수 선택)</label>
          <div class="genre-checkboxes">
            <label v-for="opt in GENRE_OPTIONS" :key="opt.value" class="checkbox-label">
              <input v-model="form.dance_genres" type="checkbox" :value="opt.value" />
              {{ opt.label }}
            </label>
          </div>

          <!-- 유형별 추가 필드: 클럽 -->
          <template v-if="form.venue_type === 'club'">
            <label class="form-label">클럽 정보</label>
            <input v-model="form.cover_charge" type="text" placeholder="입장료 (예: 20,000원)" />
            <div class="inline-checks">
              <label class="checkbox-label"><input v-model="form.has_bar" type="checkbox" /> 바/주류 판매</label>
            </div>
          </template>

          <!-- 유형별 추가 필드: 학원 -->
          <template v-if="form.venue_type === 'academy'">
            <label class="form-label">동호회 정보</label>
            <div class="inline-checks">
              <label class="checkbox-label"><input v-model="form.has_trial_class" type="checkbox" /> 체험 수업 가능</label>
            </div>
            <input v-if="form.has_trial_class" v-model="form.trial_class_fee" type="text" placeholder="체험 수업비 (예: 10,000원)" />
          </template>

          <!-- 유형별 추가 필드: 연습실 -->
          <template v-if="form.venue_type === 'practice_room'">
            <label class="form-label">연습실 정보</label>
            <input v-model="form.rental_fee" type="text" placeholder="대관료 (예: 시간당 20,000원)" />
            <input v-model.number="form.area_sqm" type="number" placeholder="면적 (㎡)" />
            <div class="inline-checks">
              <label class="checkbox-label"><input v-model="form.has_mirror" type="checkbox" /> 거울</label>
              <label class="checkbox-label"><input v-model="form.has_sound_system" type="checkbox" /> 음향 시설</label>
            </div>
          </template>

          <!-- 공통 시설 정보 -->
          <label class="form-label">시설 정보</label>
          <input v-model="form.floor_type" type="text" placeholder="플로어 타입 (예: 우드)" />
          <input v-model.number="form.capacity" type="number" placeholder="수용 인원" />
          <div class="inline-checks">
            <label class="checkbox-label"><input v-model="form.has_parking" type="checkbox" /> 주차 가능</label>
          </div>
          <input v-if="form.has_parking" v-model="form.parking_info" type="text" placeholder="주차 정보 (예: 건물 지하 주차장)" />

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
import { VENUE_TYPE_OPTIONS, GENRE_OPTIONS } from '@/utils/constants.js'
import { useAuth } from '@/composables/useAuth.js'
import { useVenues } from '@/composables/useVenues.js'
import { useImageUpload } from '@/composables/useImageUpload.js'
import { useLocationSearch } from '@/composables/useLocationSearch.js'
import { useMarkdownEditor } from '@/composables/useMarkdownEditor.js'
import { renderMarkdown } from '@/utils/markdown.js'

const route = useRoute()
const router = useRouter()
const { currentUser } = useAuth()
const { createVenue, updateVenue } = useVenues()

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
  venue_type: 'club',
  name: '',
  description: '',
  address: '',
  address_detail: '',
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
  if (!form.name) form.name = place.place_name
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
  if (!form.name.trim()) { error.value = '장소명을 입력해 주세요'; return }
  if (!form.latitude) { error.value = '위치를 선택해 주세요'; return }
  error.value = ''
  step.value = 2
}

// ===== 제출 =====
async function handleSubmit() {
  error.value = ''
  if (!form.name.trim()) { error.value = '장소명을 입력해 주세요'; return }
  if (!form.latitude || !form.longitude) { error.value = '위치를 선택해 주세요'; return }

  const body = {
    venue_type: form.venue_type,
    name: form.name,
    description: form.description || null,
    address: form.address || null,
    address_detail: form.address_detail || null,
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

  let savedId
  if (editMode.value) {
    const result = await updateVenue(editId.value, body)
    if (!result.ok) { error.value = result.error; return }
    savedId = editId.value
  } else {
    const result = await createVenue(body)
    if (!result.ok) { error.value = result.error; return }
    savedId = result.venueId
  }

  await saveMedia('venues', savedId)
  router.push(`/venues/${savedId}`)
}

// ===== 수정 모드: 기존 데이터 로드 =====
async function loadVenue() {
  const res = await apiFetch(`/api/venues/${editId.value}`)
  if (!res.ok) { router.push('/'); return }
  const v = await res.json()
  Object.assign(form, {
    venue_type: v.venue_type || 'club',
    name: v.name || '',
    description: v.description || '',
    address: v.address || '',
    address_detail: v.address_detail || '',
    latitude: v.latitude || '',
    longitude: v.longitude || '',
    phone: v.phone || '',
    website: v.website || '',
    dance_genres: v.dance_genres || [],
    cover_charge: v.cover_charge || '',
    has_bar: !!v.has_bar,
    has_trial_class: !!v.has_trial_class,
    trial_class_fee: v.trial_class_fee || '',
    rental_fee: v.rental_fee || '',
    area_sqm: v.area_sqm || null,
    has_mirror: !!v.has_mirror,
    has_sound_system: !!v.has_sound_system,
    floor_type: v.floor_type || '',
    capacity: v.capacity || null,
    has_parking: !!v.has_parking,
    parking_info: v.parking_info || '',
  })
  setExistingMedia(v.media)
}

// ===== onMounted =====
onMounted(() => {
  if (!currentUser.value) { router.push('/'); return }
  if (editMode.value) {
    loadVenue().then(() => window.kakao.maps.load(initMinimap))
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
