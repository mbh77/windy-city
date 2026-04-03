<template>
  <div class="category-bar" @mousedown.stop @touchstart.stop>
    <button
      v-for="cat in categories"
      :key="cat.key"
      :class="['cat-chip', { active: visibleCategories[cat.key]}]"
      :style="chipStyle(cat)"
      @click="$emit('toggle', cat.key)"
    >
      {{  cat.label }}
    </button>
    <span class="cat-divider">|</span>
    <button
      v-for="et in eventTypes"
      :key="et.value"
      :class="['cat-chip', 'event-type-chip', { active: selectedEventTypes.includes(et.value) }]"
      @click="$emit('toggleEventType', et.value)"
    >
      {{ et.label }}
    </button>
  </div>
</template>

<script setup>
import { MAP_CATEGORIES, TYPE_OPTIONS } from '../utils/constants';

defineProps({
  visibleCategories: { type: Object, required: true },
  selectedEventTypes: { type: Array, default: () => [] },
})
defineEmits(['toggle', 'toggleEventType'])

const categories = MAP_CATEGORIES
const eventTypes = TYPE_OPTIONS

function chipStyle(cat) {
  return {
    '--chip-color': cat.color,
  }
}

</script>