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

      <!-- 댓글 영역 -->
      <div class="comment-section">
        <h3>댓글 {{ post.comments?.length || 0 }}개</h3>

        <!-- 댓글 목록 -->
        <ul class="comment-list">
          <li v-for="c in post.comments" :key="c.id" class="comment-item">
            <div class="comment-header">
              <span class="comment-author">{{ c.author_nickname }}</span>
              <span class="comment-date">{{ formatDate(c.created_at) }}</span>
              <template v-if="canDeleteComment(c)">
                <button v-if="editingCommentId !== c.id" class="comment-edit" @click="startEditComment(c)">수정</button>
                <button class="comment-delete" @click="deleteComment(c.id)">삭제</button>
              </template>
            </div>
            <!-- 수정 모드 -->
            <div v-if="editingCommentId === c.id" class="comment-edit-form">
              <textarea v-model="editCommentText" rows="2"></textarea>
              <div class="comment-edit-actions">
                <button class="btn-ghost" @click="cancelEditComment">취소</button>
                <button class="btn-primary" @click="submitEditComment(c.id)" :disabled="!editCommentText.trim()">저장</button>
              </div>
            </div>
            <!-- 일반 모드 -->
            <div v-else class="comment-body">{{ c.content }}</div>
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
import { apiJson } from '@/utils/api.js'
import { useAuth } from '@/composables/useAuth.js'
import { renderMarkdown } from '@/utils/markdown.js'

const route = useRoute()
const router = useRouter()
const { currentUser } = useAuth()

const post = ref({})
const commentText = ref('')

const editingCommentId = ref(null)
const editCommentText = ref('')

const canEdit = computed(() => {
  if (!currentUser.value || !post.value.id) return false
  return post.value.author_id === currentUser.value.id || currentUser.value.is_admin
})

function startEditComment(c) {
  editingCommentId.value = c.id
  editCommentText.value = c.content
}

function cancelEditComment() {
  editingCommentId.value = null
  editCommentText.value = ''
}

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

async function submitEditComment(commentId) {
  if (!editCommentText.value.trim()) return
  const res = await apiJson(`/api/posts/${post.value.id}/comments/${commentId}`, {
    method: 'PUT',
    body: JSON.stringify({ content: editCommentText.value }),
  })
  if (res.ok) {
    editingCommentId.value = null
    editCommentText.value = ''
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
.comment-section { margin-top: 16px; }
.comment-section h3 { font-size: 0.9rem; margin-bottom: 12px; }
.comment-list { list-style: none; padding: 0; margin: 0 0 12px 0; }
.comment-item { padding: 10px 0; border-bottom: 1px solid #EDE5DB; }
.comment-header { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.comment-author { font-size: 0.8rem; font-weight: 600; }
.comment-date { font-size: 0.7rem; color: #8B7B6B; }
.comment-delete { background: none; border: none; color: #8B7B6B; font-size: 0.7rem; cursor: pointer; margin-left: auto; }
.comment-delete:hover { color: #c0392b; }
.comment-body { font-size: 0.85rem; line-height: 1.5; }
.comment-form { display: flex; gap: 8px; align-items: flex-start; }
.comment-form textarea { flex: 1; background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 8px; font-size: 0.85rem; resize: vertical; font-family: inherit; }
.comment-form .btn-primary { padding: 8px 16px; font-size: 0.8rem; white-space: nowrap; align-self: flex-end; }
.comment-login-msg { font-size: 0.8rem; color: #8B7B6B; }
.comment-edit { background: none; border: none; color: #8B7B6B; font-size: 0.7rem; cursor: pointer; }
.comment-edit:hover { color: #5BA89E; }
.comment-edit-form textarea { width: 100%; background: #FFFFFF; color: #3D3029; border: 1px solid #E0D5C8; border-radius: 6px; padding: 8px; font-size: 0.85rem; resize: vertical; font-family: inherit; margin-top: 4px; }
.comment-edit-actions { display: flex; gap: 6px; justify-content: flex-end; margin-top: 4px; }
.comment-edit-actions button { padding: 4px 12px; font-size: 0.75rem; }
</style>