<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/" class="page-nav-btn" title="지도">지도</router-link>
      <h1 class="page-title">바람난 도시</h1>
    </header>

    <main class="page-body">
      <section class="about-section">
        <h2>서비스 소개</h2>
        <p>바람난 도시는 살사, 바차타, 스윙, 탱고 등 커플댄스 커뮤니티를 위한 지도 기반 이벤트·장소 탐색 서비스입니다.</p>
      </section>

      <section class="about-section">
        <h2>이용약관</h2>
        <div class="about-text">
          <h3>제1조 (목적)</h3>
          <p>이 약관은 바람난 도시(이하 "서비스")의 이용과 관련하여 운영자와 이용자 간의 권리, 의무 및 책임사항을 규정합니다.</p>

          <h3>제2조 (서비스 내용)</h3>
          <p>서비스는 커플댄스(살사, 바차타, 스윙, 탱고 등) 관련 이벤트 및 장소 정보를 지도 기반으로 제공합니다. 서비스는 무료로 제공되며, 운영자는 서비스 내용을 변경하거나 중단할 수 있습니다.</p>

          <h3>제3조 (회원가입 및 계정)</h3>
          <p>이용자는 이메일과 닉네임으로 회원가입할 수 있습니다. 이용자는 정확한 정보를 제공해야 하며, 타인의 정보를 도용해서는 안 됩니다. 계정은 본인만 사용할 수 있으며, 관리 책임은 이용자에게 있습니다.</p>

          <h3>제4조 (이용자의 의무)</h3>
          <p>이용자는 다음 행위를 해서는 안 됩니다.</p>
          <ul>
            <li>허위 정보 등록</li>
            <li>타인의 권리를 침해하는 콘텐츠 게시</li>
            <li>서비스의 정상 운영을 방해하는 행위</li>
            <li>서비스를 상업적 목적으로 무단 이용하는 행위</li>
          </ul>

          <h3>제5조 (콘텐츠 관리)</h3>
          <p>이용자가 등록한 이벤트, 장소, 이미지 등의 콘텐츠에 대한 책임은 등록한 이용자에게 있습니다. 운영자는 약관을 위반하거나 부적절한 콘텐츠를 사전 통보 없이 삭제할 수 있습니다.</p>

          <h3>제6조 (책임 제한)</h3>
          <p>서비스는 무료로 제공되며, 운영자는 서비스 이용으로 발생하는 어떠한 손해에 대해서도 책임을 지지 않습니다. 이벤트 및 장소 정보의 정확성은 등록자에게 책임이 있으며, 운영자는 이를 보증하지 않습니다.</p>

          <h3>제7조 (약관 변경)</h3>
          <p>운영자는 필요한 경우 약관을 변경할 수 있으며, 변경된 약관은 서비스 내 공지를 통해 효력이 발생합니다.</p>

          <p class="about-date">시행일: 2026년 3월 19일</p>
        </div>
      </section>

      <section class="about-section">
        <h2>개인정보처리방침</h2>
        <div class="about-text">
          <h3>1. 수집하는 개인정보</h3>
          <p>서비스는 회원가입 및 서비스 제공을 위해 다음 정보를 수집합니다.</p>
          <ul>
            <li>필수: 이메일 주소, 닉네임, 비밀번호(암호화 저장)</li>
            <li>선택: 제보/제안 시 입력하는 이름, 이메일</li>
          </ul>

          <h3>2. 개인정보의 이용 목적</h3>
          <ul>
            <li>회원 식별 및 가입 의사 확인</li>
            <li>이메일 인증을 통한 본인 확인</li>
            <li>이벤트·장소 등록자 표시</li>
            <li>서비스 관련 공지 및 문의 응답</li>
          </ul>

          <h3>3. 개인정보의 보유 및 파기</h3>
          <p>회원 탈퇴 시 개인정보는 즉시 파기합니다. 단, 관련 법령에 의해 보존이 필요한 경우 해당 기간 동안 보관합니다.</p>

          <h3>4. 개인정보의 제3자 제공</h3>
          <p>서비스는 이용자의 개인정보를 제3자에게 제공하지 않습니다. 단, 법령에 의한 요청이 있는 경우 예외로 합니다.</p>

          <h3>5. 쿠키 및 자동 수집 정보</h3>
          <p>서비스는 로그인 상태 유지를 위해 브라우저 로컬 스토리지를 사용합니다. 별도의 쿠키는 수집하지 않습니다.</p>

          <h3>6. 개인정보 보호 책임자</h3>
          <p>문의: bh.min@live.co.kr</p>

          <p class="about-date">시행일: 2026년 3월 19일</p>
        </div>
      </section>

      <section class="about-section">
        <h2>위치기반서비스 이용약관</h2>
        <div class="about-text">
          <h3>1. 목적</h3>
          <p>본 약관은 서비스에서 제공하는 위치기반서비스의 이용 조건을 규정합니다.</p>

          <h3>2. 위치정보의 이용</h3>
          <p>서비스는 이용자의 현재 위치를 활용하여 주변 댄스 이벤트 및 장소를 검색하는 기능을 제공합니다. 위치 정보는 이용자가 명시적으로 허용한 경우에만 사용됩니다.</p>

          <h3>3. 위치정보의 저장</h3>
          <p>이용자의 위치 정보는 서버에 저장되지 않으며, 검색 요청 시 1회성으로만 사용됩니다.</p>

          <h3>4. 위치정보 이용의 거부</h3>
          <p>이용자는 브라우저 설정을 통해 위치 정보 제공을 거부할 수 있으며, 이 경우 위치 기반 검색 기능을 제외한 나머지 서비스는 정상적으로 이용 가능합니다.</p>

          <p class="about-date">시행일: 2026년 3월 19일</p>
        </div>
      </section>

      <section class="about-section">
        <h2>운영자 정보</h2>
        <div class="about-text">
          <p>서비스명: 바람난 도시</p>
          <p>운영자: 민병훈</p>
          <p>이메일: bh.min@live.co.kr</p>
          <p>웹사이트: https://windycity.co.kr</p>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.page-body { display: flex; flex-direction: column; gap: 24px; }
.about-section { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 20px; }
.about-section h2 { font-size: 1rem; margin-bottom: 10px; color: #e0e0e0; }
.about-section p { font-size: 0.85rem; color: #aaa; line-height: 1.6; }
.about-text h3 { font-size: 0.9rem; color: #ccc; margin-top: 14px; margin-bottom: 6px; }
.about-text ul { font-size: 0.85rem; color: #aaa; line-height: 1.6; padding-left: 20px; margin: 4px 0; }
.about-text li { margin-bottom: 2px; }
.about-date { margin-top: 14px; font-size: 0.8rem; color: #666; }
</style>