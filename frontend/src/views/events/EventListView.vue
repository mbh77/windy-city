<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn">지도</router-link>
      <h1 class="page-title">💃 클래스·이벤트</h1>
    </header>

    <main class="page-body">
      <!-- 검색 + 등록 -->
      <div class="board-toolbar">
        <div class="search-input-wrap">
          <input v-model="searchQuery" placeholder="제목, 장소, 강사명 검색..." @input="debouncedSearch" />
          <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''; debouncedSearch()">✕</button>
        </div>
        <router-link v-if="currentUser" to="/events/new" class="btn-primary">등록</router-link>
      </div>

      <!-- 장르 필터 -->
      <div class="compact-filter">
        <div class="compact-filter-summary" @click="showGenreFilter = !showGenreFilter">
          <span>🎵 춤 종류{{ selectedGenres.length ? ` (${selectedGenres.length})` : '' }}</span>
          <span class="date-toggle">{{ showGenreFilter ? '▲' : '▼' }}</span>
        </div>
        <div v-if="showGenreFilter" class="compact-filter-body">
          <div class="filter-row">
            <button
              v-for="g in GENRE_FILTER_OPTIONS"
              :key="g.value"
              :class="['genre-chip', { active: selectedGenres.includes(g.value) }]"
              @click="toggleGenre(g.value)"
            >{{ g.label }}</button>
            <button v-if="selectedGenres.length" class="genre-chip genre-reset" @click="selectedGenres = []; page = 1; loadEvents()">초기화</button>
          </div>
        </div>
      </div>

      <!-- 기간 + 요일 필터 -->
      <div class="compact-filter">
        <div class="compact-filter-summary" @click="showDateFilter = !showDateFilter">
          <span>📅 기간{{ dateFrom || dateTo ? ` ${dateFrom || ''}~${dateTo || ''}` : '' }}</span>
          <span v-if="selectedDays.length" class="filter-days-tag">{{ selectedDays.map(d => DAY_LABELS[d]).join('·') }}</span>
          <span class="date-toggle">{{ showDateFilter ? '▲' : '▼' }}</span>
        </div>
        <div v-if="showDateFilter" class="compact-filter-body">
          <div class="date-filter-inputs">
            <input type="date" v-model="dateFrom" @change="onDateChange" />
            <span>~</span>
            <input type="date" v-model="dateTo" @change="onDateChange" />
            <button class="btn-ghost" @click="resetDateFilter">초기화</button>
          </div>
          <div class="day-filter">
            <button
              v-for="day in DAY_OPTIONS"
              :key="day.value"
              :class="['day-chip', { active: selectedDays.includes(day.value) }]"
              @click="toggleDay(day.value)"
            >{{ day.label }}</button>
          </div>
        </div>
      </div>

      <!-- 목록 -->
      <ul class="event-list">
        <li v-for="event in filteredByDay" :key="event.id" class="event-card" @click="goDetail(event.id)">
          <div class="event-content">
            <img v-if="event.media?.length" class="event-thumb" :src="event.media[0].url" />
            <div class="event-info">
              <div class="event-badges">
                <span :class="['event-type-badge', `type-${event.event_type}`]">{{ TYPE_LABELS[event.event_type] }}</span>
                <span v-for="g in event.dance_genres || []" :key="g" :class="['genre-badge', `genre-${g}`]">{{ GENRE_LABELS[g] }}</span>
                <span class="event-title">{{ event.title }}</span>
              </div>
              <div class="event-detail">
                <span v-if="event.location_name">{{ event.location_name }}</span>
                <span class="event-date">{{ formatEventSchedule(event) }}</span>
              </div>
            </div>
          </div>
          <div class="event-meta">
            <span>{{ event.organizer_nickname }}</span>
            <span>{{ formatCreatedAt(event.created_at) }}</span>
            <span>👁 {{ event.view_count || 0 }}</span>
            <span v-if="event.comment_count > 0">💬 {{ event.comment_count }}</span>
          </div>
        </li>
        <li v-if="filteredByDay.length === 0" class="board-empty">등록된 강습·행사가 없습니다</li>
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
import { apiFetch, formatDate, formatCreatedAt } from '@/utils/api.js'
import { useAuth } from '@/composables/useAuth.js'
import { TYPE_LABELS, GENRE_LABELS, GENRE_OPTIONS } from '@/utils/constants.js'

const router = useRouter()
const { currentUser } = useAuth()

const DAY_LABELS = { mon: '월', tue: '화', wed: '수', thu: '목', fri: '금', sat: '토', sun: '일' }

function formatEventSchedule(ev) {
  const parts = []
  if (ev.event_date) {
    let dateStr = formatDate(ev.event_date)
    if (ev.event_end_date && ev.event_end_date !== ev.event_date) {
      dateStr += ' ~ ' + formatDate(ev.event_end_date)
    }
    parts.push(dateStr)
  }
  if (ev.start_time) {
    parts.push(ev.start_time.slice(0, 5))
  }
  if (ev.is_recurring && ev.recurrence_rule) {
    const freq = ev.recurrence_rule.frequency === 'weekly' ? '매주' : '격주'
    const days = (ev.recurrence_rule.days || []).map(d => DAY_LABELS[d] || d).join('·')
    parts.push(`${freq} ${days}`)
  }
  return parts.join(' · ')
}

const GENRE_FILTER_OPTIONS = GENRE_OPTIONS.filter(g => g.value !== 'other')
const selectedGenres = ref([])
const showGenreFilter = ref(false)
const showDateFilter = ref(false)

function toggleGenre(value) {
  const idx = selectedGenres.value.indexOf(value)
  if (idx >= 0) selectedGenres.value.splice(idx, 1)
  else selectedGenres.value.push(value)
  page.value = 1
  loadEvents()
}

// 날짜 필터
const dateFrom = ref('')
const dateTo = ref('')

function onDateChange() {
  if (dateTo.value && dateFrom.value && dateTo.value < dateFrom.value) dateTo.value = dateFrom.value
  page.value = 1
  loadEvents()
}

function resetDateFilter() {
  dateFrom.value = ''
  dateTo.value = ''
  selectedDays.value = []
  page.value = 1
  loadEvents()
}

// 요일 필터
const DAY_OPTIONS = [
  { value: 'mon', label: '월' }, { value: 'tue', label: '화' }, { value: 'wed', label: '수' },
  { value: 'thu', label: '목' }, { value: 'fri', label: '금' }, { value: 'sat', label: '토' }, { value: 'sun', label: '일' },
]
const WEEKDAY_TO_DAY = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
const selectedDays = ref([])

function toggleDay(day) {
  const idx = selectedDays.value.indexOf(day)
  if (idx >= 0) selectedDays.value.splice(idx, 1)
  else selectedDays.value.push(day)
  // 요일 필터는 클라이언트 사이드이므로 목록 리로드 불필요 (computed에서 처리)
}

function matchesDay(ev) {
  if (selectedDays.value.length === 0) return true
  if (ev.is_recurring && ev.recurrence_rule?.days) {
    return ev.recurrence_rule.days.some(d => selectedDays.value.includes(d))
  }
  if (!ev.event_date) return true
  const weekday = new Date(ev.event_date).getDay()
  const dayKey = WEEKDAY_TO_DAY[weekday === 0 ? 6 : weekday - 1]
  return selectedDays.value.includes(dayKey)
}

const events = ref([])
const filteredByDay = computed(() => events.value.filter(ev => matchesDay(ev)))
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
  for (const g of selectedGenres.value) params.append('dance_genres', g)
  if (dateFrom.value) params.set('date_from', dateFrom.value)
  if (dateTo.value) params.set('date_to', dateTo.value)
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
.board-toolbar { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.board-toolbar .search-input-wrap { flex: 1; position: relative; min-width: 0; }
.board-toolbar input { width: 100%; background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 8px 10px; padding-right: 28px; font-size: 0.85rem; margin-bottom: 0 !important; box-sizing: border-box; }
.board-toolbar .search-clear { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #8B7B6B; font-size: 0.8rem; cursor: pointer; padding: 2px 4px; line-height: 1; }
.board-toolbar .search-clear:hover { color: #D4725C; }
.filter-row { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px; }
.genre-chip { padding: 4px 10px; border-radius: 14px; font-size: 0.7rem; cursor: pointer; border: 1px solid #E0D5C8; background: transparent; color: #5A4A3A; transition: all 0.15s; }
.genre-chip.active { background: #a855f7; color: #fff; border-color: #a855f7; }
.genre-chip:hover { border-color: #8B7B6B; }
.genre-chip.genre-reset { color: #8B7B6B; font-size: 0.65rem; }
.compact-filter { border-bottom: 1px solid #EDE5DB; margin-bottom: 4px; }
.compact-filter-summary { font-size: 0.8rem; color: #5A4A3A; cursor: pointer; display: flex; align-items: center; gap: 6px; padding: 6px 0; }
.compact-filter-body { padding-bottom: 8px; }
.filter-days-tag { font-size: 0.7rem; background: #D4725C22; color: #D4725C; padding: 1px 6px; border-radius: 3px; }
.date-toggle { font-size: 0.6rem; color: #8B7B6B; margin-left: auto; }
.date-filter-inputs { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 6px; }
.date-filter-inputs input[type="date"] { background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 3px; padding: 4px 6px; font-size: 0.7rem; flex: 1; min-width: 0; max-width: 140px; }
.date-filter-inputs .btn-ghost { padding: 4px 6px; font-size: 0.7rem; }
.day-filter { display: flex; gap: 4px; }
.day-chip { flex: 1; padding: 4px 0; border-radius: 4px; font-size: 0.75rem; text-align: center; cursor: pointer; border: 1px solid #E0D5C8; background: transparent; color: #8B7B6B; transition: all 0.15s; }
.day-chip.active { background: #D4725C; color: #fff; border-color: #D4725C; }
.day-chip:hover { border-color: #8B7B6B; }
.board-toolbar .btn-primary { padding: 8px 16px; font-size: 0.85rem; white-space: nowrap; display: inline-flex; align-items: center; justify-content: center; text-decoration: none; box-sizing: border-box; }
.event-list { list-style: none; padding: 0; margin: 0; }
.event-card { padding: 12px 0; border-bottom: 1px solid #EDE5DB; cursor: pointer; }
.event-card:hover { background: #FAFAFA; }
.event-content { display: flex; gap: 12px; margin-bottom: 6px; }
.event-thumb { width: 48px; height: 48px; border-radius: 8px; object-fit: cover; background: #EDE5DB; flex-shrink: 0; }
.event-info { flex: 1; min-width: 0; }
.event-badges { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 4px; }
.event-badges .event-type-badge,
.event-badges .genre-badge { font-size: 0.65rem; }
.event-title { font-size: 0.9rem; font-weight: 600; margin-bottom: 4px; }
.event-detail { font-size: 0.78rem; color: #5A4A3A; display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 4px; }
.event-date { color: #5BA89E; }
.event-meta { font-size: 0.7rem; color: #8B7B6B; display: flex; gap: 10px; }
.board-empty { padding: 40px 0; text-align: center; color: #8B7B6B; font-size: 0.85rem; list-style: none; }
.board-paging { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 16px; }
.board-paging button { background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 4px 12px; font-size: 0.8rem; cursor: pointer; }
.board-paging button:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
