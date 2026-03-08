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
        <h2 style="margin-top:8px">{{ event.title }}</h2>
        <p v-if="event.description" style="margin:8px 0;color:#bbb;font-size:0.85rem">{{ event.description }}</p>
        <div class="detail-row"><span class="detail-label">장소</span>{{ event.location_name }}</div>
        <div v-if="event.address" class="detail-row"><span class="detail-label">주소</span>{{ event.address }}</div>
        <div class="detail-row"><span class="detail-label">시작</span>{{ formatDate(event.start_date) }}</div>
        <div v-if="event.end_date" class="detail-row"><span class="detail-label">종료</span>{{ formatDate(event.end_date) }}</div>
        <div class="detail-row"><span class="detail-label">주최</span>{{ event.organizer_nickname || '-' }}</div>
        <div v-if="isOwner" class="action-row">
          <button class="btn-danger" @click="handleDelete">삭제</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TYPE_LABELS, GENRE_LABELS } from '../utils/constants.js'
import { formatDate } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'
import { useEvents } from '../composables/useEvents.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
  event: { type: Object, default: null },
})
const emit = defineEmits(['close'])

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
