<template>
  <div class="page-container" style="display:flex;align-items:center;justify-content:center;min-height:60vh;">
    <div v-if="error" style="text-align:center;">
      <p style="color:#D4725C;margin-bottom:16px;">{{ error }}</p>
      <button class="btn-primary" @click="$router.push('/')">홈으로 돌아가기</button>
    </div>
    <div v-else style="text-align:center;">
      <p style="color:#8B7B6B;">로그인 처리 중...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'

const route = useRoute()
const router = useRouter()
const { socialLogin } = useAuth()
const error = ref('')

onMounted(async () => {
  const provider = route.params.provider // kakao or naver
  const code = route.query.code

  if (!code) {
    error.value = '인증 코드가 없습니다'
    return
  }

  const redirectUri = `${window.location.origin}/auth/${provider}/callback`
  const result = await socialLogin(provider, code, redirectUri)

  if (result.ok) {
    router.push('/')
  } else if (result.needRegister) {
    // 신규 가입 → 닉네임 입력 필요, 소셜 정보를 쿼리로 전달
    router.push({
      name: 'socialRegister',
      query: {
        provider: result.socialData.provider,
        provider_id: result.socialData.provider_id,
        email: result.socialData.email,
        nickname: result.socialData.nickname,
      },
    })
  } else {
    error.value = result.error || '소셜 로그인에 실패했습니다'
  }
})
</script>
