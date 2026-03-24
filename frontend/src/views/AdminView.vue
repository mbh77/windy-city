<template>
  <div class="page-container wide">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn" title="지도">지도</router-link>
      <h1 class="page-title">⚙️ 관리자</h1>
    </header>

    <main class="page-body">
      <div class="admin-tabs">
        <button :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">회원</button>
        <button :class="{ active: activeTab === 'events' }" @click="activeTab = 'events'">강습·행사</button>
        <button :class="{ active: activeTab === 'venues' }" @click="activeTab = 'venues'">장소</button>
      </div>

      <!-- 회원 탭 -->
      <div v-if="activeTab === 'users'">
        <h2>회원 관리</h2>
        <div class="admin-search">
          <input v-model="searchQuery" placeholder="이메일 또는 닉네임 검색..." @input="debouncedSearch" />
        </div>
        <p class="admin-total">총 {{ total }}명</p>
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>닉네임</th>
              <th>이메일</th>
              <th>인증</th>
              <th>주최자</th>
              <th>가입일</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.nickname }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.is_verified ? '✅' : '❌' }}</td>
              <td>
                <button
                  :class="['role-btn', { active: user.is_organizer }]"
                  @click="toggleOrganizer(user)"
                >
                  {{ user.is_organizer ? 'ON' : 'OFF' }}
                </button>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <button
                  v-if="!user.is_admin && user.email !== 'ghost@windycity.internal'"
                  class="delete-btn"
                  @click="deleteUser(user)"
                >삭제</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="admin-paging" v-if="totalPages > 1">
          <button :disabled="page <= 1" @click="changePage(page - 1)">◀ 이전</button>
          <span>{{ page }} / {{ totalPages }}</span>
          <button :disabled="page >= totalPages" @click="changePage(page + 1)">다음 ▶</button>
        </div>
      </div>

      <!-- 이벤트 탭 -->
      <div v-if="activeTab === 'events'">
        <h2>강습·행사 관리</h2>
        <div class="admin-search">
          <input v-model="eventSearch" placeholder="제목 또는 장소명 검색..." @input="debouncedEventSearch" />
        </div>
        <p class="admin-total">총 {{ eventTotal }}건</p>
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>제목</th>
              <th>장소</th>
              <th>유형</th>
              <th>시작일</th>
              <th>작성자</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ev in eventList" :key="ev.id">
              <td>{{ ev.id }}</td>
              <td>{{ ev.title }}</td>
              <td>{{ ev.location_name }}</td>
              <td>{{ ev.event_type }}</td>
              <td>{{ formatDate(ev.start_date) }}</td>
              <td>{{ ev.organizer_nickname }}</td>
              <td>
                <button class="delete-btn" @click="deleteEvent(ev)">삭제</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="admin-paging" v-if="eventTotalPages > 1">
          <button :disabled="eventPage <= 1" @click="changeEventPage(eventPage - 1)">◀ 이전</button>
          <span>{{ eventPage }} / {{ eventTotalPages }}</span>
          <button :disabled="eventPage >= eventTotalPages" @click="changeEventPage(eventPage + 1)">다음 ▶</button>
        </div>
      </div>

      <!-- 장소 탭 -->
      <div v-if="activeTab === 'venues'">
        <h2>장소 관리</h2>
        <div class="admin-search">
          <input v-model="venueSearch" placeholder="이름 또는 주소 검색..." @input="debouncedVenueSearch" />
        </div>
        <p class="admin-total">총 {{ venueTotal }}건</p>
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>이름</th>
              <th>유형</th>
              <th>주소</th>
              <th>등록자</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in venueList" :key="v.id">
              <td>{{ v.id }}</td>
              <td>{{ v.name }}</td>
              <td>{{ v.venue_type }}</td>
              <td>{{ v.address }}</td>
              <td>{{ v.owner_nickname }}</td>
              <td>
                <button class="delete-btn" @click="deleteVenue(v)">삭제</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="admin-paging" v-if="venueTotalPages > 1">
          <button :disabled="venuePage <= 1" @click="changeVenuePage(venuePage - 1)">◀ 이전</button>
          <span>{{ venuePage }} / {{ venueTotalPages }}</span>
          <button :disabled="venuePage >= venueTotalPages" @click="changeVenuePage(venuePage + 1)">다음 ▶</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiJson } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'
import { useRouter } from 'vue-router'

const router = useRouter()
const { currentUser } = useAuth()

const activeTab = ref('users')
const limit = 20

// ── 회원 관리 ──
const users = ref([])
const total = ref(0)
const page = ref(1)
const searchQuery = ref('')
let debounceTimer = null
const totalPages = computed(() => Math.ceil(total.value / limit))

async function loadUsers() {
  const params = new URLSearchParams({ page: page.value, limit, q: searchQuery.value })
  const res = await apiJson(`/api/admin/users?${params}`)
  const data = await res.json()
  users.value = data.users
  total.value = data.total
}

function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; loadUsers() }, 300)
}

function changePage(p) { page.value = p; loadUsers() }

async function toggleOrganizer(user) {
  await apiJson(`/api/admin/users/${user.id}`, {
    method: 'PUT',
    body: JSON.stringify({ is_organizer: !user.is_organizer }),
  })
  user.is_organizer = !user.is_organizer
}

async function deleteUser(user) {
  if (!confirm(`${user.nickname} (${user.email}) 계정을 삭제하시겠습니까?`)) return
  try {
    const res = await apiJson(`/api/admin/users/${user.id}`, { method: 'DELETE' })
    if (!res.ok) {
      const data = await res.json()
      alert(data.detail || '삭제에 실패했습니다')
      return
    }
    loadUsers()
  } catch (e) {
    alert('삭제에 실패했습니다')
  }
}

// ── 이벤트 관리 ──
const eventList = ref([])
const eventTotal = ref(0)
const eventPage = ref(1)
const eventSearch = ref('')
let eventDebounce = null
const eventTotalPages = computed(() => Math.ceil(eventTotal.value / limit))

async function loadEvents() {
  const params = new URLSearchParams({ page: eventPage.value, limit, q: eventSearch.value })
  const res = await apiJson(`/api/admin/events?${params}`)
  const data = await res.json()
  eventList.value = data.events
  eventTotal.value = data.total
}

function debouncedEventSearch() {
  clearTimeout(eventDebounce)
  eventDebounce = setTimeout(() => { eventPage.value = 1; loadEvents() }, 300)
}

function changeEventPage(p) { eventPage.value = p; loadEvents() }

async function deleteEvent(ev) {
  if (!confirm(`"${ev.title}" 강습·행사를 삭제하시겠습니까?`)) return
  try {
    const res = await apiJson(`/api/admin/events/${ev.id}`, { method: 'DELETE' })
    if (!res.ok) {
      const data = await res.json()
      alert(data.detail || '삭제에 실패했습니다')
      return
    }
    loadEvents()
  } catch (e) {
    alert('삭제에 실패했습니다')
  }
}

// ── 장소 관리 ──
const venueList = ref([])
const venueTotal = ref(0)
const venuePage = ref(1)
const venueSearch = ref('')
let venueDebounce = null
const venueTotalPages = computed(() => Math.ceil(venueTotal.value / limit))

async function loadVenues() {
  const params = new URLSearchParams({ page: venuePage.value, limit, q: venueSearch.value })
  const res = await apiJson(`/api/admin/venues?${params}`)
  const data = await res.json()
  venueList.value = data.venues
  venueTotal.value = data.total
}

function debouncedVenueSearch() {
  clearTimeout(venueDebounce)
  venueDebounce = setTimeout(() => { venuePage.value = 1; loadVenues() }, 300)
}

function changeVenuePage(p) { venuePage.value = p; loadVenues() }

async function deleteVenue(v) {
  if (!confirm(`"${v.name}" 장소를 삭제하시겠습니까?`)) return
  try {
    const res = await apiJson(`/api/admin/venues/${v.id}`, { method: 'DELETE' })
    if (!res.ok) {
      const data = await res.json()
      alert(data.detail || '삭제에 실패했습니다')
      return
    }
    loadVenues()
  } catch (e) {
    alert('삭제에 실패했습니다')
  }
}

// ── 공통 ──
function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  if (!currentUser.value?.is_admin) {
    router.push('/')
    return
  }
  loadUsers()
  loadEvents()
  loadVenues()
})
</script>

<style scoped>
.admin-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.admin-tabs button { padding: 6px 16px; border: 1px solid #444; background: transparent; color: #888; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.admin-tabs button.active { background: #ff6b6b; border-color: #ff6b6b; color: #fff; }
.page-body h2 { font-size: 1.1rem; margin-bottom: 12px; }
.admin-search { margin-bottom: 12px; }
.admin-search input { width: 100%; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 6px; padding: 8px 10px; font-size: 0.85rem; }
.admin-total { font-size: 0.8rem; color: #888; margin-bottom: 8px; }
.admin-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.admin-table th { text-align: left; padding: 8px; border-bottom: 1px solid #444; color: #aaa; }
.admin-table td { padding: 8px; border-bottom: 1px solid #2a2a2a; }
.role-btn { padding: 2px 10px; border-radius: 10px; border: 1px solid #555; background: transparent; color: #888; font-size: 0.75rem; cursor: pointer; }
.role-btn.active { background: #ff6b6b; border-color: #ff6b6b; color: #fff; }
.admin-paging { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 16px; margin-bottom: 16px; }
.admin-paging button { background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 6px; padding: 4px 12px; font-size: 0.8rem; cursor: pointer; }
.admin-paging button:disabled { opacity: 0.4; cursor: not-allowed; }
.delete-btn { padding: 2px 8px; border-radius: 6px; border: 1px solid #ff4444; background: transparent; color: #ff4444; font-size: 0.7rem; cursor: pointer; }
.delete-btn:hover { background: #ff4444; color: #fff; }
</style>
