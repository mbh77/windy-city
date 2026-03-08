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
let tempMarker = null;
let pickedLatLng = null;
// 이벤트 등록 폼 데이터 임시 저장 (위치 선택 중 모달 닫힐 때)
let savedFormData = null;
// 이메일 인증 대기 중인 이메일
let pendingVerifyEmail = null;

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
  document.getElementById('btn-add-event').addEventListener('click', () => {
    document.getElementById('form-create').reset();
    document.getElementById('input-lat').value = '';
    document.getElementById('input-lng').value = '';
    updatePickedAddressDisplay();
    openModal('modal-create');
  });

  // 장소 검색 Enter 키 처리 (폼 submit 방지)
  document.getElementById('location-search-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      searchLocation();
    }
  });
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
    pickedLatLng = latlng;

    // 기존 임시 마커 제거
    if (tempMarker) tempMarker.setMap(null);

    // 빨간 마커 생성
    tempMarker = new window.kakao.maps.Marker({
      position: latlng,
      map: map
    });

    // 역지오코딩으로 주소 표시
    document.getElementById('pick-bar-msg').textContent = '주소 검색 중...';
    const geocoder = new window.kakao.maps.services.Geocoder();
    geocoder.coord2Address(latlng.getLng(), latlng.getLat(), (result, status) => {
      if (status === window.kakao.maps.services.Status.OK && result[0]) {
        const addr = result[0].road_address
          ? result[0].road_address.address_name
          : result[0].address.address_name;
        document.getElementById('pick-bar-msg').textContent = addr;
        // 주소를 savedFormData에도 저장
        if (savedFormData) savedFormData.address = addr;
      } else {
        document.getElementById('pick-bar-msg').textContent = '주소를 찾을 수 없습니다';
      }
    });
    document.getElementById('pick-bar-actions').classList.remove('hidden');
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

// ── 버튼 스피너 유틸 ──────────────────────────────────────────
function btnLoading(btn) { btn.classList.add('btn-loading'); btn.disabled = true; }
function btnReset(btn) { btn.classList.remove('btn-loading'); btn.disabled = false; }

// ── 로그인 ────────────────────────────────────────────────────
async function handleLogin(e) {
  e.preventDefault();
  const form = e.target;
  const btn = document.getElementById('btn-login');
  const errEl = document.getElementById('login-error');
  errEl.textContent = '';
  btnLoading(btn);

  try {
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
    } else if (res.status === 403) {
      pendingVerifyEmail = form.email.value;
      showVerifySection(pendingVerifyEmail);
    } else {
      const err = await res.json();
      errEl.textContent = err.detail || '로그인에 실패했습니다';
    }
  } finally {
    btnReset(btn);
  }
}

// ── 회원가입 ──────────────────────────────────────────────────
async function handleRegister(e) {
  e.preventDefault();
  const form = e.target;
  const btn = document.getElementById('btn-register');
  const errEl = document.getElementById('register-error');
  errEl.textContent = '';
  btnLoading(btn);

  try {
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
      pendingVerifyEmail = form.email.value;
      showVerifySection(pendingVerifyEmail);
      form.reset();
    } else {
      const err = await res.json();
      errEl.textContent = err.detail || '가입에 실패했습니다';
    }
  } finally {
    btnReset(btn);
  }
}

// ── 인증 코드 UI 전환 ──────────────────────────────────────────
function showVerifySection(email) {
  document.getElementById('form-login').classList.add('hidden');
  document.getElementById('form-register').classList.add('hidden');
  document.querySelector('.tab-group').classList.add('hidden');
  document.getElementById('verify-section').classList.remove('hidden');
  document.getElementById('verify-msg').textContent = `${email} 으로 인증 코드가 발송되었습니다`;
  document.getElementById('verify-code').value = '';
  document.getElementById('verify-error').textContent = '';
}

// ── 인증 코드 확인 ──────────────────────────────────────────────
async function handleVerify() {
  const code = document.getElementById('verify-code').value.trim();
  const btn = document.getElementById('btn-verify');
  const errEl = document.getElementById('verify-error');
  errEl.textContent = '';

  if (!code || code.length !== 6) {
    errEl.textContent = '6자리 인증 코드를 입력해 주세요';
    return;
  }

  btnLoading(btn);
  try {
    const res = await fetch(`${API}/api/auth/verify-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: pendingVerifyEmail, code })
    });

    if (res.ok) {
      const data = await res.json();
      setToken(data.access_token);
      await restoreSession();
      hideVerifySection();
      closeModal('modal-auth');
    } else {
      const err = await res.json();
      errEl.textContent = err.detail || '인증에 실패했습니다';
    }
  } finally {
    btnReset(btn);
  }
}

// ── 인증 코드 재발송 ────────────────────────────────────────────
async function handleResendCode() {
  const btn = document.getElementById('btn-resend');
  const errEl = document.getElementById('verify-error');
  errEl.textContent = '';
  btnLoading(btn);

  try {
    const res = await fetch(`${API}/api/auth/resend-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: pendingVerifyEmail })
    });

    if (res.ok) {
      errEl.style.color = '#6bff9d';
      errEl.textContent = '인증 코드가 재발송되었습니다';
      setTimeout(() => { errEl.style.color = ''; }, 3000);
    } else {
      const err = await res.json();
      errEl.textContent = err.detail || '재발송에 실패했습니다';
    }
  } finally {
    btnReset(btn);
  }
}

// ── 인증 섹션 숨기고 원래 UI 복원 ───────────────────────────────
function hideVerifySection() {
  document.getElementById('verify-section').classList.add('hidden');
  document.querySelector('.tab-group').classList.remove('hidden');
  // 로그인 탭으로 초기화
  switchTab('login');
  pendingVerifyEmail = null;
}

// ── 이벤트 등록 ───────────────────────────────────────────────
async function handleCreateEvent(e) {
  e.preventDefault();
  const form = e.target;
  const errEl = document.getElementById('create-error');
  errEl.textContent = '';

  // 위치 선택 검증
  if (!form.latitude.value || !form.longitude.value) {
    errEl.textContent = '지도에서 위치를 선택해 주세요';
    return;
  }

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
    updatePickedAddressDisplay();
    await loadEvents();
  } else {
    const err = await res.json();
    errEl.textContent = err.detail || '등록에 실패했습니다';
  }
}

// ── 지도에서 위치 선택 ────────────────────────────────────────
function pickLocation() {
  // 폼 데이터 임시 저장
  savedFormData = saveCreateFormData();
  isPickingLocation = true;
  pickedLatLng = null;
  closeModal('modal-create');

  // 오버레이 바 표시
  const bar = document.getElementById('pick-location-bar');
  bar.classList.remove('hidden');
  document.getElementById('pick-bar-msg').textContent = '지도에서 위치를 클릭하세요';
  document.getElementById('pick-bar-actions').classList.add('hidden');

  // 기존 이벤트 마커 숨기기
  markers.forEach(m => m.setMap(null));

  // 커서 변경 + 지도 테두리
  document.getElementById('map').classList.add('picking');
}

// 위치 확인 → 좌표 저장 후 모달 복귀
function confirmPickedLocation() {
  if (!pickedLatLng) return;
  // 바에 표시된 주소 가져오기
  const pickedAddr = document.getElementById('pick-bar-msg').textContent;
  // 좌표를 savedFormData에 반영한 후 복원
  if (savedFormData) {
    savedFormData.latitude = pickedLatLng.getLat().toFixed(6);
    savedFormData.longitude = pickedLatLng.getLng().toFixed(6);
    // 주소 필드에도 반영
    if (pickedAddr && pickedAddr !== '주소 검색 중...' && pickedAddr !== '주소를 찾을 수 없습니다') {
      savedFormData.address = pickedAddr;
    }
  }
  exitPickMode();
  openModal('modal-create');
  if (savedFormData) {
    restoreCreateFormData(savedFormData);
    savedFormData = null;
  }
  // 모달 내 위치 표시 업데이트
  updatePickedAddressDisplay();
}

// 재선택 → 마커 제거, 다시 클릭 대기
function retryPickLocation() {
  if (tempMarker) { tempMarker.setMap(null); tempMarker = null; }
  pickedLatLng = null;
  document.getElementById('pick-bar-msg').textContent = '지도에서 위치를 클릭하세요';
  document.getElementById('pick-bar-actions').classList.add('hidden');
}

// 취소 → 원래 상태로 복귀
function cancelPickLocation() {
  exitPickMode();
  openModal('modal-create');
  if (savedFormData) {
    restoreCreateFormData(savedFormData);
    savedFormData = null;
  }
}

// 위치 선택 모드 종료 공통 처리
function exitPickMode() {
  isPickingLocation = false;
  if (tempMarker) { tempMarker.setMap(null); tempMarker = null; }
  document.getElementById('pick-location-bar').classList.add('hidden');
  document.getElementById('map').classList.remove('picking');

  // 기존 이벤트 마커 복원
  markers.forEach(m => m.setMap(map));
}

// 모달 내 선택된 주소 표시 업데이트
function updatePickedAddressDisplay() {
  const el = document.getElementById('picked-address');
  const lat = document.getElementById('input-lat').value;
  const lng = document.getElementById('input-lng').value;
  const addr = document.getElementById('form-create').address.value;
  if (lat && lng) {
    el.textContent = addr || '위치 선택됨';
    el.classList.add('has-value');
  } else {
    el.textContent = '위치를 선택해 주세요';
    el.classList.remove('has-value');
  }
}

// ── 장소/주소 검색 ──────────────────────────────────────────
function searchLocation() {
  const query = document.getElementById('location-search-input').value.trim();
  if (!query) return;

  const resultsEl = document.getElementById('location-search-results');
  resultsEl.innerHTML = '<li class="search-loading">검색 중...</li>';
  resultsEl.classList.remove('hidden');

  const places = new window.kakao.maps.services.Places();
  places.keywordSearch(query, (data, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      renderSearchResults(data.slice(0, 5));
    } else if (status === window.kakao.maps.services.Status.ZERO_RESULT) {
      resultsEl.innerHTML = '<li class="search-empty">검색 결과가 없습니다</li>';
    } else {
      resultsEl.innerHTML = '<li class="search-empty">검색에 실패했습니다</li>';
    }
  });
}

// 검색 결과 렌더링
function renderSearchResults(places) {
  const resultsEl = document.getElementById('location-search-results');
  resultsEl.innerHTML = '';
  places.forEach(place => {
    const li = document.createElement('li');
    li.innerHTML = `
      <div class="search-place-name">${place.place_name}</div>
      <div class="search-place-addr">${place.road_address_name || place.address_name}</div>
    `;
    li.addEventListener('click', () => selectSearchResult(place));
    resultsEl.appendChild(li);
  });
}

// 검색 결과 선택 → 좌표/주소/장소명 자동 입력
function selectSearchResult(place) {
  const form = document.getElementById('form-create');
  // 좌표 저장
  document.getElementById('input-lat').value = parseFloat(place.y).toFixed(6);
  document.getElementById('input-lng').value = parseFloat(place.x).toFixed(6);
  // 주소 자동 입력
  form.address.value = place.road_address_name || place.address_name;
  // 장소명이 비어 있으면 자동 입력
  if (!form.location_name.value) {
    form.location_name.value = place.place_name;
  }
  // 검색 결과 닫기
  document.getElementById('location-search-results').classList.add('hidden');
  document.getElementById('location-search-input').value = '';
  // 위치 표시 업데이트
  updatePickedAddressDisplay();
  // 지도 해당 위치로 이동
  const pos = new window.kakao.maps.LatLng(place.y, place.x);
  map.panTo(pos);
}

// 폼 데이터 저장/복원 (위치 선택 중 모달이 닫히므로)
function saveCreateFormData() {
  const form = document.getElementById('form-create');
  return {
    title: form.title.value,
    description: form.description.value,
    location_name: form.location_name.value,
    address: form.address.value,
    latitude: form.latitude.value,
    longitude: form.longitude.value,
    start_date: form.start_date.value,
    end_date: form.end_date.value,
    event_type: form.event_type.value,
    dance_genres: Array.from(form.querySelectorAll('input[name="dance_genres"]:checked')).map(cb => cb.value),
  };
}

function restoreCreateFormData(data) {
  const form = document.getElementById('form-create');
  form.title.value = data.title;
  form.description.value = data.description;
  form.location_name.value = data.location_name;
  form.address.value = data.address;
  form.latitude.value = data.latitude;
  form.longitude.value = data.longitude;
  form.start_date.value = data.start_date;
  form.end_date.value = data.end_date;
  form.event_type.value = data.event_type;
  // 체크박스 복원
  form.querySelectorAll('input[name="dance_genres"]').forEach(cb => {
    cb.checked = data.dance_genres.includes(cb.value);
  });
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
