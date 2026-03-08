<template>
  <header class="topbar">
    <div class="logo">🌀 Windy City</div>
    <div class="filters">
      <input type="date" v-model="filterDate" />
      <select v-model="filterType">
        <option value="">전체 유형</option>
        <option v-for="opt in TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
      <select v-model="filterGenre">
        <option value="">전체 장르</option>
        <option v-for="opt in GENRE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
      <button class="btn-primary" @click="handleSearch">검색</button>
    </div>
    <div class="auth-area">
      <button class="btn-ghost" @click="$emit('authClick')">
        {{ currentUser ? `${currentUser.nickname} 로그아웃` : '로그인' }}
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { TYPE_OPTIONS, GENRE_OPTIONS } from '../utils/constants.js'
import { useAuth } from '../composables/useAuth.js'

const emit = defineEmits(['search', 'authClick'])
const { currentUser } = useAuth()

const filterDate = ref('')
const filterType = ref('')
const filterGenre = ref('')

function handleSearch() {
  emit('search', {
    date: filterDate.value,
    eventType: filterType.value,
    danceGenre: filterGenre.value,
  })
}
</script>
