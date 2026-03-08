// 이벤트 유형 라벨
export const TYPE_LABELS = {
  social: '소셜',
  workshop: '워크샵',
  congress: '콩그레스',
  practice: '프랙티스',
  performance: '공연',
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
  other: '기타',
}

// 춤 종류 옵션 (checkbox용)
export const GENRE_OPTIONS = Object.entries(GENRE_LABELS).map(([value, label]) => ({ value, label }))
