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
import { apiJson } from '../utils/api.js'
import { useAuth } from '../composables/useAuth.js'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const route = useRoute()
const router = useRouter()
const { currentUser } = useAuth()

const form = ref({ title: '', content: '' })
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

marked.setOptions({ breaks: true })

// YouTube URL → iframe 변환
function embedYouTube(html) {
  // 일반 URL: youtube.com/watch?v=ID
  // 짧은 URL: youtu.be/ID  
  // Shorts: youtube.com/shorts/ID
  const ytRegex = /<a[^>]*href="https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]+)[^"]*"[^>]*>[^<]*<\/a>/g
  html = html.replace(ytRegex, (match, id) => {
    return `<div class="embed-video"><iframe src="https://www.youtube.com/embed/${id}" frameborder="0" allowfullscreen></iframe></div>`
  })

  // <a> 태그 없이 텍스트로 된 URL도 처리
  const ytTextRegex = /(?:<p>)?(https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]+)[^\s<]*)(?:<\/p>)?/g
  html = html.replace(ytTextRegex, (match, url, id) => {
    // 이미 iframe으로 변환된 건 스킵
    if (match.includes('<iframe')) return match
    return `<div class="embed-video"><iframe src="https://www.youtube.com/embed/${id}" frameborder="0" allowfullscreen></iframe></div>`
  })

  return html
}

// Instagram URL → iframe 변환
function embedInstagram(html) {
  // instagram.com/p/CODE/ 또는 /reel/CODE/
  const igRegex = /(?:<a[^>]*href=")?https?:\/\/(?:www\.)?instagram\.com\/(p|reel)\/([a-zA-Z0-9_-]+)\/?[^"<\s]*"?[^<]*(?:<\/a>)?/g
  html = html.replace(igRegex, (match, type, code) => {
    return `<div class="embed-video"><iframe src="https://www.instagram.com/${type}/${code}/embed" frameborder="0" scrolling="no"></iframe></div>`
  })
  return html
}

function renderMarkdown(content) {
  if (!content) return ''
  let html = marked(content)
  html = embedYouTube(html)
  html = embedInstagram(html)
  return DOMPurify.sanitize(html, {
    ADD_TAGS: ['iframe'],
    ADD_ATTR: ['allowfullscreen', 'frameborder', 'src', 'scrolling'],
  })
}

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
        body: JSON.stringify({ title: form.value.title, content: form.value.content }),
      })
    } else {
      res = await apiJson('/api/posts/', {
        method: 'POST',
        body: JSON.stringify({ category: category.value, title: form.value.title, content: form.value.content }),
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
.write-hint { font-size: 0.75rem; color: #888; margin-bottom: 12px; line-height: 1.5; }
.write-hint code { background: #2a2a2a; padding: 1px 4px; border-radius: 3px; font-size: 0.7rem; }
.write-title { width: 100%; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 6px; padding: 10px; font-size: 1rem; margin-bottom: 8px; }
.write-tabs { display: flex; gap: 4px; margin-bottom: 8px; }
.write-tabs button { padding: 4px 12px; border: 1px solid #444; background: transparent; color: #888; border-radius: 6px 6px 0 0; font-size: 0.8rem; cursor: pointer; }
.write-tabs button.active { background: #2a2a2a; color: #e0e0e0; border-bottom-color: #2a2a2a; }
.write-content { width: 100%; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 0 6px 6px 6px; padding: 10px; font-size: 0.9rem; resize: vertical; font-family: inherit; line-height: 1.6; }
.write-preview { background: #2a2a2a; border: 1px solid #444; border-radius: 0 6px 6px 6px; padding: 10px; font-size: 0.9rem; min-height: 200px; line-height: 1.6; }
.write-error { color: #ff6b6b; font-size: 0.8rem; margin-top: 8px; }
.write-submit { width: 100%; margin-top: 12px; padding: 10px; font-size: 0.9rem; }

/* 마크다운 렌더링 스타일 */
.markdown-body :deep(h1) { font-size: 1.3rem; margin: 16px 0 8px; }
.markdown-body :deep(h2) { font-size: 1.15rem; margin: 14px 0 6px; }
.markdown-body :deep(h3) { font-size: 1.05rem; margin: 12px 0 4px; }
.markdown-body :deep(p) { margin: 0 0 8px; }
.markdown-body :deep(a) { color: #6bc1ff; text-decoration: underline; }
.markdown-body :deep(code) { background: #1a1a2e; padding: 1px 5px; border-radius: 3px; font-size: 0.85em; }
.markdown-body :deep(pre) { background: #1a1a2e; padding: 12px; border-radius: 6px; overflow-x: auto; margin: 8px 0; }
.markdown-body :deep(pre code) { background: none; padding: 0; }
.markdown-body :deep(blockquote) { border-left: 3px solid #555; padding-left: 12px; color: #999; margin: 8px 0; }
.markdown-body :deep(ul), .markdown-body :deep(ol) { padding-left: 20px; margin: 8px 0; }
.markdown-body :deep(img) { max-width: 100%; border-radius: 6px; }
.markdown-body :deep(hr) { border: none; border-top: 1px solid #2a2a2a; margin: 16px 0; }

/* 미디어 임베드 */
.markdown-body :deep(.embed-video) { position: relative; width: 100%; padding-bottom: 56.25%; margin: 12px 0; }
.markdown-body :deep(.embed-video iframe) { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 8px; }

/* 글 작성 툴바 */
.write-toolbar { display: flex; gap: 4px; margin-bottom: 4px; }
.write-toolbar button { padding: 4px 10px; background: #2a2a2a; border: 1px solid #444; color: #ccc; border-radius: 4px; font-size: 0.8rem; cursor: pointer; }
.write-toolbar button:hover { background: #3a3a4a; color: #fff; }

/* 영상 URL 다이얼로그 */
.dialog-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog-box { background: #1e1e2e; border: 1px solid #444; border-radius: 10px; padding: 20px; width: 90%; max-width: 400px; }
.dialog-box h4 { margin: 0 0 8px; font-size: 1rem; }
.dialog-hint { font-size: 0.75rem; color: #888; margin-bottom: 12px; }
.dialog-input { width: 100%; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 6px; padding: 8px; font-size: 0.85rem; margin-bottom: 12px; }
.dialog-actions { display: flex; gap: 8px; justify-content: flex-end; }
</style>