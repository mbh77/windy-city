<template>
  <div v-if="visible" class="modal modal-detail" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="modal-close" @click="$emit('close')">✕</button>
      <template v-if="venue">
        <!-- 뱃지 -->
        <div class="badge-row">
          <span :class="['venue-type-badge', `vtype-${venue.venue_type}`]">
            {{ VENUE_TYPE_LABELS[venue.venue_type] }}
          </span>
          <span v-for="g in venue.dance_genres || []" :key="g"
                :class="['genre-badge', `genre-${g}`]">
            {{ GENRE_LABELS[g] }}
          </span>
        </div>

        <div class="title-row">
          <h2 style="margin-top:8px">{{ venue.name }}</h2>
          <button class="copy-link-btn" @click="copyLink" :title="copied ? '복사됨!' : '링크 복사'">
            {{ copied ? '✔' : '🔗' }}
          </button>
        </div>

        <!-- 이미지 갤러리 -->
        <ImageGallery :images="venue.media || []" />

        <!-- 설명 -->
        <div v-if="venue.description" class="venue-desc markdown-body" v-html="renderMarkdown(venue.description)"></div>

        <!-- 상세 정보 -->
        <div v-if="venue.address" class="detail-row">
          <span class="detail-label">주소</span>{{ venue.address }}<span v-if="venue.address_detail"> {{ venue.address_detail }}</span>
        </div>
        <div v-if="venue.phone" class="detail-row">
          <span class="detail-label">전화</span>{{ venue.phone }}
        </div>
        <div v-if="venue.website" class="detail-row">
          <span class="detail-label">웹사이트</span>
          <a :href="venue.website" target="_blank" class="venue-link">{{ venue.website }}</a>
        </div>
        <!-- 클럽 -->
        <template v-if="venue.venue_type === 'club'">
          <div v-if="venue.cover_charge" class="detail-row">
            <span class="detail-label">입장료</span>{{ venue.cover_charge }}
          </div>
          <div v-if="venue.has_bar" class="detail-row">
            <span class="detail-label">바</span>주류 판매
          </div>
        </template>
        <!-- 학원 -->
        <template v-if="venue.venue_type === 'academy'">
          <div v-if="venue.has_trial_class" class="detail-row">
            <span class="detail-label">체험수업</span>{{ venue.trial_class_fee || '가능' }}
          </div>
        </template>
        <!-- 연습실 -->
        <template v-if="venue.venue_type === 'practice_room'">
          <div v-if="venue.rental_fee" class="detail-row">
            <span class="detail-label">대관료</span>{{ venue.rental_fee }}
          </div>
          <div v-if="venue.area_sqm" class="detail-row">
            <span class="detail-label">면적</span>{{ venue.area_sqm }}㎡
          </div>
        </template>
        <!-- 공통 시설 -->
        <div v-if="venue.floor_type" class="detail-row">
          <span class="detail-label">플로어</span>{{ venue.floor_type }}
        </div>
        <div v-if="venue.has_parking" class="detail-row">
          <span class="detail-label">주차</span>{{ venue.parking_info || '가능' }}
        </div>

        <div class="action-row">
          <router-link :to="`/venues/${venue.id}`" class="btn-ghost">상세 보기</router-link>
          <template v-if="isOwner">
            <router-link :to="`/venues/${venue.id}/edit`" class="btn-ghost">수정</router-link>
            <button class="btn-danger" @click="handleDelete">삭제</button>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { VENUE_TYPE_LABELS, GENRE_LABELS } from '../utils/constants.js'
import { useAuth } from '../composables/useAuth.js'
import { useVenues } from '../composables/useVenues.js'
import ImageGallery from './ImageGallery.vue'
import { renderMarkdown } from '@/utils/markdown.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
  venue: { type: Object, default: null },
})
const emit = defineEmits(['close'])

const { currentUser } = useAuth()
const { deleteVenue } = useVenues()
const copied = ref(false)

function copyLink() {
  const url = `${window.location.origin}/venues/${props.venue.id}`
  navigator.clipboard.writeText(url).then(() => {
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  })
}

const isOwner = computed(() => {
  return currentUser.value && props.venue && (currentUser.value.id === props.venue.owner_id || currentUser.value.is_admin)
})

async function handleDelete() {
  if (!confirm('장소를 삭제할까요?')) return
  const ok = await deleteVenue(props.venue.id)
  if (ok) emit('close')
}
</script>
