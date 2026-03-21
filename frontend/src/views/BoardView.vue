<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn" title="지도">지도</router-link>
      <h1 class="page-title">{{ categoryLabel }}</h1>
    </header>

    <main class="page-body">
      <!-- 검색 + 글쓰기 -->
      <div class="board-toolbar">
        <input v-model="searchQuery" placeholder="제목 또는 내용 검색..." @input="debouncedSearch" />
        <button v-if="canWrite" class="btn-primary" @click="goWrite">글쓰기</button>
      </div>
      
      <!-- 글 목록 -->
      <ul class="board-list">
        <!-- 고정 공지 -->
        <li v-for="post in pinnedPosts" :key="'pin-'+post.id" class="board-item board-item-pinned" @click="goDetail(post.id)">
          <div class="board-item-title">📌 {{ post.title }}</div>
          <div class="board-item-meta">
            <span>공지</span>
            <span>{{ formatDate(post.created_at) }}</span>
            <span>👁 {{ post.view_count }}</span>
            <span v-if="post.comment_count > 0">💬 {{ post.comment_count }}</span>
          </div>
        </li>
        <!-- 일반 글 -->
        <li v-for="post in posts" :key="post.id" class="board-item" @click="goDetail(post.id)">
          <div class="board-item-title">{{ post.title }}</div>
          <div class="board-item-meta">
            <span>{{ post.author_nickname }}</span>
            <span>{{ formatDate(post.created_at) }}</span>
            <span>👁 {{ post.view_count }}</span>
            <span v-if="post.comment_count > 0">💬 {{ post.comment_count }}</span>
          </div>
        </li>
        <li v-if="posts.length === 0 && pinnedPosts.length === 0" class="board-empty">게시글이 없습니다</li>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiJson } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'

const route = useRoute()
const router = useRouter()
const { currentUser } = useAuth()

const posts = ref([])
const pinnedPosts = ref([])
const total = ref(0)
const page = ref(1)
const limit = 20
const searchQuery = ref('')
let debounceTimer = null

const category = computed(() => route.query.category || 'free')
const categoryLabel = computed(() => category.value === 'notice' ? '📢 공지사항' : '💬 열린 플로어')
const totalPages = computed(() => Math.ceil(total.value / limit))

// 공지사항은 관리자만, 자유게시판은 로그인 사용자
const canWrite = computed(() => {
  if (!currentUser.value) return false
  if (category.value === 'notice') return currentUser.value.is_admin
  return true
})

onMounted(() => loadPosts())

// 카테고리 변경 시 재로드
watch(category, () => {
  page.value = 1
  searchQuery.value = ''
  loadPosts()
})

async function loadPosts() {
  const params = new URLSearchParams({
    category: category.value,
    page: page.value,
    limit,
    q: searchQuery.value,
  })
  const res = await apiJson(`/api/posts/?${params}`)
  const data = await res.json()
  posts.value = data.posts
  pinnedPosts.value = data.pinned || []
  total.value = data.total
}

function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    loadPosts()
  }, 300)
}

function changePage(p) {
  page.value = p
  loadPosts()
}

function goDetail(postId) {
  router.push(`/board/${postId}`)
}

function goWrite() {
  router.push(`/board/write?category=${category.value}`)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

</script>

<style scoped>
.board-toolbar { display: flex; gap: 8px; margin-bottom: 12px; }
.board-toolbar input { flex: 1; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 6px; padding: 8px 10px; font-size: 0.85rem; }
.board-toolbar .btn-primary { padding: 8px 16px; font-size: 0.85rem; white-space: nowrap; }
.board-list { list-style: none; padding: 0; margin: 0; }
.board-item { padding: 12px 0; border-bottom: 1px solid #2a2a2a; cursor: pointer; }
.board-item:hover { background: #222; }
.board-item-pinned { background: #1a1a2e; border-left: 3px solid #ff4d6d; }
.board-item-title { font-size: 0.9rem; margin-bottom: 4px; }
.board-item-meta { font-size: 0.75rem; color: #888; display: flex; gap: 12px; }
.board-empty { padding: 40px 0; text-align: center; color: #888; font-size: 0.85rem; }
.board-paging { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 16px; }
.board-paging button { background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 6px; padding: 4px 12px; font-size: 0.8rem; cursor: pointer; }
.board-paging button:disabled { opacity: 0.4; cursor: not-allowed; }
</style>