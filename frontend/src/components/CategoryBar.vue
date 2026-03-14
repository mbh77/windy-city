<template>
  <div class="category-bar">
    <button
      v-for="cat in categories"
      :key="cat.key"
      :class="['cat-chip', { active: visibleCategories[cat.key]}]"
      :style="chipStyle(cat)"
      @click="$emit('toggle', cat.key)"
    >
      {{  cat.label }}
    </button>
  </div>
</template>

<script setup>
import { MAP_CATEGORIES } from '../utils/constants';

defineProps({
  visibleCategories: { type: Object, required: true }
})
defineEmits(['toggle'])

const categories = MAP_CATEGORIES

function chipStyle(cat) {
  return {
    '--chip-color': cat.color,
  }
}

</script>