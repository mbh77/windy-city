<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn">지도</router-link>
      <h1 class="page-title">♥ 내 북마크</h1>
    </header>

    <main class="page-body">
      <div v-if="!currentUser" class="board-empty">로그인이 필요합니다</div>

      <template v-else>
        <!-- 타입 필터 -->
        <div class="bookmark-tabs">
          <button :class="['tab-btn', { active: filterType === '' }]" @click="changeFilter('')">전체</button>
          <button :class="['tab-btn', { active: filterType === 'event' }]" @click="changeFilter('event')">강습·행사</button>
          <button :class="['tab-btn', { active: filterType === 'venue' }]" @click="changeFilter('venue')">장소</button>
        </div>

        <!-- 목록 -->
        <ul class="bookmark-list" v-if="items.length > 0">
          <!-- 이벤트 카드 -->
          <li v-for="item in items" :key="item.entity_type + '-' + item.entity_id"
              class="bookmark-card" @click="goDetail(item)">
            <div class="bookmark-content">
              <div class="bookmark-info">
                <div class="bookmark-badges">
                  <span v-if="item.entity_type === 'event'" :class="['event-type-badge', `type-${item.event_type}`]">
                    {{ TYPE_LABELS[item.event_type] || '행사' }}
                  </span>
                  <span v-else :class="['venue-type-badge', `vtype-${item.venue_type}`]">
                    {{ VENUE_TYPE_LABELS[item.venue_type] || '장소' }}
                  </span>
                  <span v-for="g in item.dance_genres || []" :key="g" :class="['genre-badge', `genre-${g}`]">
                    {{ GENRE_LABELS[g] }}
                  </span>
                  <span class="bookmark-title">{{ item.title || item.name }}</span>
                </div>
                <div class="bookmark-detail">
                  <span v-if="item.location_name || item.address">{{ item.location_name || item.address }}</span>
                  <span v-if="item.event_date" class="bookmark-date">{{ formatDate(item.event_date) }}</span>
                  <span v-if="item.start_time" class="bookmark-date">{{ item.start_time }}</span>
                </div>
              </div>
            </div>
            <div class="bookmark-meta">
              <span>{{ item.organizer_nickname || item.owner_nickname || '-' }}</span>
              <span>👁 {{ item.view_count || 0 }}</span>
              <button class="bookmark-btn-sm" @click.stop="handleRemove(item)">♥</button>
            </div>
          </li>
        </ul>

        <div v-else-if="!loading" class="board-empty">저장한 북마크가 없습니다</div>
        <div v-if="loading" class="board-empty">불러오는 중...</div>

        <!-- 페이징 -->
        <div class="board-paging" v-if="totalPages > 1">
          <button :disabled="page <= 1" @click="changePage(page - 1)">◀ 이전</button>
          <span>{{ page }} / {{ totalPages }}</span>
          <button :disabled="page >= totalPages" @click="changePage(page + 1)">다음 ▶</button>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch, formatDate } from '@/utils/api.js'
import { TYPE_LABELS, VENUE_TYPE_LABELS, GENRE_LABELS } from '@/utils/constants.js'
import { useAuth } from '@/composables/useAuth.js'
import { useBookmarks } from '@/composables/useBookmarks.js'

const router = useRouter()
const { currentUser } = useAuth()
const { toggleBookmark } = useBookmarks()

const items = ref([])
const total = ref(0)
const page = ref(1)
const limit = 20
const filterType = ref('')
const loading = ref(false)

const totalPages = computed(() => Math.ceil(total.value / limit))

onMounted(() => {
  if (currentUser.value) loadBookmarks()
})

async function loadBookmarks() {
  loading.value = true
  const params = new URLSearchParams({ page: page.value, limit })
  if (filterType.value) params.set('entity_type', filterType.value)
  try {
    const res = await apiFetch(`/api/bookmarks/me/details?${params}`)
    if (res.ok) {
      const data = await res.json()
      items.value = data.items
      total.value = data.total
    }
  } finally {
    loading.value = false
  }
}

function changeFilter(type) {
  filterType.value = type
  page.value = 1
  loadBookmarks()
}

function changePage(p) {
  page.value = p
  loadBookmarks()
}

function goDetail(item) {
  if (item.entity_type === 'event') {
    router.push(`/events/${item.entity_id}`)
  } else {
    router.push(`/venues/${item.entity_id}`)
  }
}

async function handleRemove(item) {
  await toggleBookmark(item.entity_type, item.entity_id)
  items.value = items.value.filter(
    i => !(i.entity_type === item.entity_type && i.entity_id === item.entity_id)
  )
  total.value = Math.max(0, total.value - 1)
}
</script>

<style scoped>
.bookmark-tabs { display: flex; gap: 4px; margin-bottom: 12px; }
.tab-btn {
  padding: 6px 14px; border-radius: 16px; font-size: 0.8rem; cursor: pointer;
  border: 1px solid #E0D5C8; background: transparent; color: #5A4A3A; transition: all 0.15s;
}
.tab-btn.active { background: #D4725C; color: #fff; border-color: #D4725C; }
.tab-btn:hover { border-color: #8B7B6B; }

.bookmark-list { list-style: none; padding: 0; margin: 0; }
.bookmark-card { padding: 12px 0; border-bottom: 1px solid #EDE5DB; cursor: pointer; }
.bookmark-card:hover { background: #FAFAFA; }
.bookmark-content { display: flex; gap: 12px; margin-bottom: 6px; }
.bookmark-thumb { width: 48px; height: 48px; border-radius: 8px; object-fit: cover; background: #EDE5DB; flex-shrink: 0; }
.bookmark-info { flex: 1; min-width: 0; }
.bookmark-badges { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 4px; }
.bookmark-badges .event-type-badge,
.bookmark-badges .venue-type-badge,
.bookmark-badges .genre-badge { font-size: 0.65rem; }
.bookmark-title { font-size: 0.9rem; font-weight: 600; }
.bookmark-detail { font-size: 0.78rem; color: #5A4A3A; display: flex; flex-wrap: wrap; gap: 6px; }
.bookmark-date { color: #5BA89E; }
.bookmark-meta { font-size: 0.7rem; color: #8B7B6B; display: flex; gap: 10px; align-items: center; }

.board-empty { padding: 40px 0; text-align: center; color: #8B7B6B; font-size: 0.85rem; list-style: none; }
.board-paging { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 16px; }
.board-paging button { background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 4px 12px; font-size: 0.8rem; cursor: pointer; }
.board-paging button:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
