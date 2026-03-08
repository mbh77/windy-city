import { ref } from 'vue'
import { apiFetch, apiJson, setToken, clearToken } from '../utils/api.js'

// 전역 인증 상태
const currentUser = ref(null)

export function useAuth() {
  // 세션 복원
  async function restoreSession() {
    const token = localStorage.getItem('token')
    if (!token) return
    try {
      const res = await apiFetch('/api/auth/me')
      if (res.ok) {
        currentUser.value = await res.json()
      } else {
        clearToken()
      }
    } catch {
      clearToken()
    }
  }

  // 로그인
  async function login(email, password) {
    const res = await apiJson('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    if (res.ok) {
      const data = await res.json()
      setToken(data.access_token)
      await restoreSession()
      return { ok: true }
    } else if (res.status === 403) {
      return { ok: false, needVerify: true }
    } else {
      const err = await res.json()
      return { ok: false, error: err.detail || '로그인에 실패했습니다' }
    }
  }

  // 회원가입
  async function register(email, password, nickname, isOrganizer) {
    const res = await apiJson('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, nickname, is_organizer: isOrganizer }),
    })
    if (res.ok) {
      return { ok: true }
    } else {
      const err = await res.json()
      return { ok: false, error: err.detail || '가입에 실패했습니다' }
    }
  }

  // 이메일 인증
  async function verifyEmail(email, code) {
    const res = await apiJson('/api/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ email, code }),
    })
    if (res.ok) {
      const data = await res.json()
      setToken(data.access_token)
      await restoreSession()
      return { ok: true }
    } else {
      const err = await res.json()
      return { ok: false, error: err.detail || '인증에 실패했습니다' }
    }
  }

  // 인증 코드 재발송
  async function resendCode(email) {
    const res = await apiJson('/api/auth/resend-code', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
    if (res.ok) {
      return { ok: true }
    } else {
      const err = await res.json()
      return { ok: false, error: err.detail || '재발송에 실패했습니다' }
    }
  }

  // 로그아웃
  function logout() {
    clearToken()
    currentUser.value = null
  }

  return {
    currentUser,
    restoreSession,
    login,
    register,
    verifyEmail,
    resendCode,
    logout,
  }
}
