# Production promotion — 2026-09-10

사용자가 디자인 초안을 승인하고 커밋·푸시를 통한 즉시 운영 적용을 요청했다.
새 호스팅 서비스로 이전하지 않고 기존 GitHub Pages / vramlab.com을 유지한다.

## 운영 설정

- `hugo.yaml`: `theme: [LabDraft, PaperMod]`, `params.labDraft: false`.
  디렉토리명 `LabDraft`는 최초 초안 이름을 유지하지만 현재 운영 테마다.
- React 없이 Hugo + 로컬 Three.js 0.186.0. PaperMod는 검색/SEO 등 공유 자원을
  제공하는 고정된 보조 테마다. 서브모듈 버전은 바꾸지 않았다.
- 운영 화면의 초안 배너와 `Design draft` 제목을 제거한다.
- 홈·보고서·주제 안내는 `index, follow`. 검색·태그·카테고리는 기존대로
  `noindex, follow`와 사이트맵 제외를 유지한다. robots.txt는 전체 크롤링을
  막지 않으며 운영 사이트맵 주소를 제공한다.
- 기존 Cloudflare 방문 분석, Open Graph, X 카드, BlogPosting 범위, RSS를 유지한다.
- 기존 7편의 본문/코드/표/URL/공개 증거는 수정하지 않았다. M4는 사용 가능한
  장비이며 실험 결과가 없다는 표시를 유지한다.
- Archify HTML은 최초 수락된 바이트 그대로다. 한국어 주석과 영어 Viewer UI도
  검토한 초안 그대로 유지했다.

## 검토 모드

`hugo server --config hugo.yaml,hugo.draft.yaml`은 같은 디자인에 초안 배너와
검색 차단을 켜고 방문 분석을 끈다. 이 설정이나 `.draft-build` 출력물을
발행하지 않는다. 운영 배포는 기본 `hugo.yaml`과 깨끗한 `public/` 빌드를 쓴다.

## 배포 게이트

```powershell
hugo --minify --baseURL https://vramlab.com/
python scripts/lint_content.py
python scripts/check_production.py public
```

`check_production.py`는 표준 라이브러리만 사용하며 minify 여부와 무관하게
실제 HTML 메타데이터, canonical, 사이트맵, RSS, 로컬 참조, 초안 유출,
Three.js 상대 import, Archify 고정 해시를 검사한다.
GitHub Checks와 Pages 빌드 모두 이 검사를 실행한다. Pages 검사 실패 시
artifact 업로드/배포까지 진행하지 않는다.

두 모드를 함께 확인하려면 기존 `scripts/check_design_draft.mjs`를 사용한다.
이 스크립트는 운영/검토 버전의 코드 블록과 표가 같은지도 대조한다.

## 기록의 범위

최초 디자인·Archify 검수 근거는 [README.md](README.md), 버전과 라이선스는
[THIRD_PARTY.md](THIRD_PARTY.md)에 있다. 이번 전환은 새 실험이나 측정값 추가가
아니다. 배포 성공 여부는 이 문서 작성 자체가 아니라 해당 커밋의 GitHub
Actions 완료 상태와 실제 운영 URL 응답으로 확인한다.
