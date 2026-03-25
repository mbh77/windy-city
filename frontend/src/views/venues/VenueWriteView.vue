<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn">지도</router-link>
      <a class="page-nav-btn" @click="$router.back()">뒤로</a>
      <h1 class="page-title">{{ editMode ? '장소 수정' : '장소 등록' }}</h1>
    </header>

    <main class="page-body">
      <p>장소 등록 페이지 (준비 중)</p>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const editMode = computed(() => !!route.params.id)
</script>
