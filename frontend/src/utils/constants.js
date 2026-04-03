// 기본 날짜 필터 범위 (일)
export const DEFAULT_DATE_RANGE_DAYS = 30

// 이벤트 유형 라벨
export const TYPE_LABELS = {
  regular_class: '강습',
  social: '정모',
  festival: '파티',
  workshop: '워크샵',
  other: '기타',
  performance: '공연',
  practice: '프랙티스',
}

// 이벤트 유형 옵션 (select용 — 공연/프랙티스 제외)
const HIDDEN_TYPES = ['performance', 'practice']
export const TYPE_OPTIONS = Object.entries(TYPE_LABELS)
  .filter(([value]) => !HIDDEN_TYPES.includes(value))
  .map(([value, label]) => ({ value, label }))

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
  academy: '동호회',
  practice_room: '연습실',
}

// 장소 유형 옵션 (select용)
export const VENUE_TYPE_OPTIONS = Object.entries(VENUE_TYPE_LABELS).map(([value, label]) => ({ value, label }))

// 난이도 라벨
export const DIFFICULTY_LABELS = {
  beginner: '입문',
  elementary: '초급',
  pre_intermediate: '초중급',
  upper_intermediate: '준중급',
  intermediate: '중급',
  advanced: '고급',
  all_level: '올레벨',
}

// 난이도 옵션 (select용)
export const DIFFICULTY_OPTIONS = Object.entries(DIFFICULTY_LABELS).map(([value, label]) => ({ value, label }))

// 지도 마커 카테고리 (체크박스 필터용)
export const MAP_CATEGORIES = [
  { key: 'club', label: '댄스바', color: '#2E6EB5' },         // 파랑
  { key: 'academy', label: '동호회', color: '#D4A84C' },     // 노랑
  { key: 'practice_room', label: '연습실', color: '#4EA89E' }, // 틸
  { key: 'event', label: '강습/행사', color: '#7B2D8E' },     // 보라
]
