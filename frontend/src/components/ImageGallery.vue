<template>
  <!-- 슬라이더 -->
  <div v-if="images.length > 0" class="gallery-slider">
    <div class="gallery-track" :style="{ transform: `translateX(-${currentIndex * 100}%)` }">
      <div v-for="(img, idx) in images" :key="idx" class="gallery-slide" @click="openViewer(idx)">
        <img :src="img.url" />
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

defineProps({
  images: { type: Array, default: () => [] },
})

const currentIndex = ref(0)
const viewerOpen = ref(false)
const viewerIndex = ref(0)

function openViewer(idx) {
  viewerIndex.value = idx
  viewerOpen.value = true
}
</script>
