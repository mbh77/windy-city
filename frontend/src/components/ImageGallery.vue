<template>
  <!-- 슬라이더 -->
  <div v-if="images.length > 0" class="gallery-slider"
    @touchstart="onSwipeStart" @touchend="onSwipeEnd"
    @mousedown="onSwipeStart" @mouseup="onSwipeEnd"
  >
    <div class="gallery-track" :style="{ transform: `translateX(-${currentIndex * 100}%)` }">
      <div v-for="(img, idx) in images" :key="idx" class="gallery-slide" @click="openViewer(idx)">
        <img :src="img.url" draggable="false" />
      </div>
    </div>
    <button v-if="images.length > 1 && currentIndex > 0" class="gallery-arrow gallery-prev" @click="currentIndex--">‹</button>
    <button v-if="images.length > 1 && currentIndex < images.length - 1" class="gallery-arrow gallery-next" @click="currentIndex++">›</button>
    <div v-if="images.length > 1" class="gallery-dots">
      <span
        v-for="(_, idx) in images"
        :key="idx"
        :class="['gallery-dot', { active: idx === currentIndex }]"
        @click="currentIndex = idx"
      ></span>
    </div>
  </div>

  <!-- 전체화면 뷰어 -->
  <div v-if="viewerOpen" class="image-viewer" @click.self="viewerOpen = false">
    <button class="viewer-close" @click="viewerOpen = false">✕</button>
    <button v-if="images.length > 1 && viewerIndex > 0" class="viewer-arrow viewer-prev" @click="viewerIndex--">‹</button>
    <img :src="images[viewerIndex].url" class="viewer-image" />
    <button v-if="images.length > 1 && viewerIndex < images.length - 1" class="viewer-arrow viewer-next" @click="viewerIndex++">›</button>
    <div class="viewer-counter">{{ viewerIndex + 1 }} / {{ images.length }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  images: { type: Array, default: () => [] },
})

const currentIndex = ref(0)
const viewerOpen = ref(false)
const viewerIndex = ref(0)

// 스와이프 처리
let swipeStartX = 0
let swipeStartTime = 0

function getX(e) {
  return e.touches ? e.touches[0].clientX : e.clientX
}

function onSwipeStart(e) {
  swipeStartX = getX(e)
  swipeStartTime = Date.now()
}

function onSwipeEnd(e) {
  const endX = e.changedTouches ? e.changedTouches[0].clientX : e.clientX
  const diff = swipeStartX - endX
  const elapsed = Date.now() - swipeStartTime

  // 50px 이상 또는 빠른 스와이프(300ms 이내 30px)
  if (Math.abs(diff) > 50 || (elapsed < 300 && Math.abs(diff) > 30)) {
    if (diff > 0 && currentIndex.value < props.images.length - 1) {
      currentIndex.value++
    } else if (diff < 0 && currentIndex.value > 0) {
      currentIndex.value--
    }
  }
}

function openViewer(idx) {
  // 스와이프 후 클릭 방지: 짧은 탭만 열기
  if (Date.now() - swipeStartTime > 300) return
  viewerIndex.value = idx
  viewerOpen.value = true
}
</script>
