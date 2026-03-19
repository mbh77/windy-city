<template>
  <div class="admin-page">
    <header class="admin-header">
      <router-link to="/" class="admin-back">← 지도로 돌아가기</router-link>
      <h1 class="admin-logo">⚙️ 관리자</h1>
    </header>

    <main class="admin-content">
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
                v-if="!user.is_admin"
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

const users = ref([])
const total = ref(0)
const page = ref(1)
const limit = 20
const searchQuery = ref('')
let debounceTimer = null

const totalPages = computed(() => Math.ceil(total.value / limit))

onMounted(() => {
  if (!currentUser.value?.is_admin) {
    router.push('/')
    return
  }
  loadUsers()
})

async function loadUsers() {
  const params = new URLSearchParams({ page: page.value, limit, q: searchQuery.value })
  const res = await apiJson(`/api/admin/users?${params}`)
  const data = await res.json()
  users.value = data.users
  total.value = data.total
}

function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    loadUsers()
  }, 300)
}

function changePage(p) {
  page.value = p
  loadUsers()
}

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

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
</script>

<style scoped>
.admin-page { min-height: 100vh; background: #0f0f0f; color: #e0e0e0; padding: 20px; max-width: 900px; margin: 0 auto; }
.admin-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.admin-back { color: #aaa; font-size: 0.85rem; }
.admin-back:hover { color: #fff; }
.admin-logo { font-size: 1.3rem; font-weight: 700; }
.admin-content h2 { font-size: 1.1rem; margin-bottom: 12px; }
.admin-search { margin-bottom: 12px; }
.admin-search input { width: 100%; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 6px; padding: 8px 10px; font-size: 0.85rem; }
.admin-total { font-size: 0.8rem; color: #888; margin-bottom: 8px; }
.admin-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.admin-table th { text-align: left; padding: 8px; border-bottom: 1px solid #444; color: #aaa; }
.admin-table td { padding: 8px; border-bottom: 1px solid #2a2a2a; }
.admin-content { max-height: 80vh; overflow-y: auto; }
.role-btn { padding: 2px 10px; border-radius: 10px; border: 1px solid #555; background: transparent; color: #888; font-size: 0.75rem; cursor: pointer; }
.role-btn.active { background: #ff6b6b; border-color: #ff6b6b; color: #fff; }
.admin-paging { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 16px; }
.admin-paging button { background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 6px; padding: 4px 12px; font-size: 0.8rem; cursor: pointer; }
.admin-paging button:disabled { opacity: 0.4; cursor: not-allowed; }
.delete-btn { padding: 2px 8px; border-radius: 6px; border: 1px solid #ff4444; background: transparent; color: #ff4444; font-size: 0.7rem; cursor: pointer; }
.delete-btn:hover { background: #ff4444; color: #fff; }
</style>
