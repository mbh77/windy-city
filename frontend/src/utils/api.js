// ── 토큰 관리 ──
function getToken() {
  return localStorage.getItem('token')
}

export function setToken(t) {
  localStorage.setItem('token', t)
}

export function clearToken() {
  localStorage.removeItem('token')
}

// ── 인증 헤더 ──
function authHeaders() {
  const t = getToken()
  return t ? { Authorization: `Bearer ${t}` } : {}
}

// ── API 호출 헬퍼 ──
export async function apiFetch(url, options = {}) {
  const headers = {
    ...authHeaders(),
    ...options.headers,
  }
  const res = await fetch(url, { ...options, headers })
  return res
}

export async function apiJson(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  return apiFetch(url, { ...options, headers })
}

// ── 날짜 포맷 ──
export function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso.includes('T') ? iso : iso + 'T00:00:00')
  const yy = String(d.getFullYear()).slice(2)
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yy}-${mm}-${dd}`
}

// ── 작성일 포맷 (YYYY-MM-DD HH:MM:SS) ──
export function formatCreatedAt(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

// ── 시간 포맷 (HH:MM만 표시) ──
export function formatTime(time) {
  if (!time) return ''
  return time.slice(0, 5)
}
