import { ref } from 'vue'
import { apiFetch } from '@/utils/api.js'

export function useImageUpload(maxCount = 5) {
  const uploadedImages = ref([])
  const uploadError = ref('')
  let existingMedia = []

  async function handleImageUpload(e) {
    const file = e.target.files[0]
    if (!file) return
    uploadError.value = ''

    const maxSize = file.type === 'image/png' ? 10 * 1024 * 1024 : 3 * 1024 * 1024
    if (file.size > maxSize) {
      uploadError.value = file.type === 'image/png'
        ? 'PNG 파일은 10MB 이하만 가능합니다'
        : 'JPG/WEBP 파일은 3MB 이하만 가능합니다'
      e.target.value = ''
      return
    }

    const fd = new FormData()
    fd.append('file', file)
    const res = await apiFetch('/api/upload/image', { method: 'POST', body: fd })
    if (res.ok) {
      const data = await res.json()
      uploadedImages.value.push({ url: data.url })
    } else {
      const err = await res.json()
      uploadError.value = err.detail || '업로드에 실패했습니다'
    }
    e.target.value = ''
  }

  function removeImage(idx) {
    uploadedImages.value.splice(idx, 1)
  }

  function setExistingMedia(media) {
    existingMedia = media || []
    uploadedImages.value = existingMedia
      .filter(m => m.media_type === 'image')
      .map(m => ({ id: m.id, url: m.url }))
  }

  async function saveMedia(entityType, entityId) {
    // 삭제된 기존 이미지 제거
    const currentIds = uploadedImages.value.filter(img => img.id).map(img => img.id)
    for (const m of existingMedia) {
      if (!currentIds.includes(m.id)) {
        await apiFetch(`/api/${entityType}/${entityId}/media/${m.id}`, { method: 'DELETE' })
      }
    }
    // 새로 추가된 이미지 등록
    const newImages = uploadedImages.value.filter(img => !img.id)
    for (let i = 0; i < newImages.length; i++) {
      await apiFetch(`/api/${entityType}/${entityId}/media`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ media_type: 'image', url: newImages[i].url, sort_order: i }),
      })
    }
  }

  return { uploadedImages, uploadError, handleImageUpload, removeImage, setExistingMedia, saveMedia }
}
