<template>
  <div v-if="visible" class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="modal-close" @click="$emit('close')">✕</button>
      <template v-if="event">
        <span :class="['event-type-badge', `type-${event.event_type}`]">
          {{ TYPE_LABELS[event.event_type] }}
        </span>
        <span
          v-for="g in event.dance_genres || []"
          :key="g"
          :class="['genre-badge', `genre-${g}`]"
        >
          {{ GENRE_LABELS[g] }}
        </span>
        <span v-if="event.difficulty" class="difficulty-badge">
          {{ DIFFICULTY_LABELS[event.difficulty] }}
        </span>
        <h2 style="margin-top:8px">{{ event.title }}</h2>
        <p v-if="event.description" style="margin:8px 0;color:#bbb;font-size:0.85rem">{{ event.description }}</p>

        <!-- 이미지 갤러리 -->
        <ImageGallery :images="event.media || []" />        

        <div class="detail-row"><span class="detail-label">장소</span>{{ event.location_name }}</div>
        <div v-if="event.address" class="detail-row"><span class="detail-label">주소</span>{{ event.address }}</div>
        <div class="detail-row"><span class="detail-label">시작</span>{{ formatDate(event.start_date) }}</div>
        <div v-if="event.end_date" class="detail-row"><span class="detail-label">종료</span>{{ formatDate(event.end_date) }}</div>

        <!-- 가격 정보 -->
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
        <div v-if="event.is_recurring" class="detail-row"><span class="detail-label">반복</span>반복 이벤트</div>

        <div class="detail-row"><span class="detail-label">주최</span>{{ event.organizer_nickname || '-' }}</div>

        <div v-if="isOwner" class="action-row">
          <button class="btn-ghost" @click="$emit('edit', event)">수정</button>
          <button class="btn-danger" @click="handleDelete">삭제</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TYPE_LABELS, GENRE_LABELS, DIFFICULTY_LABELS } from '../utils/constants.js'
import { formatDate } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'
import { useEvents } from '../composables/useEvents.js'
import ImageGallery from './ImageGallery.vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  event: { type: Object, default: null },
})
const emit = defineEmits(['close', 'edit'])

const { currentUser } = useAuth()
const { deleteEvent } = useEvents()

const isOwner = computed(() => {
  return currentUser.value && props.event && currentUser.value.id === props.event.organizer_id
})

async function handleDelete() {
  if (!confirm('이벤트를 삭제할까요?')) return
  const ok = await deleteEvent(props.event.id)
  if (ok) emit('close')
}
</script>
