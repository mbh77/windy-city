<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn">지도</router-link>
      <h1 class="page-title">댄스 클래스</h1>
    </header>

    <main class="page-body">
      <!-- 검색 + 등록 -->
      <div class="board-toolbar">
        <input v-model="searchQuery" placeholder="제목, 장소, 강사명 검색..." @input="debouncedSearch" />
        <router-link v-if="currentUser" to="/events/new" class="btn-primary">등록</router-link>
      </div>

      <!-- 목록 -->
      <ul class="event-list">
        <li v-for="event in events" :key="event.id" class="event-card" @click="goDetail(event.id)">
          <div class="event-info">
            <div class="event-badges">
              <span :class="['event-type-badge', `type-${event.event_type}`]">{{ TYPE_LABELS[event.event_type] }}</span>
              <span v-for="g in event.dance_genres || []" :key="g" :class="['genre-badge', `genre-${g}`]">{{ GENRE_LABELS[g] }}</span>
            </div>
            <div class="event-title">{{ event.title }}</div>
            <div class="event-detail">
              <span v-if="event.location_name">{{ event.location_name }}</span>
              <span v-if="event.event_date" class="event-date">{{ formatDate(event.event_date) }}</span>
              <span v-if="event.event_end_date" class="event-date"> ~ {{ formatDate(event.event_end_date) }}</span>
            </div>
            <div class="event-meta">
              <span>{{ event.organizer_nickname }}</span>
              <span>{{ formatCreatedAt(event.created_at) }}</span>
              <span>👁 {{ event.view_count || 0 }}</span>
              <span v-if="event.comment_count > 0">💬 {{ event.comment_count }}</span>
            </div>
          </div>
        </li>
        <li v-if="events.length === 0" class="board-empty">등록된 강습·행사가 없습니다</li>
      </ul>

      <!-- 페이징 -->
      <div class="board-paging" v-if="totalPages > 1">
        <button :disabled="page <= 1" @click="changePage(page - 1)">◀ 이전</button>
        <span>{{ page }} / {{ totalPages }}</span>
        <button :disabled="page >= totalPages" @click="changePage(page + 1)">다음 ▶</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch, formatDate, formatTime, formatCreatedAt } from '@/utils/api.js'
import { useAuth } from '@/composables/useAuth.js'
import { TYPE_LABELS, GENRE_LABELS } from '@/utils/constants.js'

const router = useRouter()
const { currentUser } = useAuth()

const events = ref([])
const total = ref(0)
const page = ref(1)
const limit = 20
const searchQuery = ref('')
let debounceTimer = null

const totalPages = computed(() => Math.ceil(total.value / limit))

onMounted(() => loadEvents())

async function loadEvents() {
  const params = new URLSearchParams({
    page: page.value,
    limit,
    q: searchQuery.value,
  })
  const res = await apiFetch(`/api/events/list?${params}`)
  if (res.ok) {
    const data = await res.json()
    events.value = data.events
    total.value = data.total
  }
}

function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    loadEvents()
  }, 300)
}

function changePage(p) {
  page.value = p
  loadEvents()
}

function goDetail(id) {
  router.push(`/events/${id}`)
}

</script>

<style scoped>
.board-toolbar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.board-toolbar input { flex: 1; background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 8px 10px; font-size: 0.85rem; margin-bottom: 0 !important; }
.board-toolbar .btn-primary { padding: 8px 16px; font-size: 0.85rem; white-space: nowrap; display: inline-flex; align-items: center; justify-content: center; text-decoration: none; box-sizing: border-box; }
.event-list { list-style: none; padding: 0; margin: 0; }
.event-card { display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid #EDE5DB; cursor: pointer; }
.event-card:hover { background: #FAFAFA; }
.event-info { flex: 1; min-width: 0; }
.event-badges { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 4px; }
.event-badges .event-type-badge,
.event-badges .genre-badge { font-size: 0.65rem; }
.event-title { font-size: 0.9rem; font-weight: 600; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.event-detail { font-size: 0.78rem; color: #5A4A3A; display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 4px; }
.event-date { color: #5BA89E; }
.event-meta { font-size: 0.7rem; color: #8B7B6B; display: flex; gap: 10px; }
.board-empty { padding: 40px 0; text-align: center; color: #8B7B6B; font-size: 0.85rem; list-style: none; }
.board-paging { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 16px; }
.board-paging button { background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 4px 12px; font-size: 0.8rem; cursor: pointer; }
.board-paging button:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
