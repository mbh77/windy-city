<template>
  <aside :class="['sidebar', { expanded: isExpanded }]">
    <div class="sheet-handle" @click="isExpanded = !isExpanded">
      <span></span>
    </div>
    <!-- 검색창 -->
    <div class="search-box">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="🔍 이벤트, 장소, 강사 이름으로 검색..."
        @keydown.esc="searchQuery = ''"
        @focus="isExpanded = true"
      />
    </div>
    <!-- 검색 모드: 검색어가 있을 때 -->
    <template v-if="searchQuery.trim()">
      <div class="sidebar-header">
        <span>검색 결과 {{ searchResults.length }}건</span>        
      </div>
      <ul class="sidebar-list">
        <li 
          v-for="item in searchResults"
          :key="item.item_type + '-' + item.id"
          @click="handleSearchClick(item)"
        >
          <span v-if="item.item_type === 'event'" :class="['event-type-badge', `type-${item.event_type}`]">
            {{  TYPE_LABELS[item.event_type] }}
          </span>
          <span v-else :class="['venue-type-badge', `vtype-${item.venue_type}`]">
            {{  VENUE_TYPE_LABELS[item.venue_type] }}
          </span>
          <span
            v-for="g in item.dance_genres || []"
            :key="g"
            :class="['genre-badge', `genre-${g}`]"
          >
            {{ GENRE_LABELS[g] }}
          </span>
          <div class="item-title">{{ item.item_type === 'event' ? item.title : item.name }}</div>
          <div class="item-meta">{{ item.item_type === 'event' ? item.location_name : item.address }}</div>
          <div v-if="item.item_type === 'event'" class="item-meta">{{ formatDate(item.start_date) }}</div>
        </li>
        <li v-if="searchResults.length === 0" class="empty-state">
          <div class="empty-icon">🔍</div>
          <div class="empty-title">검색 결과가 없습니다</div>
          <div class="empty-hint">다른 키워드로 검색해보세요</div>
        </li>
      </ul>
    </template>

    <!-- 탐색 모드: 검색어가 없을 때 -->
    <template v-else>
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
        <!-- 날짜 필터 -->
        <div class="date-filter">
          <div class="date-filter-summary" @click="showDatePicker = !showDatePicker">
            📅 {{ formatFilterDate(dateFrom) }} ~ {{ formatFilterDate(dateTo) }}
            <span class="date-toggle">{{ showDatePicker ? '▲' : '▼' }}</span>
          </div>
          <div v-if="showDatePicker" class="date-filter-inputs">
            <input type="date" v-model="dateFrom" />
            <span>~</span>
            <input type="date" v-model="dateTo" />
            <button class="btn-ghost" @click="applyDateFilter">적용</button>
            <button class="btn-ghost" @click="resetDateFilter">초기화</button>
          </div>
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
          <li v-if="visibleEvents.length === 0" class="empty-state">
            <div class="empty-icon">📅</div>
            <div class="empty-title">이 지역에 이벤트가 없어요</div>
            <div class="empty-hint">날짜 범위를 넓히거나 지도를 이동해보세요</div>
            <button v-if="currentUser?.is_organizer" class="btn-primary" @click="$emit('addEvent')">+ 이벤트 등록하기</button>
          </li>
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
          <li v-if="visibleVenues.length === 0" class="empty-state">
            <div class="empty-icon">📍</div>
            <div class="empty-title">이 지역에 등록된 장소가 없어요</div>
            <div class="empty-hint">지도를 이동해서 다른 지역을 탐색해보세요</div>
            <button v-if="currentUser?.is_organizer" class="btn-primary" @click="$emit('addVenue')">+ 장소 등록하기</button>
          </li>          
        </ul>
      </template>      

    </template>
  </aside>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { TYPE_LABELS, GENRE_LABELS, VENUE_TYPE_LABELS } from '../utils/constants.js'
import { apiFetch, formatDate } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'
import { useEvents } from '../composables/useEvents.js'
import { useVenues } from '../composables/useVenues.js'

const emit = defineEmits(['addEvent', 'selectEvent', 'addVenue', 'selectVenue', 'dateFilterChange'])
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

// 날짜 필터
const showDatePicker = ref(false)
const today = new Date().toISOString().slice(0, 10)
const weekLater = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10)
const dateFrom = ref(today)
const dateTo = ref(weekLater)

watch(dateFrom, (val) => {
  if (dateTo.value < val) {
    dateTo.value = val
  }
})

function formatFilterDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function applyDateFilter() {
  emit('dateFilterChange', { date_from: dateFrom.value, date_to: dateTo.value })
  showDatePicker.value = false
}

function resetDateFilter() {
  dateFrom.value = today
  dateTo.value = weekLater
  emit('dateFilterChange', { date_from: today, date_to: weekLater })
  showDatePicker.value = false
}

// 검색 관련
const searchQuery = ref('')
const searchResults = ref([])
let searchTimer = null
const isExpanded = ref(false)

watch(searchQuery, (val) => {
  clearTimeout(searchTimer)
  const q = val.trim()
  
  if (!q) {
    searchResults.value = []
    return
  }

  isExpanded.value = true

  searchTimer = setTimeout(async () => {
    const res = await apiFetch(`/api/search?q=${encodeURIComponent(q)}`)
    if (res.ok) {
      searchResults.value = await res.json()
    }
  }, 300)
})

async function handleSearchClick(item) {
  // 검색 결과는 간소화된 데이터이므로 전체 데이터를 다시 가져옴
  const url = item.item_type === 'event'
    ? `/api/events/${item.id}`
    : `/api/venues/${item.id}`
  const res = await apiFetch(url)
  if (res.ok) {
    const fullData = await res.json()
    if (item.item_type === 'event') {
      emit('selectEvent', fullData)
    } else {
      emit('selectVenue', fullData)
    }
  }
}

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
