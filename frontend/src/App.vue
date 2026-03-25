<template>
  <TopBar
    :showSearch="isMainPage"
    @authClick="handleAuthClick"
    @placeSelect="handlePlaceSelect"
    @click="closeMapInfowindows"
  />
  <router-view v-slot="{ Component }">
    <component :is="Component" ref="routerViewRef" />
  </router-view>

  <!-- 로그인/회원가입 모달 (전역) -->
  <AuthModal
    :visible="showAuth"
    @close="showAuth = false"
  />
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import TopBar from './components/TopBar.vue'
import AuthModal from './components/AuthModal.vue'
import { useAuth } from './composables/useAuth.js'

const route = useRoute()
const routerViewRef = ref(null)
const { currentUser, logout } = useAuth()

const isMainPage = computed(() => route.path === '/')
const showAuth = ref(false)

function handleAuthClick() {
  if (currentUser.value) {
    logout()
  } else {
    showAuth.value = true
  }
}

function handlePlaceSelect(place) {
  if (routerViewRef.value?.handlePlaceSelect) {
    routerViewRef.value.handlePlaceSelect(place)
  }
}

function closeMapInfowindows() {
  window.__windycity_closeInfowindows?.()
}
</script>
