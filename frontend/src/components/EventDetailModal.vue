<template>
  <div v-if="visible" class="modal modal-detail" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="modal-close" @click="$emit('close')">✕</button>
      <template v-if="event">
        <!-- 뱃지 -->
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

        <h2 style="margin-top:8px">{{ event.title }}</h2>

        <!-- 이미지 갤러리 -->
        <ImageGallery :images="event.media || []" />

        <!-- 설명 -->
        <div v-if="event.description" class="markdown-body" style="margin:8px 0;font-size:0.85rem;" v-html="renderMarkdown(event.description)"></div>

        <!-- 상세 정보 -->
        <div class="detail-row"><span class="detail-label">장소</span>{{ event.location_name }}</div>
        <div v-if="event.address" class="detail-row"><span class="detail-label">주소</span>{{ event.address }}<span v-if="event.address_detail"> {{ event.address_detail }}</span></div>
        <div v-if="event.start_time" class="detail-row">
          <span class="detail-label">시간</span>
          {{ formatTime(event.start_time) }}{{ event.end_time ? ' ~ ' + formatTime(event.end_time) : '' }}
        </div>
        <div v-if="event.price" class="detail-row"><span class="detail-label">가격</span>{{ event.price }}</div>
        <div v-if="event.early_bird_price" class="detail-row"><span class="detail-label">얼리버드</span>{{ event.early_bird_price }}</div>
        <!-- 소셜 파티 -->
        <div v-if="event.dj_name" class="detail-row"><span class="detail-label">DJ</span>{{ event.dj_name }}</div>
        <div v-if="event.dress_code" class="detail-row"><span class="detail-label">드레스코드</span>{{ event.dress_code }}</div>
        <div v-if="event.has_pre_lesson" class="detail-row"><span class="detail-label">프리레슨</span>포함</div>
        <!-- 워크샵/수업 -->
        <div v-if="event.instructor_name" class="detail-row"><span class="detail-label">강사</span>{{ event.instructor_name }}</div>
        <!-- 반복 (주기·요일만 표시) -->
        <template v-if="event.is_recurring && event.recurrence_rule">
          <div class="detail-row">
            <span class="detail-label">반복</span>
            {{ event.recurrence_rule.frequency === 'weekly' ? '매주' : '격주' }}
            {{ (event.recurrence_rule.days || []).map(d => DAY_LABELS[d]).join(' · ') }}
          </div>
        </template>
        <div v-else-if="event.is_recurring" class="detail-row"><span class="detail-label">반복</span>반복 강습·행사</div>

        <div class="action-row">
          <router-link :to="`/events/${event.id}`" class="btn-ghost">상세 보기</router-link>
          <template v-if="isOwner">
            <router-link :to="`/events/${event.id}/edit`" class="btn-ghost">수정</router-link>
            <button class="btn-danger" @click="handleDelete">삭제</button>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TYPE_LABELS, GENRE_LABELS, DIFFICULTY_LABELS } from '../utils/constants.js'
import { formatTime } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'
import { useEvents } from '../composables/useEvents.js'
import ImageGallery from './ImageGallery.vue'
import { renderMarkdown } from '@/utils/markdown.js'

const DAY_LABELS = { mon: '월', tue: '화', wed: '수', thu: '목', fri: '금', sat: '토', sun: '일' }

const props = defineProps({
  visible: { type: Boolean, default: false },
  event: { type: Object, default: null },
})
const emit = defineEmits(['close'])

const { currentUser } = useAuth()
const { deleteEvent } = useEvents()

const isOwner = computed(() => {
  return currentUser.value && props.event && (currentUser.value.id === props.event.organizer_id || currentUser.value.is_admin)
})

async function handleDelete() {
  if (!confirm('강습·행사를 삭제할까요?')) return
  const ok = await deleteEvent(props.event.id)
  if (ok) emit('close')
}
</script>
