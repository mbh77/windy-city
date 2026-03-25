<template>
  <div v-if="visible" class="onboarding-overlay" @click.self="dismiss">
    <div class="onboarding-card">
      <div class="onboarding-header">
        <div class="onboarding-logo-wrap">
          <img src="@/assets/windycity_logo.png" alt="바람난 도시" class="onboarding-logo" />
        </div>
        <p class="onboarding-subtitle">살사 · 바차타 · 스윙 · 탱고</p>
        <p class="onboarding-desc">커플댄스 강습·행사와 장소를<br/>지도에서 한눈에 찾아보세요</p>
      </div>

      <div class="onboarding-guide">
        <div class="guide-item">
          <span class="guide-num">①</span>
          <span>상단 검색창에서 <b>지역을 검색</b>하세요</span>
        </div>
        <div class="guide-item">
          <span class="guide-num">②</span>
          <span><b>카테고리 버튼</b>으로 클럽·학원·연습실·강습·행사를 필터링</span>
        </div>
        <div class="guide-item">
          <span class="guide-num">③</span>
          <span><b>지도 마커</b>를 눌러 상세 정보를 확인</span>
        </div>
        <div class="guide-item">
          <span class="guide-num">④</span>
          <span>사이드바에서 <b>날짜·요일별</b>로 강습·행사 탐색</span>
        </div>
      </div>

      <div class="onboarding-actions">
        <button class="onboarding-btn primary" @click="dismiss">시작하기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['close'])
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
  background: rgba(0, 0, 0, 0.5);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.onboarding-card {
  background: #FFFFFF; border-radius: 16px; padding: 32px 28px;
  max-width: 420px; width: 100%; text-align: center;
  border: 1px solid #E0D5C8;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}
.onboarding-logo-wrap {
  background: #5BA89E; border-radius: 12px; padding: 16px;
  margin-bottom: 12px; display: inline-block;
}
.onboarding-logo { height: 48px; }
.onboarding-subtitle { font-size: 0.85rem; color: #8B7B6B; margin-bottom: 12px; }
.onboarding-desc { font-size: 0.9rem; color: #5A4A3A; line-height: 1.5; margin-bottom: 20px; }

.onboarding-guide {
  text-align: left; margin-bottom: 24px;
  background: #F8F4F0; border-radius: 10px; padding: 14px 16px;
}
.guide-item {
  display: flex; align-items: flex-start; gap: 8px;
  font-size: 0.8rem; color: #5A4A3A; padding: 6px 0;
}
.guide-item b { color: #3D3029; }
.guide-num { color: #D4725C; font-weight: 700; font-size: 0.85rem; flex-shrink: 0; }

.onboarding-actions { display: flex; flex-direction: column; gap: 8px; }
.onboarding-btn {
  padding: 10px 16px; border-radius: 8px; font-size: 0.85rem;
  cursor: pointer; border: none; font-weight: 600;
}
.onboarding-btn.primary { background: #5BA89E; color: #fff; }
.onboarding-btn.primary:hover { background: #4E9589; }

@media (max-width: 768px) {
  .onboarding-card { padding: 24px 20px; }
  .onboarding-logo { height: 40px; }
}
</style>
