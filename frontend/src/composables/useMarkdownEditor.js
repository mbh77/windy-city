import { ref, nextTick } from 'vue'
import { apiFetch } from '@/utils/api.js'

export function useMarkdownEditor(getContent, setContent) {
  const descPreview = ref(false)
  const descArea = ref(null)
  const descImageInput = ref(null)
  const showVideoDialog = ref(false)
  const videoUrl = ref('')

  function insertAtCursor(before, after = '') {
    const ta = descArea.value
    if (!ta) return
    const content = getContent()
    const start = ta.selectionStart
    const end = ta.selectionEnd
    const selected = content.substring(start, end)
    setContent(content.substring(0, start) + before + (selected || '') + after + content.substring(end))
    const cursorPos = start + before.length + (selected || '').length
    nextTick(() => { ta.focus(); ta.setSelectionRange(cursorPos, cursorPos) })
  }

  function insertBold() { insertAtCursor('**', '**') }
  function insertItalic() { insertAtCursor('*', '*') }
  function insertLink() { insertAtCursor('[링크 텍스트](', ')') }
  function triggerDescImage() { descImageInput.value?.click() }

  async function uploadDescImage(e) {
    const file = e.target.files[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    const res = await apiFetch('/api/upload/image', { method: 'POST', body: fd })
    if (res.ok) {
      const data = await res.json()
      insertAtCursor(`![이미지](${data.url})`)
    } else {
      alert('이미지 업로드에 실패했습니다')
    }
    e.target.value = ''
  }

  function insertVideo() {
    if (videoUrl.value.trim()) {
      insertAtCursor(videoUrl.value.trim() + '\n')
      videoUrl.value = ''
      showVideoDialog.value = false
    }
  }

  return {
    descPreview, descArea, descImageInput, showVideoDialog, videoUrl,
    insertBold, insertItalic, insertLink, triggerDescImage, uploadDescImage, insertVideo,
  }
}
