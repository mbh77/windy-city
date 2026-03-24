<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn" title="지도">지도</router-link>
      <a class="page-nav-btn" @click="goBack">목록</a>
      <h1 class="page-title">{{ editMode ? '글 수정' : '글 작성' }}</h1>
    </header>

    <main class="page-body">
      <p class="write-hint">💡 마크다운 형식을 지원합니다. 미리보기로 작성된 내용을 확인할 수 있습니다.<br>
        <code>**굵게**</code> <code>*기울임*</code> <code>[링크](url)</code> <code>![이미지](url)</code>
      </p>

      <input v-model="form.title" placeholder="제목을 입력하세요" class="write-title" />

      <label v-if="category === 'notice'" class="write-pin-check">
        <input type="checkbox" v-model="form.is_pinned" />
        📌 상단 고정
      </label>

      <div class="write-tabs">
        <button :class="{ active: !previewing }" @click="previewing = false">작성</button>
        <button :class="{ active: previewing }" @click="previewing = true">미리보기</button>
      </div>

      <!-- 글 작성 툴바 -->
      <div class="write-toolbar" v-if="!previewing">
        <button @click="insertBold" title="굵게">B</button>
        <button @click="insertItalic" title="기울임"><em>I</em></button>
        <button @click="insertLink" title="링크">🔗</button>
        <button @click="triggerImageUpload" title="이미지 업로드">📷</button>
        <button @click="showVideoDialog = true" title="영상 URL">▶️</button>
        <input type="file" ref="imageInput" accept="image/*" style="display:none" @change="uploadImage" />
      </div>

      <textarea v-if="!previewing" ref="contentArea" v-model="form.content" placeholder="내용을 입력하세요..." rows="12" class="write-content"></textarea>
      <div v-else class="write-preview markdown-body" v-html="renderMarkdown(form.content)"></div>

      <!-- 영상 URL 입력 다이얼로그 -->
      <div class="dialog-overlay" v-if="showVideoDialog" @click.self="showVideoDialog = false">
        <div class="dialog-box">
          <h4>영상 URL 입력</h4>
          <p class="dialog-hint">YouTube 또는 Instagram 영상 URL을 입력하세요</p>
          <input v-model="videoUrl" placeholder="https://www.youtube.com/watch?v=..." class="dialog-input" @keyup.enter="insertVideo" />
          <div class="dialog-actions">
            <button class="btn-ghost" @click="showVideoDialog = false">취소</button>
            <button class="btn-primary" @click="insertVideo" :disabled="!videoUrl.trim()">삽입</button>
          </div>
        </div>
      </div>      

      <p v-if="error" class="write-error">{{ error }}</p>

      <button class="btn-primary write-submit" @click="submitPost" :disabled="sending">
        {{ sending ? '저장 중...' : (editMode ? '수정하기' : '등록하기') }}
      </button>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiJson } from '@/utils/api.js'
import { useAuth } from '@/composables/useAuth.js'
import { renderMarkdown } from '@/utils/markdown.js'

const route = useRoute()
const router = useRouter()
const { currentUser } = useAuth()

const form = ref({ title: '', content: '', is_pinned: false })
const previewing = ref(false)
const error = ref('')
const sending = ref(false)

const contentArea = ref(null)
const imageInput = ref(null)
const showVideoDialog = ref(false)
const videoUrl = ref('')

const category = computed(() => route.query.category || 'free')
const editId = computed(() => route.query.edit || null)
const editMode = computed(() => !!editId.value)

onMounted(async () => {
  if (!currentUser.value) {
    router.push('/')
    return
  }
  if (category.value === 'notice' && !currentUser.value.is_admin) {
    router.push('/')
    return
  }
  if (editMode.value) {
    const res = await apiJson(`/api/posts/${editId.value}`)
    const data = await res.json()
    form.value.title = data.title
    form.value.content = data.content
    form.value.is_pinned = data.is_pinned || false
  }
})

function goBack() {
  router.push(`/board?category=${category.value}`)
}

async function submitPost() {
  error.value = ''
  if (!form.value.title.trim()) { error.value = '제목을 입력해주세요'; return }
  if (!form.value.content.trim()) { error.value = '내용을 입력해주세요'; return }

  sending.value = true
  try {
    let res
    if (editMode.value) {
      res = await apiJson(`/api/posts/${editId.value}`, {
        method: 'PUT',
        body: JSON.stringify({ title: form.value.title, content: form.value.content, is_pinned: form.value.is_pinned }),
      })
    } else {
      res = await apiJson('/api/posts/', {
        method: 'POST',
        body: JSON.stringify({ category: category.value, title: form.value.title, content: form.value.content, is_pinned: form.value.is_pinned }),
      })
    }
    if (res.ok) {
      const data = await res.json()
      router.push(`/board/${data.id}`)
    } else {
      const d = await res.json()
      error.value = d.detail || '저장에 실패했습니다'
    }
  } catch (e) {
    error.value = '저장에 실패했습니다'
  } finally {
    sending.value = false
  }
}

// 커서 위치에 텍스트 삽입
function insertAtCursor(before, after = '') {
  const ta = contentArea.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const selected = form.value.content.substring(start, end)
  const text = before + (selected || '') + after
  form.value.content = form.value.content.substring(0, start) + text + form.value.content.substring(end)
  // 커서 위치 복원
  const cursorPos = start + before.length + (selected || '').length
  nextTick(() => {
    ta.focus()
    ta.setSelectionRange(cursorPos, cursorPos)
  })
}

function insertBold() { insertAtCursor('**', '**') }
function insertItalic() { insertAtCursor('*', '*') }
function insertLink() { insertAtCursor('[링크 텍스트](', ')') }

function triggerImageUpload() { imageInput.value?.click() }

async function uploadImage(e) {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/upload/image', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData,
    })
    if (res.ok) {
      const data = await res.json()
      insertAtCursor(`![이미지](${data.url})`)
    } else {
      alert('이미지 업로드에 실패했습니다')
    }
  } catch {
    alert('이미지 업로드에 실패했습니다')
  }
  imageInput.value.value = ''
}

function insertVideo() {
  if (!videoUrl.value.trim()) return
  insertAtCursor('\n' + videoUrl.value.trim() + '\n')
  videoUrl.value = ''
  showVideoDialog.value = false
}

</script>

<style scoped>
.write-hint { font-size: 0.75rem; color: #8B7B6B; margin-bottom: 12px; line-height: 1.5; }
.write-hint code { background: #FFFFFF; padding: 1px 4px; border-radius: 3px; font-size: 0.7rem; }
.write-pin-check { display: flex; align-items: center; gap: 6px; font-size: 0.85rem; color: #5A4A3A; margin-bottom: 8px; cursor: pointer; }
.write-pin-check input { accent-color: #D4725C; }
</style>