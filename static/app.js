// ── 상수 ──────────────────────────────────────────────────────
const API = '';  // 같은 origin이므로 빈 문자열
// 이벤트 유형 라벨
const TYPE_LABELS = {
  social: '소셜', workshop: '워크샵', congress: '콩그레스',
  practice: '프랙티스', performance: '공연', other: '기타'
};
// 춤 종류 라벨
const GENRE_LABELS = {
  salsa: '살사', bachata: '바차타', kizomba: '키좀바',
  zouk: '주크', tango: '탱고', other: '기타'
};

// ── 상태 ──────────────────────────────────────────────────────
let map = null;
let markers = [];
let events = [];
let currentUser = null;
let isPickingLocation = false;

// ── 토큰 관리 ─────────────────────────────────────────────────
function getToken() { return localStorage.getItem('token'); }
function setToken(t) { localStorage.setItem('token', t); }
function clearToken() { localStorage.removeItem('token'); }

function authHeaders() {
  const t = getToken();
  return t ? { 'Authorization': `Bearer ${t}` } : {};
}

// ── 초기화 ────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', async () => {
  if (window.kakao && window.kakao.maps) {
    await new Promise(resolve => window.kakao.maps.load(resolve));
  }
  initMap();
  await restoreSession();
  await loadEvents();

  document.getElementById('btn-search').addEventListener('click', loadEvents);
  document.getElementById('btn-auth').addEventListener('click', () => {
    if (currentUser) logout();
    else openModal('modal-auth');
  });
  document.getElementById('btn-add-event').addEventListener('click', () => openModal('modal-create'));
});

function initMap() {
  const container = document.getElementById('map');
  // 서울 시청 기준 초기 위치
  const options = {
    center: new window.kakao.maps.LatLng(37.5665, 126.9780),
    level: 7
  };
  map = new window.kakao.maps.Map(container, options);

  // 지도 클릭 시 위치 선택 (이벤트 등록용)
  window.kakao.maps.event.addListener(map, 'click', (mouseEvent) => {
    if (!isPickingLocation) return;
    const latlng = mouseEvent.latLng;
    document.getElementById('input-lat').value = latlng.getLat().toFixed(6);
    document.getElementById('input-lng').value = latlng.getLng().toFixed(6);
    isPickingLocation = false;
    map.setCursor('');
  });
}

// ── 세션 복원 ─────────────────────────────────────────────────
async function restoreSession() {
  const token = getToken();
  if (!token) return;
  try {
    const res = await fetch(`${API}/api/auth/me`, { headers: authHeaders() });
    if (res.ok) {
      currentUser = await res.json();
      updateAuthUI();
    } else {
      clearToken();
    }
  } catch {}
}

function updateAuthUI() {
  const btnAuth = document.getElementById('btn-auth');
  const btnAdd = document.getElementById('btn-add-event');
  if (currentUser) {
    btnAuth.textContent = `${currentUser.nickname} 로그아웃`;
    if (currentUser.is_organizer) btnAdd.style.display = '';
  } else {
    btnAuth.textContent = '로그인';
    btnAdd.style.display = 'none';
  }
}

// ── 이벤트 목록 로드 ──────────────────────────────────────────
async function loadEvents() {
  const dateVal = document.getElementById('filter-date').value;
  const typeVal = document.getElementById('filter-type').value;

  const params = new URLSearchParams();
  if (dateVal) {
    params.set('date_from', new Date(dateVal).toISOString());
    // 선택한 날짜 하루 끝까지
    const end = new Date(dateVal);
    end.setDate(end.getDate() + 1);
    params.set('date_to', end.toISOString());
  }
  if (typeVal) params.set('event_type', typeVal);
  const genreVal = document.getElementById('filter-genre').value;
  if (genreVal) params.set('dance_genre', genreVal);

  const res = await fetch(`${API}/api/events/?${params}`);
  events = await res.json();
  renderList(events);
  renderMarkers(events);
}

// ── 사이드바 목록 렌더링 ──────────────────────────────────────
function renderList(evts) {
  const ul = document.getElementById('event-list');
  document.getElementById('event-count').textContent = `이벤트 ${evts.length}개`;
  ul.innerHTML = '';
  evts.forEach(ev => {
    const li = document.createElement('li');
    const genreBadges = (ev.dance_genres || []).map(g =>
      `<span class="genre-badge genre-${g}">${GENRE_LABELS[g]}</span>`
    ).join('');
    li.innerHTML = `
      <span class="event-type-badge type-${ev.event_type}">${TYPE_LABELS[ev.event_type]}</span>
      ${genreBadges}
      <div class="event-title">${ev.title}</div>
      <div class="event-meta">📍 ${ev.location_name}</div>
      <div class="event-meta">📅 ${formatDate(ev.start_date)}</div>
    `;
    li.addEventListener('click', () => showEventDetail(ev));
    ul.appendChild(li);
  });
}

// ── 카카오맵 마커 렌더링 ──────────────────────────────────────
function renderMarkers(evts) {
  // 기존 마커 제거
  markers.forEach(m => m.setMap(null));
  markers = [];

  evts.forEach(ev => {
    const pos = new window.kakao.maps.LatLng(ev.latitude, ev.longitude);
    const marker = new window.kakao.maps.Marker({ position: pos, map });

    // 인포윈도우
    const infoContent = `
      <div style="padding:6px 10px;font-size:13px;white-space:nowrap">
        <strong>${ev.title}</strong><br/>
        <span style="color:#888;font-size:11px">${formatDate(ev.start_date)}</span>
      </div>`;
    const infowindow = new window.kakao.maps.InfoWindow({ content: infoContent });

    window.kakao.maps.event.addListener(marker, 'mouseover', () => infowindow.open(map, marker));
    window.kakao.maps.event.addListener(marker, 'mouseout', () => infowindow.close());
    window.kakao.maps.event.addListener(marker, 'click', () => showEventDetail(ev));

    markers.push(marker);
  });
}

// ── 이벤트 상세 팝업 ──────────────────────────────────────────
function showEventDetail(ev) {
  const isOwner = currentUser && currentUser.id === ev.organizer_id;
  const body = document.getElementById('modal-event-body');
  const detailGenres = (ev.dance_genres || []).map(g =>
    `<span class="genre-badge genre-${g}">${GENRE_LABELS[g]}</span>`
  ).join('');
  body.innerHTML = `
    <span class="event-type-badge type-${ev.event_type}">${TYPE_LABELS[ev.event_type]}</span>
    ${detailGenres}
    <h2 style="margin-top:8px">${ev.title}</h2>
    ${ev.description ? `<p style="margin:8px 0;color:#bbb;font-size:0.85rem">${ev.description}</p>` : ''}
    <div class="detail-row"><span class="detail-label">장소</span>${ev.location_name}</div>
    ${ev.address ? `<div class="detail-row"><span class="detail-label">주소</span>${ev.address}</div>` : ''}
    <div class="detail-row"><span class="detail-label">시작</span>${formatDate(ev.start_date)}</div>
    ${ev.end_date ? `<div class="detail-row"><span class="detail-label">종료</span>${formatDate(ev.end_date)}</div>` : ''}
    <div class="detail-row"><span class="detail-label">주최</span>${ev.organizer_nickname || '-'}</div>
    ${isOwner ? `
      <div class="action-row">
        <button class="btn-danger" onclick="deleteEvent(${ev.id})">삭제</button>
      </div>` : ''}
  `;
  openModal('modal-event');

  // 지도에서 해당 마커 위치로 이동
  map.panTo(new window.kakao.maps.LatLng(ev.latitude, ev.longitude));
}

// ── 이벤트 삭제 ───────────────────────────────────────────────
async function deleteEvent(id) {
  if (!confirm('이벤트를 삭제할까요?')) return;
  const res = await fetch(`${API}/api/events/${id}`, {
    method: 'DELETE',
    headers: authHeaders()
  });
  if (res.ok) {
    closeModal('modal-event');
    await loadEvents();
  }
}

// ── 로그인 ────────────────────────────────────────────────────
async function handleLogin(e) {
  e.preventDefault();
  const form = e.target;
  const errEl = document.getElementById('login-error');
  errEl.textContent = '';

  const res = await fetch(`${API}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: form.email.value,
      password: form.password.value,
    })
  });

  if (res.ok) {
    const data = await res.json();
    setToken(data.access_token);
    await restoreSession();
    closeModal('modal-auth');
    form.reset();
  } else {
    const err = await res.json();
    errEl.textContent = err.detail || '로그인에 실패했습니다';
  }
}

// ── 회원가입 ──────────────────────────────────────────────────
async function handleRegister(e) {
  e.preventDefault();
  const form = e.target;
  const errEl = document.getElementById('register-error');
  errEl.textContent = '';

  const res = await fetch(`${API}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: form.email.value,
      password: form.password.value,
      nickname: form.nickname.value,
      is_organizer: form.is_organizer.checked,
    })
  });

  if (res.ok) {
    // 가입 후 자동 로그인
    const loginRes = await fetch(`${API}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: form.email.value, password: form.password.value })
    });
    const data = await loginRes.json();
    setToken(data.access_token);
    await restoreSession();
    closeModal('modal-auth');
    form.reset();
  } else {
    const err = await res.json();
    errEl.textContent = err.detail || '가입에 실패했습니다';
  }
}

// ── 이벤트 등록 ───────────────────────────────────────────────
async function handleCreateEvent(e) {
  e.preventDefault();
  const form = e.target;
  const errEl = document.getElementById('create-error');
  errEl.textContent = '';

  // 선택된 춤 종류 수집
  const selectedGenres = Array.from(form.querySelectorAll('input[name="dance_genres"]:checked'))
    .map(cb => cb.value);

  const body = {
    title: form.title.value,
    description: form.description.value || null,
    location_name: form.location_name.value,
    address: form.address.value || null,
    latitude: parseFloat(form.latitude.value),
    longitude: parseFloat(form.longitude.value),
    start_date: new Date(form.start_date.value).toISOString(),
    end_date: form.end_date.value ? new Date(form.end_date.value).toISOString() : null,
    event_type: form.event_type.value,
    dance_genres: selectedGenres,
  };

  const res = await fetch(`${API}/api/events/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body)
  });

  if (res.ok) {
    closeModal('modal-create');
    form.reset();
    await loadEvents();
  } else {
    const err = await res.json();
    errEl.textContent = err.detail || '등록에 실패했습니다';
  }
}

// ── 지도에서 위치 선택 ────────────────────────────────────────
function pickLocation() {
  isPickingLocation = true;
  closeModal('modal-create');
  // 잠깐 후 다시 열기 (지도 클릭 후 모달 복귀는 클릭 핸들러에서 처리)
  alert('지도에서 위치를 클릭하세요. 선택 후 이벤트 등록 창을 다시 열어주세요.');
}

// ── 로그아웃 ──────────────────────────────────────────────────
function logout() {
  clearToken();
  currentUser = null;
  updateAuthUI();
}

// ── 모달 유틸 ─────────────────────────────────────────────────
function openModal(id) { document.getElementById(id).classList.remove('hidden'); }
function closeModal(id) { document.getElementById(id).classList.add('hidden'); }

// ── 탭 전환 ───────────────────────────────────────────────────
function switchTab(tab) {
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(t => t.classList.remove('active'));
  document.querySelector(`.tab[onclick="switchTab('${tab}')"]`).classList.add('active');
  document.getElementById('form-login').classList.toggle('hidden', tab !== 'login');
  document.getElementById('form-register').classList.toggle('hidden', tab !== 'register');
}

// ── 날짜 포맷 ─────────────────────────────────────────────────
function formatDate(iso) {
  if (!iso) return '-';
  const d = new Date(iso);
  return d.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
