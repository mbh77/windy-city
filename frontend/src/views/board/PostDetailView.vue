<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn" title="지도">지도</router-link>
      <a class="page-nav-btn" @click="goBack">목록</a>
      <h1 class="page-title">{{ post.category === 'notice' ? '📢 공지사항' : '💬 열린 플로어' }}</h1>
    </header>

    <main class="page-body" v-if="post.id">
      <!-- 글 헤더 -->
      <h2 class="post-title">{{ post.title }}</h2>
      <div class="post-meta">
        <span>{{ post.author_nickname }}</span>
        <span>{{ formatDate(post.created_at) }}</span>
        <span>조회 {{ post.view_count }}</span>
      </div>

      <!-- 글 내용 -->
      <div class="post-body markdown-body" v-html="renderMarkdown(post.content)" ></div>

      <!-- 수정/삭제 (본인 또는 관리자) -->
      <div class="post-actions" v-if="canEdit">
        <button class="btn-ghost" @click="goEdit">수정</button>
        <button class="btn-danger" @click="deletePost">삭제</button>
      </div>

      <!-- 댓글 -->
      <CommentSection :apiBase="`/api/posts/${post.id}`" />

    </main>
  </div>

</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiJson } from '@/utils/api.js'
import { useAuth } from '@/composables/useAuth.js'
import { renderMarkdown } from '@/utils/markdown.js'
import CommentSection from '@/components/CommentSection.vue'

const route = useRoute()
const router = useRouter()
const { currentUser } = useAuth()

const post = ref({})

const canEdit = computed(() => {
  if (!currentUser.value || !post.value.id) return false
  return post.value.author_id === currentUser.value.id || currentUser.value.is_admin
})

onMounted(() => loadPost())

async function loadPost() {
  const viewedKey = `viewed_post_${route.params.id}`
  const noCount = localStorage.getItem(viewedKey) ? 'true' : 'false'

  const res = await apiJson(`/api/posts/${route.params.id}?no_count=${noCount}`)
  if (res.ok) {
    post.value = await res.json()
    localStorage.setItem(viewedKey, 'true')
  }
}

function goBack() {
  router.push(`/board?category=${post.value.category || 'free'}`)
}

function goEdit() {
  router.push(`/board/write?category=${post.value.category}&edit=${post.value.id}`)
}

async function deletePost() {
  if (!confirm('이 글을 삭제하시겠습니까?')) return
  await apiJson(`/api/posts/${post.value.id}`, { method: 'DELETE' })
  goBack()
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

</script>

