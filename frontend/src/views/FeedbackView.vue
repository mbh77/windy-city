<template>
  <div class="feedback-page">
    <header class="feedback-header">
      <router-link to="/" class="feedback-back">← 지도로 돌아가기</router-link>
      <h1 class="feedback-logo">제보 / 제안</h1>
    </header>

    <main class="feedback-content">
      <p class="feedback-desc">바람난 도시에 대한 제보, 제안, 버그 신고 등 자유롭게 보내주세요.</p>

      <form @submit.prevent="submitFeedback">
        <label class="feedback-label">이름 (선택)</label>
        <input v-model="form.name" type="text" placeholder="익명도 가능합니다" />

        <label class="feedback-label">이메일 (선택)</label>
        <input v-model="form.email" type="email" placeholder="답변을 받으실 이메일" />

        <label class="feedback-label">내용 *</label>
        <textarea v-model="form.message" placeholder="제보하실 내용을 입력해주세요" rows="6"></textarea>

        <p v-if="error" class="feedback-error">{{ error }}</p>
        <p v-if="success" class="feedback-success">{{ success }}</p>

        <button type="submit" class="feedback-btn" :disabled="sending">
          {{ sending ? '전송 중...' : '보내기' }}
        </button>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { apiJson } from '../utils/api.js'

const form = reactive({ name: '', email: '', message: '' })
const error = ref('')
const success = ref('')
const sending = ref(false)

async function submitFeedback() {
  error.value = ''
  success.value = ''

  if (!form.message.trim()) {
    error.value = '내용을 입력해주세요'
    return
  }

  sending.value = true
  try {
    await apiJson('/api/feedback/', {
      method: 'POST',
      body: JSON.stringify({
        name: form.name,
        email: form.email,
        message: form.message,
      }),
    })
    success.value = '제보가 전송되었습니다. 감사합니다!'
    form.name = ''
    form.email = ''
    form.message = ''
  } catch (e) {
    error.value = '전송에 실패했습니다. 잠시 후 다시 시도해주세요.'
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.feedback-page { min-height: 100vh; background: #0f0f0f; color: #e0e0e0; padding: 20px; max-width: 720px; margin: 0 auto; }
.feedback-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.feedback-back { color: #aaa; text-decoration: none; font-size: 0.85rem; }
.feedback-back:hover { color: #fff; }
.feedback-logo { font-size: 1.3rem; font-weight: 700; color: #ff6b6b; }
.feedback-content { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 24px; }
.feedback-desc { font-size: 0.85rem; color: #aaa; margin-bottom: 20px; line-height: 1.5; }
.feedback-label { font-size: 0.8rem; color: #999; margin-bottom: 4px; display: block; }
input, textarea { width: 100%; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 6px; padding: 8px 10px; font-size: 0.85rem; margin-bottom: 12px; }
textarea { resize: vertical; font-family: inherit; }
input:focus, textarea:focus { border-color: #ff6b6b; outline: none; }
.feedback-btn { width: 100%; background: #ff6b6b; color: #fff; border: none; border-radius: 6px; padding: 10px; font-size: 0.9rem; font-weight: 600; cursor: pointer; }
.feedback-btn:hover { background: #e05555; }
.feedback-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.feedback-error { color: #ff6b6b; font-size: 0.8rem; margin-bottom: 8px; }
.feedback-success { color: #6bff9d; font-size: 0.8rem; margin-bottom: 8px; }
</style>
