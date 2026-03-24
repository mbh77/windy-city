<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn">지도</router-link>
      <a class="page-nav-btn" @click="$router.back()">뒤로</a>
      <h1 class="page-title">강습·행사 상세</h1>
    </header>

    <main class="page-body" v-if="event">
      <!-- 뱃지들 -->
      <div class="badge-row">
        <span :class="['event-type-badge', `type-${event.event_type}`]">
          {{ TYPE_LABELS[event.event_type] }}
        </span>
        <span v-for="g in event.dance_genres || []" :key="g"
              :class="['genre-badge', `genre-${g}`]">
          {{ GENRE_LABELS[g] }}
        </span>
        <span v-if="event.difficulty" class="difficulty-badge">
          {{ DIFFICULTY_LABELS[event.difficulty] }}
        </span>
      </div>

      <!-- 제목 -->
      <h2 class="post-title">{{ event.title }}</h2>
      <div class="post-meta">
        <span>{{ event.organizer_nickname || '-' }}</span>
        <span>{{ formatEventDate(event) }}</span>
      </div>

      <!-- 이미지 갤러리 -->
      <ImageGallery :images="event.media || []" />

      <!-- 설명 (마크다운) -->
      <div v-if="event.description" class="post-body markdown-body"
           v-html="renderMarkdown(event.description)"></div>

      <!-- 상세 정보 -->
      <div class="detail-section">
        <div class="detail-row"><span class="detail-label">장소</span>{{ event.location_name }}</div>
        <div v-if="event.address" class="detail-row">
          <span class="detail-label">주소</span>{{ event.address }}
          <span v-if="event.address_detail"> {{ event.address_detail }}</span>
        </div>
        <!-- 시간 (있을 때만) -->
        <div v-if="event.start_time" class="detail-row">
          <span class="detail-label">시간</span>
          {{ event.start_time }}{{ event.end_time ? ' ~ ' + event.end_time : '' }}
        </div>
        <!-- 가격 -->
        <div v-if="event.price" class="detail-row"><span class="detail-label">가격</span>{{ event.price }}</div>
        <div v-if="event.early_bird_price" class="detail-row"><span class="detail-label">얼리버드</span>{{ event.early_bird_price }}</div>
        <!-- 소셜 파티 -->
        <div v-if="event.dj_name" class="detail-row"><span class="detail-label">DJ</span>{{ event.dj_name }}</div>
        <div v-if="event.dress_code" class="detail-row"><span class="detail-label">드레스코드</span>{{ event.dress_code }}</div>
        <div v-if="event.has_pre_lesson" class="detail-row"><span class="detail-label">프리레슨</span>포함</div>
        <!-- 워크샵/수업 -->
        <div v-if="event.instructor_name" class="detail-row"><span class="detail-label">강사</span>{{ event.instructor_name }}</div>
        <div v-if="event.max_participants" class="detail-row"><span class="detail-label">정원</span>{{ event.max_participants }}명</div>
        <div v-if="event.requires_partner" class="detail-row"><span class="detail-label">파트너</span>필요</div>
        <!-- 반복 -->
        <template v-if="event.is_recurring && event.recurrence_rule">
          <div class="detail-row">
            <span class="detail-label">반복</span>
            {{ event.recurrence_rule.frequency === 'weekly' ? '매주' : '격주' }}
            {{ (event.recurrence_rule.days || []).map(d => DAY_LABELS[d]).join(' · ') }}
          </div>
          <div v-if="event.recurrence_rule.skip_dates?.length" class="detail-row">
            <span class="detail-label">휴강일</span>
            <span class="date-tag-list-inline">
              <span v-for="d in event.recurrence_rule.skip_dates" :key="d" class="date-tag">{{ d }}</span>
            </span>
          </div>
          <div v-if="event.recurrence_rule.extra_dates?.length" class="detail-row">
            <span class="detail-label">보강일</span>
            <span class="date-tag-list-inline">
              <span v-for="d in event.recurrence_rule.extra_dates" :key="d" class="date-tag">{{ d }}</span>
            </span>
          </div>
        </template>
        <div v-else-if="event.is_recurring" class="detail-row"><span class="detail-label">반복</span>반복 강습·행사</div>

      </div>

      <!-- 수정/삭제 (본인 또는 관리자) -->
      <div class="post-actions" v-if="isOwner">
        <router-link :to="`/events/${event.id}/edit`" class="btn-ghost">수정</router-link>
        <button class="btn-danger" @click="handleDelete">삭제</button>
      </div>
    </main>

    <!-- 로딩/에러 -->
    <div v-else-if="loading" class="page-body">로딩 중...</div>
    <div v-else class="page-body">강습·행사를 찾을 수 없습니다.</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '@/utils/api.js'
import { TYPE_LABELS, GENRE_LABELS, DIFFICULTY_LABELS } from '@/utils/constants.js'
import { useAuth } from '@/composables/useAuth.js'
import ImageGallery from '@/components/ImageGallery.vue'
import { renderMarkdown } from '@/utils/markdown.js'

const DAY_LABELS = { mon: '월', tue: '화', wed: '수', thu: '목', fri: '금', sat: '토', sun: '일' }

const route = useRoute()
const router = useRouter()
const { currentUser } = useAuth()

const event = ref(null)
const loading = ref(true)

const isOwner = computed(() => {
  return currentUser.value && event.value && 
    (currentUser.value.id === event.value.organizer_id || currentUser.value.is_admin)
})

// 날짜 포맷 (새 구조 대응)
function formatEventDate(e) {
  if (!e.event_date) return '-'
  const d = new Date(e.event_date + 'T00:00:00')
  let str = d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'short', day: 'numeric' })
  if (e.event_end_date && e.event_end_date !== e.event_date) {
    const d2 = new Date(e.event_end_date + 'T00:00:00')
    str += ' ~ ' + d2.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
  }
  return str
}

async function fetchEvent() {
  try {
    const res = await apiFetch(`/api/events/${route.params.id}`)
    if (res.ok) {
      event.value = await res.json()
    }
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  if (!confirm('강습·행사를 삭제할까요?')) return
  const res = await apiFetch(`/api/events/${event.value.id}`, { method: 'DELETE' })
  if (res.ok) router.push('/')
}

onMounted(fetchEvent)
</script>
