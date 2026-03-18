// 이벤트 유형 라벨
export const TYPE_LABELS = {
  social: '소셜',
  workshop: '워크샵',
  festival: '페스티벌',
  regular_class: '정규수업',
  performance: '공연',
  practice: '프랙티스',
  other: '기타',
}

// 이벤트 유형 옵션 (select용)
export const TYPE_OPTIONS = Object.entries(TYPE_LABELS).map(([value, label]) => ({ value, label }))

// 춤 종류 라벨
export const GENRE_LABELS = {
  salsa: '살사',
  bachata: '바차타',
  kizomba: '키좀바',
  zouk: '주크',
  tango: '탱고',
  merengue: '메렝게',
  lindy_hop: '린디합',
  balboa: '발보아',
  blues: '블루스',
  west_coast_swing: '웨스트코스트스윙',
  other: '기타',
}

// 춤 종류 옵션 (checkbox용)
export const GENRE_OPTIONS = Object.entries(GENRE_LABELS).map(([value, label]) => ({ value, label }))

// 장소 유형 라벨
export const VENUE_TYPE_LABELS = {
  club: '클럽',
  academy: '학원',
  practice_room: '연습실',
}

// 장소 유형 옵션 (select용)
export const VENUE_TYPE_OPTIONS = Object.entries(VENUE_TYPE_LABELS).map(([value, label]) => ({ value, label }))

// 난이도 라벨
export const DIFFICULTY_LABELS = {
  beginner: '입문',
  elementary: '초급',
  intermediate: '중급',
  advanced: '고급',
  all_level: '올레벨',
}

// 난이도 옵션 (select용)
export const DIFFICULTY_OPTIONS = Object.entries(DIFFICULTY_LABELS).map(([value, label]) => ({ value, label }))

// 지도 마커 카테고리 (체크박스 필터용)
export const MAP_CATEGORIES = [
  { key: 'club', label: '클럽', color: '#9b59b6' },       // 보라색
  { key: 'academy', label: '학원', color: '#3498db' },     // 파란색
  { key: 'practice_room', label: '연습실', color: '#2ecc71' }, // 초록색
  { key: 'event', label: '이벤트', color: '#e74c3c' },     // 빨간색
]
