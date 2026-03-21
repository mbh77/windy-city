<template>
  <TopBar
    :showSearch="isMainPage"
    @authClick="handleAuthClick"
    @placeSelect="handlePlaceSelect"
  />
  <router-view
    ref="routerViewRef"
    @authClick="handleAuthClick"
    @placeSelect="handlePlaceSelect"
  />
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import TopBar from './components/TopBar.vue'

const route = useRoute()
const routerViewRef = ref(null)

const isMainPage = computed(() => route.path === '/')

function handleAuthClick() {
  // MainView의 authClick 처리로 전달
  if (routerViewRef.value?.handleAuthClick) {
    routerViewRef.value.handleAuthClick()
  }
}

function handlePlaceSelect(place) {
  if (routerViewRef.value?.handlePlaceSelect) {
    routerViewRef.value.handlePlaceSelect(place)
  }
}
</script>
