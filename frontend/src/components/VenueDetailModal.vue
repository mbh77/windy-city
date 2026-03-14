<template>
  <div v-if="visible" class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="modal-close" @click="$emit('close')">✕</button>
      <template v-if="venue">
        <span :class="['venue-type-badge', `vtype-${venue.venue_type}`]">
          {{ VENUE_TYPE_LABELS[venue.venue_type] }}
        </span>
        <span
          v-for="g in venue.dance_genres || []"
          :key="g"
          :class="['genre-badge', `genre-${g}`]"
        >
          {{ GENRE_LABELS[g] }}
        </span>
        <h2 style="margin-top:8px">{{ venue.name }}</h2>

        <p v-if="venue.description" class="venue-desc">{{ venue.description }}</p>

        <div v-if="venue.address" class="detail-row">
          <span class="detail-label">주소</span>{{ venue.address }}
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

        <div class="detail-row">
          <span class="detail-label">등록자</span>{{ venue.owner_nickname || '-' }}
        </div>

        <div v-if="isOwner" class="action-row">
          <button class="btn-primary" @click="$emit('edit', venue)">수정</button>
          <button class="btn-danger" @click="handleDelete">삭제</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { VENUE_TYPE_LABELS, GENRE_LABELS } from '../utils/constants.js'
import { useAuth } from '../composables/useAuth.js'
import { useVenues } from '../composables/useVenues.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
  venue: { type: Object, default: null },
})
const emit = defineEmits(['close','edit'])

const { currentUser } = useAuth()
const { deleteVenue } = useVenues()

const isOwner = computed(() => {
  return currentUser.value && props.venue && currentUser.value.id === props.venue.owner_id
})

async function handleDelete() {
  if (!confirm('장소를 삭제할까요?')) return
  const ok = await deleteVenue(props.venue.id)
  if (ok) emit('close')
}
</script>
