<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <span>이벤트 {{ events.length }}개</span>
      <button
        v-if="currentUser?.is_organizer"
        class="btn-primary"
        @click="$emit('addEvent')"
      >
        + 이벤트 등록
      </button>
    </div>
    <ul id="event-list">
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
        <div class="event-title">{{ ev.title }}</div>
        <div class="event-meta">📍 {{ ev.location_name }}</div>
        <div class="event-meta">📅 {{ formatDate(ev.start_date) }}</div>
      </li>
    </ul>
  </aside>
</template>

<script setup>
import { TYPE_LABELS, GENRE_LABELS } from '../utils/constants.js'
import { formatDate } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'
import { useEvents } from '../composables/useEvents.js'

defineEmits(['addEvent', 'selectEvent'])
const { currentUser } = useAuth()
const { events } = useEvents()
</script>
