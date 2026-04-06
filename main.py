from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os
import re

from database import engine
import models
from routers import auth, events, venues, search, upload, feedback, admin, posts, health

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Windy City", description="살사 댄스 강습·행사 지도 서비스")

# CORS 설정 (개발 중 모든 origin 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(venues.router)
app.include_router(search.router)
app.include_router(upload.router)
app.include_router(feedback.router)
app.include_router(admin.router)
app.include_router(posts.router)
app.include_router(health.router)

# ── robots.txt ──
@app.get("/robots.txt")
async def robots_txt():
    content = """User-agent: *
Allow: /
Disallow: /admin

Sitemap: https://windycity.co.kr/sitemap.xml
"""
    return HTMLResponse(content, media_type="text/plain")


# ── sitemap.xml (동적 생성) ──
@app.get("/sitemap.xml")
async def sitemap_xml():
    from database import SessionLocal
    from datetime import datetime

    db = SessionLocal()
    try:
        urls = []

        # 고정 페이지
        static_pages = [
            {"loc": "/", "priority": "1.0", "changefreq": "daily"},
            {"loc": "/events", "priority": "0.9", "changefreq": "daily"},
            {"loc": "/venues", "priority": "0.8", "changefreq": "weekly"},
            {"loc": "/board", "priority": "0.7", "changefreq": "daily"},
            {"loc": "/about", "priority": "0.3", "changefreq": "monthly"},
        ]
        for p in static_pages:
            urls.append(
                f'  <url>\n'
                f'    <loc>https://windycity.co.kr{p["loc"]}</loc>\n'
                f'    <changefreq>{p["changefreq"]}</changefreq>\n'
                f'    <priority>{p["priority"]}</priority>\n'
                f'  </url>'
            )

        # 이벤트
        all_events = db.query(models.Event.id, models.Event.updated_at).all()
        for eid, updated in all_events:
            lastmod = updated.strftime("%Y-%m-%d") if updated else datetime.now().strftime("%Y-%m-%d")
            urls.append(
                f'  <url>\n'
                f'    <loc>https://windycity.co.kr/events/{eid}</loc>\n'
                f'    <lastmod>{lastmod}</lastmod>\n'
                f'    <changefreq>weekly</changefreq>\n'
                f'    <priority>0.8</priority>\n'
                f'  </url>'
            )

        # 장소
        all_venues = db.query(models.Venue.id, models.Venue.updated_at).all()
        for vid, updated in all_venues:
            lastmod = updated.strftime("%Y-%m-%d") if updated else datetime.now().strftime("%Y-%m-%d")
            urls.append(
                f'  <url>\n'
                f'    <loc>https://windycity.co.kr/venues/{vid}</loc>\n'
                f'    <lastmod>{lastmod}</lastmod>\n'
                f'    <changefreq>weekly</changefreq>\n'
                f'    <priority>0.7</priority>\n'
                f'  </url>'
            )

        # 게시글
        all_posts = db.query(models.Post.id, models.Post.updated_at).all()
        for pid, updated in all_posts:
            lastmod = updated.strftime("%Y-%m-%d") if updated else datetime.now().strftime("%Y-%m-%d")
            urls.append(
                f'  <url>\n'
                f'    <loc>https://windycity.co.kr/board/{pid}</loc>\n'
                f'    <lastmod>{lastmod}</lastmod>\n'
                f'    <changefreq>monthly</changefreq>\n'
                f'    <priority>0.5</priority>\n'
                f'  </url>'
            )

        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n"
            '</urlset>'
        )
        return HTMLResponse(xml, media_type="application/xml")
    finally:
        db.close()


# 업로드 이미지 서빙 (빌드와 분리)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 정적 파일 서빙 (프론트엔드)
app.mount("/static-files", StaticFiles(directory="static"), name="static")

# ── 봇 감지 + 메타태그 동적 생성 (SEO) ──

BOT_USER_AGENTS = re.compile(
    r"googlebot|bingbot|yandexbot|slurp|duckduckbot|baiduspider|"
    r"facebookexternalhit|twitterbot|kakaotalk-scrap|line-poker|"
    r"telegrambot|discordbot|slackbot|linkedinbot|pinterestbot",
    re.IGNORECASE,
)

VENUE_TYPE_KO = {"club": "댄스바", "academy": "동호회", "practice_room": "연습실"}
EVENT_TYPE_KO = {
    "social": "소셜파티", "workshop": "워크샵", "festival": "페스티벌",
    "regular_class": "강습", "performance": "공연", "practice": "연습", "other": "기타",
}
GENRE_KO = {
    "salsa": "살사", "bachata": "바차타", "kizomba": "키좀바", "zouk": "주크",
    "tango": "탱고", "merengue": "메렝게", "lindy_hop": "린디합", "balboa": "발보아",
    "blues": "블루스", "west_coast_swing": "웨스트코스트스윙", "other": "기타",
}
SEO_KEYWORDS = "라틴댄스, 소셜댄스, 커플댄스, 살사, 바차타, 키좀바, 스윙, 린디합, 탱고, 발보아, 블루스"

def _escape(text: str) -> str:
    """HTML 메타태그용 이스케이프"""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

def _strip_markup(text: str) -> str:
    """HTML 태그 + 마크다운 문법 제거 → 순수 텍스트"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)                  # HTML 태그
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)     # 이미지 ![alt](url)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text) # 링크 [text](url)
    text = re.sub(r'[*_~`#>]+', '', text)                # 마크다운 기호
    text = re.sub(r'\n+', ' ', text)                     # 줄바꿈 → 공백
    text = re.sub(r'\s+', ' ', text).strip()             # 다중 공백 정리
    return text

def _build_meta_html(title: str, description: str, url: str, image: str = "", body_content: str = "") -> str:
    """index.html의 <head>에 메타태그를 교체하고, body_content가 있으면 본문에 삽입"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        return ""

    title = _escape(title)
    description = _escape(description[:200]) if description else ""
    full_url = f"https://windycity.co.kr/{url.lstrip('/')}"
    image = image or "https://windycity.co.kr/og-image.jpg"

    # 기존 메타태그 교체
    html = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', html)
    html = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{description}">', html)
    html = re.sub(r'<meta property="og:title"[^>]*>', f'<meta property="og:title" content="{title}">', html)
    html = re.sub(r'<meta property="og:description"[^>]*>', f'<meta property="og:description" content="{description}">', html)
    html = re.sub(r'<meta property="og:url"[^>]*>', f'<meta property="og:url" content="{full_url}">', html)
    html = re.sub(r'<meta property="og:image"[^>]*>', f'<meta property="og:image" content="{image}">', html)

    # 봇용 본문 콘텐츠 삽입 (SEO)
    if body_content:
        html = html.replace(
            '<div id="app"></div>',
            f'<div id="app"></div>\n<div id="bot-content" style="display:none">{body_content}</div>'
        )

    return html

def _get_bot_response(full_path: str):
    """봇용 메타태그 + 본문 HTML 생성. 해당 경로가 아니면 None 반환."""
    from database import SessionLocal
    import models

    # /events/123 — 이벤트 상세
    m = re.match(r"events/(\d+)$", full_path)
    if m:
        db = SessionLocal()
        try:
            event = db.query(models.Event).filter(models.Event.id == int(m.group(1))).first()
            if not event:
                return None
            media = db.query(models.Media).filter(
                models.Media.entity_type == "event", models.Media.entity_id == event.id
            ).order_by(models.Media.sort_order).first()
            image = f"https://windycity.co.kr{media.url}" if media else ""

            type_ko = EVENT_TYPE_KO.get(event.event_type, "")
            date_str = event.event_date.strftime("%Y-%m-%d") if event.event_date else ""
            title = f"{event.title} - 바람난 도시"
            desc_parts = []
            if type_ko:
                desc_parts.append(type_ko)
            if date_str:
                desc_parts.append(date_str)
            if event.location_name:
                desc_parts.append(event.location_name)
            desc = " · ".join(desc_parts)
            if event.description:
                plain = _strip_markup(event.description)
                desc += f" | {plain[:150]}"

            # 봇용 본문
            genres = db.query(models.EventDanceGenre).filter(models.EventDanceGenre.event_id == event.id).all()
            genres_ko = ", ".join(GENRE_KO.get(g.dance_genre.value if hasattr(g.dance_genre, 'value') else g.dance_genre, "") for g in genres)

            body = f"<h1>{_escape(event.title)}</h1>"
            body += f"<p>{_escape(type_ko)} · {_escape(date_str)}</p>"
            if genres_ko:
                body += f"<p>장르: {_escape(genres_ko)}</p>"
            if event.location_name:
                body += f"<p>장소: {_escape(event.location_name)}</p>"
            if event.address:
                body += f"<p>주소: {_escape(event.address)}</p>"
            if event.description:
                body += f"<p>{_escape(_strip_markup(event.description)[:500])}</p>"

            return _build_meta_html(title, desc, full_path, image, body)
        finally:
            db.close()

    # /venues/123 — 장소 상세
    m = re.match(r"venues/(\d+)$", full_path)
    if m:
        db = SessionLocal()
        try:
            venue = db.query(models.Venue).filter(models.Venue.id == int(m.group(1))).first()
            if not venue:
                return None
            media = db.query(models.Media).filter(
                models.Media.entity_type == "venue", models.Media.entity_id == venue.id
            ).order_by(models.Media.sort_order).first()
            image = f"https://windycity.co.kr{media.url}" if media else ""

            type_ko = VENUE_TYPE_KO.get(venue.venue_type, "")
            title = f"{venue.name} - 바람난 도시"
            desc_parts = []
            if type_ko:
                desc_parts.append(type_ko)
            if venue.address:
                desc_parts.append(venue.address)
            desc = " · ".join(desc_parts)
            if venue.description:
                plain = _strip_markup(venue.description)
                desc += f" | {plain[:150]}"

            # 봇용 본문
            genres = db.query(models.VenueDanceGenre).filter(models.VenueDanceGenre.venue_id == venue.id).all()
            genres_ko = ", ".join(GENRE_KO.get(g.dance_genre.value if hasattr(g.dance_genre, 'value') else g.dance_genre, "") for g in genres)

            body = f"<h1>{_escape(venue.name)}</h1>"
            body += f"<p>{_escape(type_ko)}</p>"
            if genres_ko:
                body += f"<p>장르: {_escape(genres_ko)}</p>"
            if venue.address:
                body += f"<p>주소: {_escape(venue.address)}</p>"
            if venue.description:
                body += f"<p>{_escape(_strip_markup(venue.description)[:500])}</p>"

            return _build_meta_html(title, desc, full_path, image, body)
        finally:
            db.close()

    # /board/123 — 게시글 상세
    m = re.match(r"board/(\d+)$", full_path)
    if m:
        db = SessionLocal()
        try:
            post = db.query(models.Post).filter(models.Post.id == int(m.group(1))).first()
            if not post:
                return None
            title = f"{post.title} - 바람난 도시"
            desc = ""
            if post.content:
                plain = _strip_markup(post.content)
                desc = plain[:200]

            # 봇용 본문
            body = f"<h1>{_escape(post.title)}</h1>"
            if post.content:
                body += f"<p>{_escape(_strip_markup(post.content)[:1000])}</p>"

            return _build_meta_html(title, desc, full_path, body_content=body)
        finally:
            db.close()

    # / — 메인 페이지
    if full_path == "" or full_path == "/":
        title = "바람난 도시 - 라틴댄스·스윙·탱고 강습·행사·동호회 지도"
        desc = f"{SEO_KEYWORDS} 강습·행사와 동호회, 댄스바를 지도에서 한눈에 찾아보세요."
        body = (
            "<h1>바람난 도시 - 댄스 강습·행사·동호회 지도</h1>"
            f"<p>{SEO_KEYWORDS} 강습, 행사, 파티 일정과 동호회, 댄스바, 연습실을 지도에서 찾아보세요.</p>"
            "<p>바람난 도시는 커플댄스 커뮤니티를 위한 지도 기반 탐색 서비스입니다. "
            "인스타그램, 네이버 카페, 카카오채널에 흩어진 댄스 강습·행사·장소 정보를 하나의 플랫폼에서 확인하세요.</p>"
            '<p><a href="/events">강습·행사 보기</a> · <a href="/venues">동호회·댄스바·연습실 보기</a> · <a href="/board">게시판</a></p>'
        )
        return _build_meta_html(title, desc, full_path, body_content=body)

    # /events — 이벤트 목록
    if full_path == "events":
        db = SessionLocal()
        try:
            events = db.query(models.Event).order_by(models.Event.event_date.desc()).limit(50).all()
            title = "라틴댄스·스윙·탱고 강습·행사 - 바람난 도시"
            desc = f"{SEO_KEYWORDS} 강습, 워크샵, 소셜파티, 페스티벌 일정을 찾아보세요."

            body = f"<h1>강습·행사 목록</h1>"
            body += f"<p>{SEO_KEYWORDS} 강습, 워크샵, 소셜파티, 페스티벌 일정을 한눈에 확인하세요.</p><ul>"
            for e in events:
                type_ko = EVENT_TYPE_KO.get(e.event_type, "")
                date_str = e.event_date.strftime("%Y-%m-%d") if e.event_date else ""
                body += f'<li><a href="/events/{e.id}">{_escape(e.title)}</a> · {_escape(type_ko)} · {_escape(date_str)}'
                if e.location_name:
                    body += f" · {_escape(e.location_name)}"
                body += "</li>"
            body += "</ul>"

            return _build_meta_html(title, desc, full_path, body_content=body)
        finally:
            db.close()

    # /venues — 장소 목록
    if full_path == "venues":
        db = SessionLocal()
        try:
            venues = db.query(models.Venue).order_by(models.Venue.created_at.desc()).limit(50).all()
            title = "라틴댄스·스윙·탱고 동호회·댄스바·연습실 - 바람난 도시"
            desc = f"{SEO_KEYWORDS} 동호회, 댄스바, 연습실을 찾아보세요."

            body = f"<h1>동호회·댄스바·연습실 목록</h1>"
            body += f"<p>{SEO_KEYWORDS} 동호회, 댄스바, 연습실 정보를 확인하세요.</p><ul>"
            for v in venues:
                type_ko = VENUE_TYPE_KO.get(v.venue_type, "")
                body += f'<li><a href="/venues/{v.id}">{_escape(v.name)}</a> · {_escape(type_ko)}'
                if v.address:
                    body += f" · {_escape(v.address)}"
                body += "</li>"
            body += "</ul>"

            return _build_meta_html(title, desc, full_path, body_content=body)
        finally:
            db.close()

    # /board — 게시판 목록
    if full_path == "board":
        db = SessionLocal()
        try:
            posts = db.query(models.Post).order_by(models.Post.created_at.desc()).limit(50).all()
            title = "게시판 - 바람난 도시"
            desc = "바람난 도시 커뮤니티 게시판입니다."

            body = "<h1>게시판</h1><ul>"
            for p in posts:
                date_str = p.created_at.strftime("%Y-%m-%d") if p.created_at else ""
                body += f'<li><a href="/board/{p.id}">{_escape(p.title)}</a> · {_escape(date_str)}</li>'
            body += "</ul>"

            return _build_meta_html(title, desc, full_path, body_content=body)
        finally:
            db.close()

    return None


# SPA fallback: 정적 파일이 있으면 반환, 없으면 index.html 반환
@app.get("/{full_path:path}")
async def spa_fallback(request: Request, full_path: str):
    file_path = os.path.join("static", full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # 봇이면 메타태그 삽입된 HTML 반환
    ua = request.headers.get("user-agent", "")
    if BOT_USER_AGENTS.search(ua):
        bot_html = _get_bot_response(full_path)
        if bot_html:
            return HTMLResponse(bot_html)

    return FileResponse("static/index.html")
