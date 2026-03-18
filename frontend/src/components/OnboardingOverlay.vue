<template>
  <div v-if="visible" class="onboarding-overlay" @click.self="dismiss">
    <div class="onboarding-card">
      <div class="onboarding-header">
        <span class="onboarding-emoji">💃🕺</span>
        <h1 class="onboarding-title">바람난 도시</h1>
        <p class="onboarding-subtitle">살사 · 바차타 · 스윙 · 탱고</p>
        <p class="onboarding-desc">커플댄스 이벤트와 장소를<br/>지도에서 한눈에 찾아보세요</p>
      </div>

      <div class="onboarding-guide">
        <div class="guide-item">
          <span class="guide-num">①</span>
          <span>상단 검색창에서 <b>지역을 검색</b>하세요</span>
        </div>
        <div class="guide-item">
          <span class="guide-num">②</span>
          <span><b>카테고리 버튼</b>으로 클럽·학원·연습실·이벤트를 필터링</span>
        </div>
        <div class="guide-item">
          <span class="guide-num">③</span>
          <span><b>지도 마커</b>를 눌러 상세 정보를 확인</span>
        </div>
        <div class="guide-item">
          <span class="guide-num">④</span>
          <span>사이드바에서 <b>날짜·요일별</b>로 이벤트 탐색</span>
        </div>
      </div>

      <div class="onboarding-actions">
        <button class="onboarding-btn primary" @click="$emit('goEvents')">이벤트 탐색하기</button>
        <button class="onboarding-btn primary" @click="$emit('goVenues')">장소 둘러보기</button>
        <button class="onboarding-btn ghost" @click="dismiss">바로시작</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['goEvents', 'goVenues', 'close'])
const visible = ref(false)

onMounted(() => {
  if (!localStorage.getItem('onboarding_done')) {
    visible.value = true
  }
})

function dismiss() {
  visible.value = false
  localStorage.setItem('onboarding_done', '1')
  emit('close')
}

defineExpose({ dismiss })
</script>

<style scoped>
.onboarding-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.onboarding-card {
  background: #1e1e2e; border-radius: 16px; padding: 32px 28px;
  max-width: 420px; width: 100%; text-align: center;
  border: 1px solid #333;
}
.onboarding-emoji { font-size: 2.5rem; display: block; margin-bottom: 8px; }
.onboarding-title { font-size: 1.5rem; font-weight: 700; color: #ff6b6b; margin-bottom: 4px; }
.onboarding-subtitle { font-size: 0.85rem; color: #a0a0a0; margin-bottom: 12px; }
.onboarding-desc { font-size: 0.9rem; color: #ccc; line-height: 1.5; margin-bottom: 20px; }

.onboarding-guide {
  text-align: left; margin-bottom: 24px;
  background: #16162a; border-radius: 10px; padding: 14px 16px;
}
.guide-item {
  display: flex; align-items: flex-start; gap: 8px;
  font-size: 0.8rem; color: #bbb; padding: 6px 0;
}
.guide-item b { color: #e0e0e0; }
.guide-num { color: #ff6b6b; font-weight: 700; font-size: 0.85rem; flex-shrink: 0; }

.onboarding-actions { display: flex; flex-direction: column; gap: 8px; }
.onboarding-btn {
  padding: 10px 16px; border-radius: 8px; font-size: 0.85rem;
  cursor: pointer; border: none; font-weight: 600;
}
.onboarding-btn.primary { background: #ff6b6b; color: #fff; }
.onboarding-btn.primary:hover { background: #ff5252; }
.onboarding-btn.ghost { background: transparent; color: #888; border: 1px solid #444; }
.onboarding-btn.ghost:hover { color: #ccc; border-color: #666; }

@media (max-width: 768px) {
  .onboarding-card { padding: 24px 20px; }
  .onboarding-emoji { font-size: 2rem; }
  .onboarding-title { font-size: 1.3rem; }
}
</style>
