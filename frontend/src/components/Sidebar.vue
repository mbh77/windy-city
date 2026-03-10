<template>
  <aside class="sidebar">
    <!-- 탭 -->
    <div class="tab-group">
      <button :class="['tab', { active: activeTab === 'events' }]" @click="activeTab = 'events'">
        이벤트 {{ visibleEvents.length }}
      </button>
      <button :class="['tab', { active: activeTab === 'venues' }]" @click="activeTab = 'venues'">
        장소 {{ visibleVenues.length }}
      </button>
    </div>

    <!-- 이벤트 탭 -->
    <template v-if="activeTab === 'events'">
      <div class="sidebar-header">
        <span>이벤트 {{ visibleEvents.length }}개</span>
        <button
          v-if="currentUser?.is_organizer"
          class="btn-primary"
          @click="$emit('addEvent')"
        >
          + 이벤트
        </button>
      </div>
      <ul class="sidebar-list">
        <li v-for="ev in visibleEvents" :key="ev.id" @click="$emit('selectEvent', ev)">
          <span :class="['event-type-badge', `type-${ev.event_type}`]">
            {{ TYPE_LABELS[ev.event_type] }}
          </span>
          <span
            v-for="g in ev.dance_genres || []"
            :key="g"
            :class="['genre-badge', `genre-${g}`]"
          >
            {{ GENRE_LABELS[g] }}
          </span>
          <div class="item-title">{{ ev.title }}</div>
          <div class="item-meta">{{ ev.location_name }}</div>
          <div class="item-meta">{{ formatDate(ev.start_date) }}</div>
        </li>
        <li v-if="visibleEvents.length === 0" class="empty-msg">현재 지도 영역에 이벤트가 없습니다</li>
      </ul>
    </template>

    <!-- 장소 탭 -->
    <template v-if="activeTab === 'venues'">
      <div class="sidebar-header">
        <span>장소 {{ visibleVenues.length }}개</span>
        <button
          v-if="currentUser?.is_organizer"
          class="btn-primary"
          @click="$emit('addVenue')"
        >
          + 장소
        </button>
      </div>
      <ul class="sidebar-list">
        <li v-for="v in visibleVenues" :key="v.id" @click="$emit('selectVenue', v)">
          <span :class="['venue-type-badge', `vtype-${v.venue_type}`]">
            {{ VENUE_TYPE_LABELS[v.venue_type] }}
          </span>
          <span
            v-for="g in v.dance_genres || []"
            :key="g"
            :class="['genre-badge', `genre-${g}`]"
          >
            {{ GENRE_LABELS[g] }}
          </span>
          <div class="item-title">{{ v.name }}</div>
          <div v-if="v.address" class="item-meta">{{ v.address }}</div>
        </li>
        <li v-if="visibleVenues.length === 0" class="empty-msg">현재 지도 영역에 장소가 없습니다</li>
      </ul>
    </template>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { TYPE_LABELS, GENRE_LABELS, VENUE_TYPE_LABELS } from '../utils/constants.js'
import { formatDate } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'
import { useEvents } from '../composables/useEvents.js'
import { useVenues } from '../composables/useVenues.js'

defineEmits(['addEvent', 'selectEvent', 'addVenue', 'selectVenue'])
const props = defineProps({
  mapBounds: { type: Object, default: null },
  visibleCategories: {
    type: Object,
    default: () => ({ club: true, academy: true, practice_room: true, event: true }),
  },
})
const { currentUser } = useAuth()
const { events } = useEvents()
const { venues } = useVenues()

const activeTab = ref('events')

// 지도 영역 내 항목만 필터링
function inBounds(lat, lng) {
  if (!props.mapBounds) return true
  const { swLat, swLng, neLat, neLng } = props.mapBounds
  return lat >= swLat && lat <= neLat && lng >= swLng && lng <= neLng
}

const visibleEvents = computed(() =>
  props.visibleCategories.event
    ? events.value.filter(ev => inBounds(ev.latitude, ev.longitude))
    : []
)

const visibleVenues = computed(() =>
  venues.value.filter(v =>
    props.visibleCategories[v.venue_type] && inBounds(v.latitude, v.longitude)
  )
)
</script>
