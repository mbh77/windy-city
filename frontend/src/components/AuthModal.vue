<template>
  <div v-if="visible" class="modal modal-sm" @click.self="handleClose">
    <div class="modal-content">
      <button class="modal-close" @click="handleClose">✕</button>

      <!-- 탭 -->
      <div v-if="mode !== 'verify'" class="tab-group">
        <button :class="['tab', { active: mode === 'login' }]" @click="mode = 'login'">로그인</button>
        <button :class="['tab', { active: mode === 'register' }]" @click="mode = 'register'">회원가입</button>
      </div>

      <!-- 로그인 폼 -->
      <form v-if="mode === 'login'" @submit.prevent="handleLogin">
        <input v-model="loginEmail" type="email" placeholder="이메일" required />
        <input v-model="loginPassword" type="password" placeholder="비밀번호" required />
        <button type="submit" class="btn-primary w100" :class="{ 'btn-loading': loginLoading }" :disabled="loginLoading">
          <span class="btn-text">로그인</span>
        </button>
        <p class="form-error">{{ loginError }}</p>
      </form>

      <!-- 회원가입 폼 -->
      <form v-if="mode === 'register'" @submit.prevent="handleRegister">
        <input v-model="regEmail" type="email" placeholder="이메일" required />
        <input v-model="regPassword" type="password" placeholder="비밀번호" required />
        <div style="position:relative;">
          <input v-model="regNickname" type="text" placeholder="닉네임" required @blur="checkNickname" />
          <p v-if="nicknameMsg" class="form-error" :style="{ color: nicknameAvailable ? '#5BA89E' : '' }">{{ nicknameMsg }}</p>
        </div>
        <!-- 주최자 권한은 관리자가 부여 (회원가입 시 비활성) -->
        <!-- <label class="checkbox-label">
          <input v-model="regIsOrganizer" type="checkbox" />
          강습·행사 주최자로 가입
        </label> -->
        <button type="submit" class="btn-primary w100" :class="{ 'btn-loading': regLoading }" :disabled="regLoading">
          <span class="btn-text">가입하기</span>
        </button>
        <p class="form-error">{{ regError }}</p>
      </form>

      <!-- 이메일 인증 -->
      <div v-if="mode === 'verify'">
        <h2>이메일 인증</h2>
        <p style="color:#999;font-size:0.85rem;margin-bottom:12px">{{ pendingEmail }} 으로 인증 코드가 발송되었습니다</p>
        <input v-model="verifyCode" type="text" placeholder="6자리 인증 코드" maxlength="6" />
        <button class="btn-primary w100" :class="{ 'btn-loading': verifyLoading }" :disabled="verifyLoading" @click="handleVerify">
          <span class="btn-text">인증 확인</span>
        </button>
        <button class="btn-ghost w100" :class="{ 'btn-loading': resendLoading }" :disabled="resendLoading" @click="handleResend" style="margin-top:8px">
          <span class="btn-text">코드 재발송</span>
        </button>
        <p class="form-error" :style="{ color: resendSuccess ? '#6bff9d' : '' }">{{ verifyError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAuth } from '../composables/useAuth.js'
import { apiFetch } from '../utils/api.js'

const props = defineProps({
  visible: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])
const { login, register, verifyEmail, resendCode } = useAuth()

// 모드: login | register | verify
const mode = ref('login')

// 로그인
const loginEmail = ref('')
const loginPassword = ref('')
const loginError = ref('')
const loginLoading = ref(false)

// 회원가입
const regEmail = ref('')
const regPassword = ref('')
const regNickname = ref('')
const regIsOrganizer = ref(false)
const regError = ref('')
const regLoading = ref(false)
const nicknameMsg = ref('')
const nicknameAvailable = ref(false)

// 이메일 인증
const pendingEmail = ref('')
const verifyCode = ref('')
const verifyError = ref('')
const verifyLoading = ref(false)
const resendLoading = ref(false)
const resendSuccess = ref(false)

// 모달 닫힐 때 초기화
watch(() => props.visible, (v) => {
  if (!v) {
    mode.value = 'login'
    loginError.value = ''
    regError.value = ''
    verifyError.value = ''
  }
})

function handleClose() {
  emit('close')
}

async function checkNickname() {
  const nick = regNickname.value.trim()
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

async function handleLogin() {
  loginError.value = ''
  loginLoading.value = true
  try {
    const result = await login(loginEmail.value, loginPassword.value)
    if (result.ok) {
      loginEmail.value = ''
      loginPassword.value = ''
      emit('close')
    } else if (result.needVerify) {
      pendingEmail.value = loginEmail.value
      mode.value = 'verify'
    } else {
      loginError.value = result.error
    }
  } finally {
    loginLoading.value = false
  }
}

async function handleRegister() {
  regError.value = ''
  await checkNickname()
  if (nicknameMsg.value && !nicknameAvailable.value) {
    regError.value = nicknameMsg.value
    return
  }
  regLoading.value = true
  try {
    const result = await register(regEmail.value, regPassword.value, regNickname.value, regIsOrganizer.value)
    if (result.ok) {
      pendingEmail.value = regEmail.value
      mode.value = 'verify'
      regEmail.value = ''
      regPassword.value = ''
      regNickname.value = ''
      regIsOrganizer.value = false
    } else {
      regError.value = result.error
    }
  } finally {
    regLoading.value = false
  }
}

async function handleVerify() {
  verifyError.value = ''
  resendSuccess.value = false
  if (!verifyCode.value || verifyCode.value.length !== 6) {
    verifyError.value = '6자리 인증 코드를 입력해 주세요'
    return
  }
  verifyLoading.value = true
  try {
    const result = await verifyEmail(pendingEmail.value, verifyCode.value)
    if (result.ok) {
      emit('close')
    } else {
      verifyError.value = result.error
    }
  } finally {
    verifyLoading.value = false
  }
}

async function handleResend() {
  verifyError.value = ''
  resendSuccess.value = false
  resendLoading.value = true
  try {
    const result = await resendCode(pendingEmail.value)
    if (result.ok) {
      resendSuccess.value = true
      verifyError.value = '인증 코드가 재발송되었습니다'
      setTimeout(() => { resendSuccess.value = false; verifyError.value = '' }, 3000)
    } else {
      verifyError.value = result.error
    }
  } finally {
    resendLoading.value = false
  }
}
</script>
