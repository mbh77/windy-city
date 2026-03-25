<template>
  <div class="comment-section">
    <h3>댓글 {{ comments.length }}개</h3>

    <!-- 댓글 목록 -->
    <ul class="comment-list">
      <li v-for="c in comments" :key="c.id" class="comment-item">
        <div class="comment-header">
          <span class="comment-author">{{ c.author_nickname }}</span>
          <span class="comment-date">{{ formatDate(c.created_at) }}</span>
          <template v-if="canEdit(c)">
            <button v-if="editingId !== c.id" class="comment-edit" @click="startEdit(c)">수정</button>
            <button class="comment-delete" @click="remove(c.id)">삭제</button>
          </template>
        </div>
        <!-- 수정 모드 -->
        <div v-if="editingId === c.id" class="comment-edit-form">
          <textarea v-model="editText" rows="2"></textarea>
          <div class="comment-edit-actions">
            <button class="btn-ghost" @click="cancelEdit">취소</button>
            <button class="btn-primary" @click="submitEdit(c.id)" :disabled="!editText.trim()">저장</button>
          </div>
        </div>
        <!-- 일반 모드 -->
        <div v-else class="comment-body">{{ c.content }}</div>
      </li>
    </ul>

    <!-- 댓글 입력 -->
    <div class="comment-form" v-if="currentUser">
      <textarea v-model="newText" placeholder="댓글을 입력하세요..." rows="2"></textarea>
      <button class="btn-primary" @click="submit" :disabled="!newText.trim()">등록</button>
    </div>
    <p v-else class="comment-login-msg">댓글을 작성하려면 로그인하세요.</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { apiJson } from '@/utils/api.js'
import { useAuth } from '@/composables/useAuth.js'

const props = defineProps({
  apiBase: { type: String, required: true },  // 예: "/api/events/33"
})

const { currentUser } = useAuth()
const comments = ref([])
const newText = ref('')
const editingId = ref(null)
const editText = ref('')

async function load() {
  const res = await apiJson(`${props.apiBase}/comments`)
  if (res.ok) comments.value = await res.json()
}

function canEdit(c) {
  if (!currentUser.value) return false
  return c.author_id === currentUser.value.id || currentUser.value.is_admin
}

function startEdit(c) {
  editingId.value = c.id
  editText.value = c.content
}

function cancelEdit() {
  editingId.value = null
  editText.value = ''
}

async function submit() {
  if (!newText.value.trim()) return
  const res = await apiJson(`${props.apiBase}/comments`, {
    method: 'POST',
    body: JSON.stringify({ content: newText.value }),
  })
  if (res.ok) {
    newText.value = ''
    load()
  }
}

async function submitEdit(commentId) {
  if (!editText.value.trim()) return
  const res = await apiJson(`${props.apiBase}/comments/${commentId}`, {
    method: 'PUT',
    body: JSON.stringify({ content: editText.value }),
  })
  if (res.ok) {
    editingId.value = null
    editText.value = ''
    load()
  }
}

async function remove(commentId) {
  if (!confirm('댓글을 삭제하시겠습니까?')) return
  await apiJson(`${props.apiBase}/comments/${commentId}`, { method: 'DELETE' })
  load()
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(() => load())
watch(() => props.apiBase, () => load())
</script>
