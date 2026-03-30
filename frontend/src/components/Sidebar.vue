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
        placeholder="🔍 클래스, 댄스바, 강사, DJ 등으로 검색"
        @keydown.esc="searchQuery = ''"
        @focus="isExpanded = true"
      />
      <button
        :class="['search-bounds-btn', { active: searchInBounds }]"
        @click="searchInBounds = !searchInBounds">
        📍 지도 내
      </button>
    </div>
    <!-- 검색 모드: 검색어가 있을 때 -->
    <template v-if="searchQuery.trim()">
      <div class="sidebar-header">
        <span>검색 결과 {{ filteredSearchResults.length }}건</span>
      </div>
      <ul class="sidebar-list">
        <li
          v-for="item in filteredSearchResults"
          :key="item.item_type + '-' + item.id"
          class="card-with-thumb"
          @click="handleSearchClick(item)"
        >
          <img :src="item.media?.[0]?.url || (item.item_type === 'event' ? markerEventImg : (venueDefaultImg[item.venue_type] || markerClubImg))" class="card-thumb" />
          <div class="card-info">
            <div class="card-line1">
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
              <span class="item-title">{{ item.item_type === 'event' ? item.title : item.name }}</span>
            </div>
            <div class="card-line2">
              <span class="item-meta">{{ item.item_type === 'event' ? item.location_name : item.address }}</span>
              <template v-if="item.item_type === 'event'">
                <span class="card-dot">·</span>
                <span class="item-meta">{{ formatEventSchedule(item) }}</span>
              </template>
            </div>
          </div>
        </li>
        <li v-if="filteredSearchResults.length === 0" class="empty-state">
          <div class="empty-icon">🔍</div>
          <div class="empty-title">검색 결과가 없습니다</div>
          <div class="empty-hint">다른 키워드로 검색해보세요</div>
        </li>
      </ul>
    </template>

    <!-- 탐색 모드: 검색어가 없을 때 -->
    <template v-else>
      <!-- 탭 + 등록 버튼 -->
      <div class="tab-group">
        <button :class="['tab', { active: activeTab === 'events' }]" @click="activeTab = 'events'">
          강습·행사 {{ filteredEvents.length }}
        </button>
        <button :class="['tab', { active: activeTab === 'venues' }]" @click="activeTab = 'venues'">
          장소 {{ visibleVenues.length }}
        </button>
        <router-link to="/events/new"
          v-if="currentUser?.is_organizer && activeTab === 'events'"
          class="btn-primary tab-action"
        >등록 +</router-link>
        <router-link to="/venues/new"
          v-if="currentUser?.is_organizer && activeTab === 'venues'"
          class="btn-primary tab-action"
        >등록 +</router-link>
      </div>

      <!-- 이벤트 탭 -->
      <template v-if="activeTab === 'events'">
        <!-- 날짜+요일 필터 (접이식) -->
        <div class="compact-filter">
          <div class="compact-filter-summary" @click="showFilter = !showFilter">
            <span>📅 {{ formatFilterDate(dateFrom) }}~{{ formatFilterDate(dateTo) }}</span>
            <span v-if="selectedDays.length" class="filter-days-tag">{{ selectedDays.map(d => DAY_LABELS[d]).join('·') }}</span>
            <span class="date-toggle">{{ showFilter ? '▲' : '▼' }}</span>
          </div>
          <div v-if="showFilter" class="compact-filter-body">
            <div class="date-filter-inputs">
              <input type="date" v-model="dateFrom" />
              <span>~</span>
              <input type="date" v-model="dateTo" />
              <button class="btn-ghost" @click="applyDateFilter">적용</button>
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
        <ul class="sidebar-list">
          <li v-for="ev in filteredEvents" :key="ev.id" class="card-item card-with-thumb" @click="$emit('selectEvent', ev)">
            <img :src="ev.media?.[0]?.url || markerEventImg" class="card-thumb" />
            <div class="card-info">
              <div class="card-line1">
                <span :class="['event-type-badge', `type-${ev.event_type}`]">{{ TYPE_LABELS[ev.event_type] }}</span>
                <span
                  v-for="g in ev.dance_genres || []"
                  :key="g"
                  :class="['genre-badge', `genre-${g}`]"
                >{{ GENRE_LABELS[g] }}</span>
                <span class="item-title">{{ ev.title }}</span>
              </div>
              <div class="card-line2">
                <span class="item-meta">{{ ev.location_name }}</span>
                <span class="card-dot">·</span>
                <span class="item-meta">{{ formatEventSchedule(ev) }}</span>
              </div>
            </div>
          </li>
          <li v-if="filteredEvents.length === 0" class="empty-state">
            <div class="empty-icon">📅</div>
            <div class="empty-title">이 지역에 강습·행사가 없어요</div>
            <div class="empty-hint">날짜 범위를 넓히거나 지도를 이동해보세요</div>
            <router-link to="/events/new"
              v-if="currentUser?.is_organizer && activeTab === 'events'"
              class="btn-primary tab-action">+ 강습·행사 등록하기</router-link>
          </li>
        </ul>
      </template>    

      <!-- 장소 탭 -->
      <template v-if="activeTab === 'venues'">
        <ul class="sidebar-list">
          <li v-for="v in visibleVenues" :key="v.id" class="card-item card-with-thumb" @click="$emit('selectVenue', v)">
            <img :src="v.media?.[0]?.url || venueDefaultImg[v.venue_type] || markerClubImg" class="card-thumb" />
            <div class="card-info">
              <div class="card-line1">
                <span :class="['venue-type-badge', `vtype-${v.venue_type}`]">{{ VENUE_TYPE_LABELS[v.venue_type] }}</span>
                <span
                  v-for="g in v.dance_genres || []"
                  :key="g"
                  :class="['genre-badge', `genre-${g}`]"
                >{{ GENRE_LABELS[g] }}</span>
                <span class="item-title">{{ v.name }}</span>
              </div>
              <div class="card-line2">
                <span v-if="v.address" class="item-meta">{{ v.address }}</span>
              </div>
            </div>
          </li>
          <li v-if="visibleVenues.length === 0" class="empty-state">
            <div class="empty-icon">📍</div>
            <div class="empty-title">이 지역에 등록된 장소가 없어요</div>
            <div class="empty-hint">지도를 이동해서 다른 지역을 탐색해보세요</div>
              <router-link to="/venues/new"
              v-if="currentUser?.is_organizer && activeTab === 'venues'"
              class="btn-primary tab-action">+ 장소 등록하기</router-link>
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
import markerClubImg from '@/assets/maker_club.png'
import markerSchoolImg from '@/assets/maker_shcool.png'
import markerPracticeImg from '@/assets/maker_practice.png'
import markerEventImg from '@/assets/maker_event.png'

const venueDefaultImg = { club: markerClubImg, academy: markerSchoolImg, practice_room: markerPracticeImg }

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
const showFilter = ref(false)
const today = new Date().toISOString().slice(0, 10)
const weekLater = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10)
const dateFrom = ref(today)
const dateTo = ref(weekLater)

const searchInBounds = ref(false)

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
  showFilter.value = false
}

function resetDateFilter() {
  dateFrom.value = today
  dateTo.value = weekLater
  selectedDays.value = []
  emit('dateFilterChange', { date_from: today, date_to: weekLater })
  showFilter.value = false
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

// 반복 이벤트 표시
const DAY_LABELS = { mon: '월', tue: '화', wed: '수', thu: '목', fri: '금', sat: '토', sun: '일' }
const WEEKDAY_TO_DAY = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
const DAY_OPTIONS = [
  { value: 'mon', label: '월' },
  { value: 'tue', label: '화' },
  { value: 'wed', label: '수' },
  { value: 'thu', label: '목' },
  { value: 'fri', label: '금' },
  { value: 'sat', label: '토' },
  { value: 'sun', label: '일' },
]

// 요일 필터
const selectedDays = ref([])

function toggleDay(day) {
  const idx = selectedDays.value.indexOf(day)
  if (idx >= 0) {
    selectedDays.value.splice(idx, 1)
  } else {
    selectedDays.value.push(day)
  }
}

function matchesDay(ev) {
  if (selectedDays.value.length === 0) return true
  if (ev.is_recurring && ev.recurrence_rule?.days) {
    return ev.recurrence_rule.days.some(d => selectedDays.value.includes(d))
  }
  // 비반복: event_date 요일 확인
  const weekday = new Date(ev.event_date).getDay()
  const dayKey = WEEKDAY_TO_DAY[weekday === 0 ? 6 : weekday - 1]
  return selectedDays.value.includes(dayKey)
}

function formatRecurring(rule) {
  if (!rule) return '반복'
  const freq = rule.frequency === 'weekly' ? '매주' : '격주'
  const days = (rule.days || []).map(d => DAY_LABELS[d] || d).join('·')
  return `${freq} ${days}`
}

function formatEventSchedule(ev) {
  const parts = []
  // 날짜
  if (ev.event_date) {
    let dateStr = formatDate(ev.event_date)
    if (ev.event_end_date && ev.event_end_date !== ev.event_date) {
      dateStr += ' ~ ' + formatDate(ev.event_end_date)
    }
    parts.push(dateStr)
  }
  // 시간
  if (ev.start_time) {
    parts.push(ev.start_time.slice(0, 5))
  }
  // 반복
  if (ev.is_recurring && ev.recurrence_rule) {
    parts.push(formatRecurring(ev.recurrence_rule))
  }
  return parts.join(' · ')
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

const filteredEvents = computed(() =>
  visibleEvents.value.filter(ev => matchesDay(ev))
)

const visibleVenues = computed(() =>
  venues.value.filter(v =>
    props.visibleCategories[v.venue_type] && inBounds(v.latitude, v.longitude)
  )
)

const filteredSearchResults = computed(() => {
  if (!searchInBounds.value || !props.mapBounds) return searchResults.value
  return searchResults.value.filter(item => {
    const lat = item.latitude
    const lng = item.longitude
    return lat >= props.mapBounds.swLat && lat <= props.mapBounds.neLat
        && lng >= props.mapBounds.swLng && lng <= props.mapBounds.neLng
  })
})

</script>
