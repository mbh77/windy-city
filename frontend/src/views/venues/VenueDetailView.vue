<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn">지도</router-link>
      <router-link to="/venues" class="page-nav-btn">목록</router-link>
      <h1 class="page-title">🎭 댄스바·연습실</h1>
    </header>

    <main class="page-body" v-if="venue">
      <!-- 뱃지들 -->
      <div class="badge-row">
        <span :class="['venue-type-badge', `vtype-${venue.venue_type}`]">
          {{ VENUE_TYPE_LABELS[venue.venue_type] }}
        </span>
        <span v-for="g in venue.dance_genres || []" :key="g"
              :class="['genre-badge', `genre-${g}`]">
          {{ GENRE_LABELS[g] }}
        </span>
      </div>

      <!-- 이름 -->
      <h2 class="post-title">{{ venue.name }}</h2>
      <div class="post-meta">
        <span>{{ venue.owner_nickname || '-' }}</span>
        <span>조회 {{ venue.view_count || 0 }}</span>
      </div>

      <!-- 이미지 갤러리 -->
      <ImageGallery :images="venue.media || []" />

      <!-- 설명 (마크다운) -->
      <div v-if="venue.description" class="post-body markdown-body"
           v-html="renderMarkdown(venue.description)"></div>

      <!-- 상세 정보 -->
      <div class="detail-section">
        <div v-if="venue.address" class="detail-row">
          <span class="detail-label">주소</span>{{ venue.address }}
          <span v-if="venue.address_detail"> {{ venue.address_detail }}</span>
        </div>
        <div v-if="venue.phone" class="detail-row">
          <span class="detail-label">전화</span>{{ venue.phone }}
        </div>
        <div v-if="venue.website" class="detail-row">
          <span class="detail-label">웹사이트</span>
          <a :href="venue.website" target="_blank" class="venue-link">{{ venue.website }}</a>
        </div>

        <!-- 클럽 정보 -->
        <template v-if="venue.venue_type === 'club'">
          <div v-if="venue.cover_charge" class="detail-row">
            <span class="detail-label">입장료</span>{{ venue.cover_charge }}
          </div>
          <div v-if="venue.has_bar" class="detail-row">
            <span class="detail-label">바</span>주류 판매
          </div>
        </template>

        <!-- 학원 정보 -->
        <template v-if="venue.venue_type === 'academy'">
          <div v-if="venue.has_trial_class" class="detail-row">
            <span class="detail-label">체험수업</span>{{ venue.trial_class_fee || '가능' }}
          </div>
        </template>

        <!-- 연습실 정보 -->
        <template v-if="venue.venue_type === 'practice_room'">
          <div v-if="venue.rental_fee" class="detail-row">
            <span class="detail-label">대관료</span>{{ venue.rental_fee }}
          </div>
          <div v-if="venue.area_sqm" class="detail-row">
            <span class="detail-label">면적</span>{{ venue.area_sqm }}㎡
          </div>
          <div class="detail-row">
            <span class="detail-label">시설</span>
            <span v-if="venue.has_mirror" class="facility-tag">거울</span>
            <span v-if="venue.has_sound_system" class="facility-tag">음향</span>
            <span v-if="!venue.has_mirror && !venue.has_sound_system" style="color:#888">-</span>
          </div>
        </template>

        <!-- 공통 시설 -->
        <div v-if="venue.floor_type" class="detail-row">
          <span class="detail-label">플로어</span>{{ venue.floor_type }}
        </div>
        <div v-if="venue.capacity" class="detail-row">
          <span class="detail-label">수용</span>{{ venue.capacity }}명
        </div>
        <div v-if="venue.has_parking" class="detail-row">
          <span class="detail-label">주차</span>{{ venue.parking_info || '가능' }}
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="post-actions">
        <router-link :to="{ path: '/', query: { venueId: venue.id } }" class="btn-ghost">지도에서 보기</router-link>
        <template v-if="isOwner">
          <router-link :to="`/venues/${venue.id}/edit`" class="btn-ghost">수정</router-link>
          <button class="btn-danger" @click="handleDelete">삭제</button>
        </template>
      </div>

      <!-- 댓글 -->
      <CommentSection :apiBase="`/api/venues/${venue.id}`" />
    </main>

    <!-- 로딩/에러 -->
    <div v-else-if="loading" class="page-body">로딩 중...</div>
    <div v-else class="page-body">장소를 찾을 수 없습니다.</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '@/utils/api.js'
import { VENUE_TYPE_LABELS, GENRE_LABELS } from '@/utils/constants.js'
import { useAuth } from '@/composables/useAuth.js'
import ImageGallery from '@/components/ImageGallery.vue'
import CommentSection from '@/components/CommentSection.vue'
import { renderMarkdown } from '@/utils/markdown.js'

const route = useRoute()
const router = useRouter()
const { currentUser } = useAuth()

const venue = ref(null)
const loading = ref(true)

const isOwner = computed(() => {
  return currentUser.value && venue.value &&
    (currentUser.value.id === venue.value.owner_id || currentUser.value.is_admin)
})

async function fetchVenue() {
  try {
    const res = await apiFetch(`/api/venues/${route.params.id}`)
    if (res.ok) {
      venue.value = await res.json()
    }
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  if (!confirm('장소를 삭제할까요?')) return
  const res = await apiFetch(`/api/venues/${venue.value.id}`, { method: 'DELETE' })
  if (res.ok) router.push('/')
}

onMounted(fetchVenue)
</script>
