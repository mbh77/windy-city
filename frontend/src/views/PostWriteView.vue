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

      <textarea v-if="!previewing" v-model="form.content" placeholder="내용을 입력하세요..." rows="12" class="write-content"></textarea>
      <div v-else class="write-preview" style="white-space: pre-wrap;">{{ form.content }}</div>

      <p v-if="error" class="write-error">{{ error }}</p>

      <button class="btn-primary write-submit" @click="submitPost" :disabled="sending">
        {{ sending ? '저장 중...' : (editMode ? '수정하기' : '등록하기') }}
      </button>
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

const form = ref({ title: '', content: '' })
const previewing = ref(false)
const error = ref('')
const sending = ref(false)

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
</style>