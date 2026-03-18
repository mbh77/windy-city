<template>
  <div class="about-page">
    <header class="about-header">
      <router-link to="/" class="about-back">← 지도로 돌아가기</router-link>
      <h1 class="about-logo">바람난 도시</h1>
    </header>

    <main class="about-content">
      <section class="about-section">
        <h2>서비스 소개</h2>
        <p>바람난 도시는 살사, 바차타, 스윙, 탱고 등 커플댄스 커뮤니티를 위한 지도 기반 이벤트·장소 탐색 서비스입니다.</p>
      </section>

      <section class="about-section">
        <h2>이용약관</h2>
        <p>준비 중입니다.</p>
      </section>

      <section class="about-section">
        <h2>개인정보처리방침</h2>
        <p>준비 중입니다.</p>
      </section>

      <section class="about-section">
        <h2>사업자 정보</h2>
        <p>준비 중입니다.</p>
      </section>
    </main>
  </div>
</template>

<style scoped>
.about-page { min-height: 100vh; background: #0f0f0f; color: #e0e0e0; padding: 20px; max-width: 720px; margin: 0 auto; }
.about-header { display: flex; align-items: center; gap: 16px; margin-bottom: 32px; }
.about-back { color: #aaa; text-decoration: none; font-size: 0.85rem; }
.about-back:hover { color: #fff; }
.about-logo { font-size: 1.3rem; font-weight: 700; color: #ff6b6b; }
.about-content { display: flex; flex-direction: column; gap: 24px; }
.about-section { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 20px; }
.about-section h2 { font-size: 1rem; margin-bottom: 10px; color: #e0e0e0; }
.about-section p { font-size: 0.85rem; color: #aaa; line-height: 1.6; }
</style>