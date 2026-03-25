import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({ breaks: true })

function embedYouTube(html) {
  const ytRegex = /<a[^>]*href="https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]+)[^"]*"[^>]*>[^<]*<\/a>/g
  html = html.replace(ytRegex, (match, id) => {
    return `<div class="embed-video"><iframe src="https://www.youtube.com/embed/${id}" frameborder="0" allowfullscreen></iframe></div>`
  })
  const ytTextRegex = /(?:<p>)?(https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]+)[^\s<]*)(?:<\/p>)?/g
  html = html.replace(ytTextRegex, (match, url, id) => {
    if (match.includes('<iframe')) return match
    return `<div class="embed-video"><iframe src="https://www.youtube.com/embed/${id}" frameborder="0" allowfullscreen></iframe></div>`
  })
  return html
}

function embedInstagram(html) {
  const igRegex = /(?:<a[^>]*href=")?https?:\/\/(?:www\.)?instagram\.com\/(p|reel)\/([a-zA-Z0-9_-]+)\/?[^"<\s]*"?[^<]*(?:<\/a>)?/g
  html = html.replace(igRegex, (match, type, code) => {
    return `<div class="embed-video"><iframe src="https://www.instagram.com/${type}/${code}/embed" frameborder="0" scrolling="no"></iframe></div>`
  })
  return html
}

export function renderMarkdown(content) {
  if (!content) return ''
  // 연속 빈 줄을 보존: 3개 이상 줄바꿈 → 빈 줄마다 <br> 삽입
  content = content.replace(/\n{3,}/g, (match) => '\n\n' + '<br>\n'.repeat(match.length - 1))
  let html = marked(content)
  html = embedYouTube(html)
  html = embedInstagram(html)
  return DOMPurify.sanitize(html, {
    ADD_TAGS: ['iframe'],
    ADD_ATTR: ['allowfullscreen', 'frameborder', 'src', 'scrolling'],
  })
}
