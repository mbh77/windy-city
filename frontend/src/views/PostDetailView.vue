<template>
  <div class="board-page">
    <header class="board-header">
      <a class="board-back" @click="goBack">← 목록으로</a>
      <h1 class="board-logo">{{ post.category === 'notice' ? '📢 공지사항' : '💬 열린 플로어' }}</h1>
    </header>
    
    <main class="board-content" v-if="post.id">
      <!-- 글 헤더 -->
      <h2 class="post-title">{{ post.title }}</h2>
      <div class="post-meta">
        <span>{{ post.author_nickname }}</span>
        <span>{{ formatDate(post.created_at) }}</span>
      </div>

      <!-- 글 내용 -->
      <div class="post-body" style="white-space: pre-wrap;">{{ post.content }}</div>

      <!-- 수정/삭제 (본인 또는 관리자) -->
      <div class="post-actions" v-if="canEdit">
        <button class="btn-ghost" @click="goEdit">수정</button>
        <button class="btn-danger" @click="deletePost">삭제</button>
      </div>

      <!-- 댓글 영역 -->
      <div class="comment-section">
         <h3>댓글 {{ post.comments?.length || 0 }}개</h3>

        <!-- 댓글 목록 -->
        <ul class="comment-list">
          <li v-for="c in post.comments" :key="c.id" class="comment-item">
            <div class="comment-header">
              <span class="comment-author">{{ c.author_nickname }}</span>
              <span class="comment-date">{{ formatDate(c.created_at) }}</span>
              <button v-if="canDeleteComment(c)" class="comment-delete" @click="deleteComment(c.id)">삭제</button>
            </div>
            <div class="comment-body">{{ c.content }}</div>
          </li>
        </ul>
        
        <!-- 댓글 입력 -->
        <div class="comment-form" v-if="currentUser">
          <textarea v-model="commentText" placeholder="댓글을 입력하세요..." rows="2"></textarea>
          <button class="btn-primary" @click="submitComment" :disabled="!commentText.trim()">등록</button>
        </div>        
        <p v-else class="comment-login-msg">댓글을 작성하려면 로그인하세요.</p>

      </div>

    </main>
  </div>

</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiJson } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'

const route = useRoute()
const router = useRouter()
const { currentUser } = useAuth()

const post = ref({})
const commentText = ref('')

const canEdit = computed(() => {
  if (!currentUser.value || !post.value.id) return false
  return post.value.author_id === currentUser.value.id || currentUser.value.is_admin
})

function canDeleteComment(c) {
  if (!currentUser.value) return false
  return c.author_id === currentUser.value.id || currentUser.value.is_admin
}

onMounted(() => loadPost())

async function loadPost() {
  const res = await apiJson(`/api/posts/${route.params.id}`)
  post.value = await res.json()
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

async function submitComment() {
  if (!commentText.value.trim()) return
  const res = await apiJson(`/api/posts/${post.value.id}/comments`, {
    method: 'POST',
    body: JSON.stringify({ content: commentText.value }),
  })
  if (res.ok) {
    commentText.value = ''
    loadPost()
  }
}

async function deleteComment(commentId) {
  if (!confirm('댓글을 삭제하시겠습니까?')) return
  await apiJson(`/api/posts/${post.value.id}/comments/${commentId}`, { method: 'DELETE' })
  loadPost()
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

</script>

<style scoped>
.board-page { min-height: 100vh; background: #0f0f0f; color: #e0e0e0; padding: 20px; max-width: 720px; margin: 0 auto; }
.board-header { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.board-back { color: #aaa; font-size: 0.85rem; cursor: pointer; }
.board-back:hover { color: #fff; }
.board-logo { font-size: 1.2rem; font-weight: 700; }
.board-content { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 20px; }
.post-title { font-size: 1.2rem; margin-bottom: 8px; }
.post-meta { font-size: 0.8rem; color: #888; display: flex; gap: 12px; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #2a2a2a; }
.post-body { font-size: 0.9rem; line-height: 1.6; min-height: 100px; margin-bottom: 16px; }
.post-actions { display: flex; gap: 8px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #2a2a2a; }
.btn-ghost { padding: 6px 14px; background: transparent; border: 1px solid #555; color: #ccc; border-radius: 6px; font-size: 0.8rem; cursor: pointer; }
.btn-danger { padding: 6px 14px; background: #dc3545; border: none; color: #fff; border-radius: 6px; font-size: 0.8rem; cursor: pointer; }
.comment-section { margin-top: 16px; }
.comment-section h3 { font-size: 0.9rem; margin-bottom: 12px; }
.comment-list { list-style: none; padding: 0; margin: 0 0 12px 0; }
.comment-item { padding: 10px 0; border-bottom: 1px solid #2a2a2a; }
.comment-header { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.comment-author { font-size: 0.8rem; font-weight: 600; }
.comment-date { font-size: 0.7rem; color: #888; }
.comment-delete { background: none; border: none; color: #888; font-size: 0.7rem; cursor: pointer; margin-left: auto; }
.comment-delete:hover { color: #dc3545; }
.comment-body { font-size: 0.85rem; line-height: 1.5; }
.comment-form { display: flex; gap: 8px; align-items: flex-start; }
.comment-form textarea { flex: 1; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 6px; padding: 8px; font-size: 0.85rem; resize: vertical; font-family: inherit; }
.comment-form .btn-primary { padding: 8px 16px; font-size: 0.8rem; white-space: nowrap; align-self: flex-end; }
.comment-login-msg { font-size: 0.8rem; color: #888; }
</style>