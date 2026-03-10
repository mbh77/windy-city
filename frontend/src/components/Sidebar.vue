<template>
  <aside class="sidebar">
    <!-- 탭 -->
    <div class="tab-group">
      <button :class="['tab', { active: activeTab === 'events' }]" @click="activeTab = 'events'">
        이벤트 {{ events.length }}
      </button>
      <button :class="['tab', { active: activeTab === 'venues' }]" @click="activeTab = 'venues'">
        장소 {{ venues.length }}
      </button>
    </div>

    <!-- 이벤트 탭 -->
    <template v-if="activeTab === 'events'">
      <div class="sidebar-header">
        <span>이벤트 {{ events.length }}개</span>
        <button
          v-if="currentUser?.is_organizer"
          class="btn-primary"
          @click="$emit('addEvent')"
        >
          + 이벤트
        </button>
      </div>
      <ul class="sidebar-list">
        <li v-for="ev in events" :key="ev.id" @click="$emit('selectEvent', ev)">
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
        <li v-if="events.length === 0" class="empty-msg">이벤트가 없습니다</li>
      </ul>
    </template>

    <!-- 장소 탭 -->
    <template v-if="activeTab === 'venues'">
      <div class="sidebar-header">
        <span>장소 {{ venues.length }}개</span>
        <button
          v-if="currentUser?.is_organizer"
          class="btn-primary"
          @click="$emit('addVenue')"
        >
          + 장소
        </button>
      </div>
      <ul class="sidebar-list">
        <li v-for="v in venues" :key="v.id" @click="$emit('selectVenue', v)">
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
        <li v-if="venues.length === 0" class="empty-msg">등록된 장소가 없습니다</li>
      </ul>
    </template>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { TYPE_LABELS, GENRE_LABELS, VENUE_TYPE_LABELS } from '../utils/constants.js'
import { formatDate } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'
import { useEvents } from '../composables/useEvents.js'
import { useVenues } from '../composables/useVenues.js'

defineEmits(['addEvent', 'selectEvent', 'addVenue', 'selectVenue'])
const { currentUser } = useAuth()
const { events } = useEvents()
const { venues } = useVenues()

const activeTab = ref('events')
</script>
