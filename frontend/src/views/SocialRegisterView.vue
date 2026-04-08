<template>
  <div class="page-container" style="display:flex;align-items:center;justify-content:center;min-height:60vh;">
    <div class="social-register-card">
      <h2>닉네임 설정</h2>
      <p class="social-register-desc">
        {{ providerLabel }} 계정으로 처음 로그인합니다.<br/>사용할 닉네임을 입력해 주세요.
      </p>

      <form @submit.prevent="handleRegister">
        <div style="position:relative;">
          <input v-model="nickname" type="text" placeholder="닉네임" required @blur="checkNickname" />
          <p v-if="nicknameMsg" class="form-error" :style="{ color: nicknameAvailable ? '#5BA89E' : '' }">{{ nicknameMsg }}</p>
        </div>
        <button type="submit" class="btn-primary w100" :class="{ 'btn-loading': loading }" :disabled="loading">
          <span class="btn-text">가입 완료</span>
        </button>
        <p v-if="error" class="form-error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import { apiFetch } from '../utils/api.js'

const route = useRoute()
const router = useRouter()
const { socialRegister } = useAuth()

const provider = ref('')
const providerId = ref('')
const email = ref('')
const nickname = ref('')
const nicknameMsg = ref('')
const nicknameAvailable = ref(false)
const error = ref('')
const loading = ref(false)

const providerLabel = computed(() => {
  if (provider.value === 'kakao') return '카카오'
  if (provider.value === 'naver') return '네이버'
  return ''
})

onMounted(() => {
  provider.value = route.query.provider || ''
  providerId.value = route.query.provider_id || ''
  email.value = route.query.email || ''
  nickname.value = route.query.nickname || ''

  if (!provider.value || !providerId.value) {
    router.push('/')
  }
})

async function checkNickname() {
  const nick = nickname.value.trim()
  nicknameMsg.value = ''
  nicknameAvailable.value = false
  if (!nick) return
  try {
    const res = await apiFetch(`/api/auth/check-nickname?nickname=${encodeURIComponent(nick)}`)
    const data = await res.json()
    nicknameMsg.value = data.message
    nicknameAvailable.value = data.available
  } catch {
    nicknameMsg.value = ''
  }
}

async function handleRegister() {
  error.value = ''
  await checkNickname()
  if (nicknameMsg.value && !nicknameAvailable.value) {
    error.value = nicknameMsg.value
    return
  }
  loading.value = true
  try {
    const result = await socialRegister(provider.value, providerId.value, email.value, nickname.value.trim())
    if (result.ok) {
      router.push('/')
    } else {
      error.value = result.error
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.social-register-card {
  background: #fff;
  border: 1px solid #E0D5C8;
  border-radius: 12px;
  padding: 32px 28px;
  max-width: 400px;
  width: 100%;
}
.social-register-card h2 {
  font-size: 1.1rem;
  color: #3D3029;
  margin-bottom: 8px;
}
.social-register-desc {
  font-size: 0.85rem;
  color: #8B7B6B;
  line-height: 1.5;
  margin-bottom: 20px;
}
</style>
