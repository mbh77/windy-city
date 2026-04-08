import { ref } from 'vue'
import { apiFetch, apiJson, setToken, clearToken } from '../utils/api.js'
import { useBookmarks } from './useBookmarks.js'

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

  // 소셜 로그인 (인가코드를 백엔드에 전달)
  async function socialLogin(provider, code, redirectUri) {
    const res = await apiJson(`/api/auth/${provider}`, {
      method: 'POST',
      body: JSON.stringify({ code, redirect_uri: redirectUri }),
    })
    if (res.ok) {
      const data = await res.json()
      if (data.status === 'login') {
        setToken(data.access_token)
        await restoreSession()
        return { ok: true }
      }
      // 신규 가입 필요
      return { ok: false, needRegister: true, socialData: data }
    } else {
      const err = await res.json()
      return { ok: false, error: err.detail || '소셜 로그인에 실패했습니다' }
    }
  }

  // 소셜 회원가입 (닉네임 확인 후 계정 생성)
  async function socialRegister(provider, providerId, email, nickname) {
    const res = await apiJson('/api/auth/social/register', {
      method: 'POST',
      body: JSON.stringify({ provider, provider_id: providerId, email, nickname }),
    })
    if (res.ok) {
      const data = await res.json()
      setToken(data.access_token)
      await restoreSession()
      return { ok: true }
    } else {
      const err = await res.json()
      return { ok: false, error: err.detail || '가입에 실패했습니다' }
    }
  }

  // 로그아웃
  function logout() {
    clearToken()
    currentUser.value = null
    useBookmarks().clearBookmarks()
  }

  // 회원 탈퇴
  async function withdraw() {
    const res = await apiJson('/api/auth/me', { method: 'DELETE' })
    if (res.ok) {
      clearToken()
      currentUser.value = null
      useBookmarks().clearBookmarks()
      return { ok: true }
    } else {
      const err = await res.json()
      return { ok: false, error: err.detail || '탈퇴에 실패했습니다' }
    }
  }

  return {
    currentUser,
    restoreSession,
    login,
    register,
    verifyEmail,
    resendCode,
    socialLogin,
    socialRegister,
    logout,
    withdraw,
  }
}
