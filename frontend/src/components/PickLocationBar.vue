<template>
  <div v-if="visible" class="pick-bar">
    <span>{{ message }}</span>
    <div v-if="hasLocation" style="display:flex;gap:6px">
      <button class="btn-primary" @click="$emit('confirm')">확인</button>
      <button class="btn-ghost" @click="$emit('retry')">재선택</button>
    </div>
    <button class="btn-ghost" @click="$emit('cancel')">취소</button>
  </div>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  message: { type: String, default: '지도에서 위치를 클릭하세요' },
  hasLocation: { type: Boolean, default: false },
})
defineEmits(['confirm', 'retry', 'cancel'])
</script>
