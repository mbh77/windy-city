<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn">지도</router-link>
      <h1 class="page-title">🎭 댄스바·동호회·연습실</h1>
    </header>

    <main class="page-body">
      <!-- 검색 + 등록 -->
      <div class="board-toolbar">
        <input v-model="searchQuery" placeholder="장소명, 주소 검색..." @input="debouncedSearch" />
        <router-link v-if="currentUser" to="/venues/new" class="btn-primary">등록</router-link>
      </div>

      <!-- 목록 -->
      <ul class="venue-list">
        <li v-for="venue in venues" :key="venue.id" class="venue-card" @click="goDetail(venue.id)">
          <div class="venue-content">
            <img v-if="venue.media?.length" class="venue-thumb" :src="venue.media[0].url" />
            <div class="venue-info">
              <div class="venue-badges">
                <span :class="['venue-type-badge', `vtype-${venue.venue_type}`]">{{ VENUE_TYPE_LABELS[venue.venue_type] }}</span>
                <span v-for="g in venue.dance_genres || []" :key="g" :class="['genre-badge', `genre-${g}`]">{{ GENRE_LABELS[g] }}</span>
                <span class="venue-title">{{ venue.name }}</span>
              </div>
              <div class="venue-detail">
                <span v-if="venue.address">{{ venue.address }}</span>
              </div>
            </div>
          </div>
          <div class="venue-meta">
            <span>{{ venue.owner_nickname || '-' }}</span>
            <span>{{ formatCreatedAt(venue.created_at) }}</span>
            <span>👁 {{ venue.view_count || 0 }}</span>
            <span v-if="venue.comment_count > 0">💬 {{ venue.comment_count }}</span>
          </div>
        </li>
        <li v-if="venues.length === 0" class="board-empty">등록된 장소가 없습니다</li>
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
import { apiFetch, formatCreatedAt } from '@/utils/api.js'
import { useAuth } from '@/composables/useAuth.js'
import { VENUE_TYPE_LABELS, GENRE_LABELS } from '@/utils/constants.js'

const router = useRouter()
const { currentUser } = useAuth()

const venues = ref([])
const total = ref(0)
const page = ref(1)
const limit = 20
const searchQuery = ref('')
let debounceTimer = null

const totalPages = computed(() => Math.ceil(total.value / limit))

onMounted(() => loadVenues())

async function loadVenues() {
  const params = new URLSearchParams({
    page: page.value,
    limit,
    q: searchQuery.value,
  })
  const res = await apiFetch(`/api/venues/list?${params}`)
  if (res.ok) {
    const data = await res.json()
    venues.value = data.venues
    total.value = data.total
  }
}

function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    loadVenues()
  }, 300)
}

function changePage(p) {
  page.value = p
  loadVenues()
}

function goDetail(id) {
  router.push(`/venues/${id}`)
}

</script>

<style scoped>
.board-toolbar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.board-toolbar input { flex: 1; background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 8px 10px; font-size: 0.85rem; margin-bottom: 0 !important; }
.board-toolbar .btn-primary { padding: 8px 16px; font-size: 0.85rem; white-space: nowrap; display: inline-flex; align-items: center; justify-content: center; text-decoration: none; box-sizing: border-box; }
.venue-list { list-style: none; padding: 0; margin: 0; }
.venue-card { padding: 12px 0; border-bottom: 1px solid #EDE5DB; cursor: pointer; }
.venue-card:hover { background: #FAFAFA; }
.venue-content { display: flex; gap: 12px; margin-bottom: 6px; }
.venue-thumb { width: 48px; height: 48px; border-radius: 8px; object-fit: cover; background: #EDE5DB; flex-shrink: 0; }
.venue-info { flex: 1; min-width: 0; }
.venue-badges { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 4px; }
.venue-badges .venue-type-badge,
.venue-badges .genre-badge { font-size: 0.65rem; }
.venue-title { font-size: 0.9rem; font-weight: 600; margin-bottom: 4px; }
.venue-detail { font-size: 0.78rem; color: #5A4A3A; display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 4px; }
.venue-meta { font-size: 0.7rem; color: #8B7B6B; display: flex; gap: 10px; }
.board-empty { padding: 40px 0; text-align: center; color: #8B7B6B; font-size: 0.85rem; list-style: none; }
.board-paging { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 16px; }
.board-paging button { background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 4px 12px; font-size: 0.8rem; cursor: pointer; }
.board-paging button:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
