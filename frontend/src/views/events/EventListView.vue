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
      <ul class="board-list">
        <li v-for="event in events" :key="event.id" class="board-item" @click="goDetail(event.id)">
          <div class="board-item-title">
            <span :class="['event-type-badge', `type-${event.event_type}`]" style="font-size:0.7rem; margin-right:6px;">
              {{ TYPE_LABELS[event.event_type] }}
            </span>
            {{ event.title }}
          </div>
          <div class="board-item-meta">
            <span>{{ event.organizer_nickname }}</span>
            <span>{{ formatCreatedAt(event.created_at) }}</span>
            <span>👁 {{ event.view_count || 0 }}</span>
            <span v-if="event.comment_count > 0">💬 {{ event.comment_count }}</span>
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
import { apiFetch, formatCreatedAt } from '@/utils/api.js'
import { useAuth } from '@/composables/useAuth.js'
import { TYPE_LABELS } from '@/utils/constants.js'

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
.board-toolbar { display: flex; gap: 8px; margin-bottom: 12px; }
.board-toolbar input { flex: 1; background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 8px 10px; font-size: 0.85rem; }
.board-toolbar .btn-primary { padding: 8px 16px; font-size: 0.85rem; white-space: nowrap; }
.board-list { list-style: none; padding: 0; margin: 0; }
.board-item { padding: 12px 0; border-bottom: 1px solid #EDE5DB; cursor: pointer; }
.board-item:hover { background: #FFFFFF; }
.board-item-title { font-size: 0.9rem; margin-bottom: 4px; }
.board-item-meta { font-size: 0.75rem; color: #8B7B6B; display: flex; gap: 12px; }
.board-empty { padding: 40px 0; text-align: center; color: #8B7B6B; font-size: 0.85rem; }
.board-paging { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 16px; }
.board-paging button { background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 4px 12px; font-size: 0.8rem; cursor: pointer; }
.board-paging button:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
