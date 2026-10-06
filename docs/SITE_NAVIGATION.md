# 사이트 연결과 발행 유지 규칙

공통 release ID: `nav-2026-10-07`

`AGENTS.md` → `PROJECT_MEMORY.md` → 이 문서 → `WRITING_STYLE.md`를
먼저 읽는다. 이 문서는 방법이며 실행 결과가 아니다. 현재 완료 여부는
[구현 기록](../design/NAVIGATION_IMPLEMENTATION_2026-10-07.md)에서 확인한다.

## 연결 원본

상단 메뉴는 `hugo.yaml`의 `menu.main`이며 LabDraft가 렌더링한다.
Start here → Fixes → Compatibility → Measurements → All reports →
Search 6개를 유지한다. Measurements의 URL은 `/benchmarks/`다.
About·Contact·Privacy의 직접·하단 접근을 유지한다.

새 글은 기존 4개 안내의 선택표·섹션에 연결한다. 독립된 독자 과제와
여러 실측 보고서가 쌓이기 전에 장비·라이브러리별 허브를 늘리지 않는다.
Fixes는 디스크 확장·회수, Hugging Face 파일, CUDA 환경을 구분하며 기존
`/fixes/#disk-space-and-model-caches`를 보존한다.

## 보고서 메타데이터

```yaml
primaryHub: "/fixes"
relatedReading:
  - page: "/posts/hf-datasets-cache-wsl2"
    reason: "Hub downloads and generated Arrow files use separate cache locations."
  - page: "/posts/wsl2-sparse-vhd-cannot-compact"
    reason: "Deleting cache files and reclaiming Windows disk space are separate steps."
```

- `primaryHub`: `/start-here`, `/fixes`, `/compatibility`, `/benchmarks` 중 실제 과제에 맞는 콘텐츠 참조. 현재 9편은 3개 주제 안내에 분배했지만 Start here도 허용한다. 기본 복귀 경로이며 배타적 분류가 아니다.
- `relatedReading`: 0~2개. `page`와 비어 있지 않은 dry English `reason`을 가진 block mapping을 쓴다. 관련 대상이 없으면 `[]`다.
- `page`: 공개 보고서 또는 `/start-here`, `/fixes`, `/compatibility`, `/benchmarks`의 실제 콘텐츠 참조. `site.GetPage` 결과의 `.RelPermalink`를 렌더링한다.
- 본인·중복 목적지·주 안내와 동일 목적지·draft·미래 발행·없는 페이지·허용 밖 페이지는 제외한다.
- 다른 환경의 CUDA 글에는 GPU·드라이버 차이를 밝힌다. 다른 라이브러리 측정을 동일 조건 성능 비교로 연결하지 않는다.
- M4처럼 직접 관련 후속 글이 없으면 개수를 채우지 않는다. 같은 주 안내를 다음 읽기로 중복 출력하지 않는다.

Resize 콘텐츠 참조는 `/posts/wsl2-vhd-uncompressed-unencrypted-not-sparse`,
공개 URL은 `/posts/wsl-resize-error-0xc03a001a/`다. 명시적 slug를 보존하고
공개 URL을 파일명으로 추측하지 않는다.

`lab/report-navigation.html`이 콘텐츠 참조를 해결하고 상단
`lab/topic-return.html`, 하단 `lab/next-reading.html`이 같은 데이터를
사용한다. 템플릿이 잘못된 항목을 생략해도 원본이 올바른 것은 아니다.
검사는 원본과 렌더링된 대상·제목·이유를 대조한다. 형식을 확장할 때 검사도
함께 확장하며 지원하지 않는 탐색 형식을 조용히 무시하지 않는다.

화면 breadcrumb와 JSON-LD `BreadcrumbList`는
`lab/breadcrumb-data.html`의 같은 경로·이름을 쓴다. 보고서는 Home →
주 안내 → 보고서이며 `BlogPosting`은 보고서에만 출력한다.

홈은 Start here 첫 행동과 3개 과제 선택을 제공한다. 최신 목록은 공개
`PublishDate`순 2편, draft·미래 발행 제외다. 선정 실험 수치·주석을 새
글에 재활용하지 않는다. 전체 목록·RSS는 공개 보고서 전체를 제공한다.

## 검색과 장비 범위

검색 JSON은 공개 보고서 N편 + 안내 4개다. 현재 9+4=13은 대상 수이며
검색 결과 상한이나 최대 보고서 수가 아니다. About·Contact·Privacy Policy·
Search Collector의 `searchHidden: true`와 직접·하단 접근을 유지한다.

검색은 로딩·준비 완료·검색 결과·무결과·요청 실패를 구분한다. 오류 시
재시도·전체 보고서·Start here를 제공하며 no-JS에서도 안내 경로가 남는다.
네트워크 실패와 무결과는 실제 브라우저에서 따로 확인한다. 검색·tag/category의
기존 noindex·사이트맵 제외 정책을 유지한다. PaperMod 서브모듈 대신 LabDraft
assets/layouts 또는 저장소 override를 수정한다.

About의 M4는 16GB 공유 시스템 메모리, macOS·native arm64·Metal 범위다.
GPU 전용 VRAM으로 표현하지 않는다. Streaming의 시간·메모리를 모든
형식에 일반화하지 않는다. SVG는 원본 500×860 공간을 예약하되 CLS 개선
폭을 실측 없이 주장하지 않는다.

## 새 글 작업

1. 실제 실험·로그·재현 조건을 확정하고 `WRITING_STYLE.md`의 증거·보안·문체 기준을 따른다.
2. archetype으로 draft를 만든 뒤 제목·URL을 확정한다. 기존 발행 URL은 이동하지 않는다.
3. 주 안내와 관련 글 0~2개 및 이유를 작성한다. 실제 콘텐츠 참조·대상 발행 상태를 확인한다.
4. 관련 기존 안내 본문의 선택표·설명에 새 글을 연결한다. 모든 공개 보고서는 적어도 하나의 안내에서 연결되어야 한다.
5. 최신·전체 목록·검색 N+4·RSS가 새 공개 글을 반영하고 draft를 제외하는지 확인한다.
6. 장비·범위가 달라지면 About·메모리·검증 기준도 갱신한다. 관련 없는 실험 변경을 보존한다.
7. 아래 정적 검사와 실제 독자 과제를 실행하고 결과·미확인 범위를 기록한다. 수정·실패·미해결 문제가 있을 때만 다시 검사한다.
8. 요청 범위의 검토 경로만 커밋·푸시한다. Checks와 Pages의 공개 SHA·성공 및 실제 URL·자료·RSS·사이트맵을 확인한다.
9. 공개에는 구조·버전, 비공개에는 원본·작업 기록을 남기고 release ID·공개 버전 참조를 맞춘다.

탐색 정리에서는 기존 본문·제목·수치·코드·로그·URL을 보존한다. 별도의
재측정·내용 수정은 근거와 변경 기록을 갖춘 다른 범위로 처리한다.

## 검증 명령

Hugo 0.164.0 extended를 사용한다. 운영 배포 검증에 `-D`를 쓰거나 preview
`public/`를 업로드하지 않는다. 새 production 산출물에 다음을 실행한다.

```bash
python scripts/lint_content.py
hugo --minify --baseURL "https://vramlab.com/"
python scripts/check_production.py public
python scripts/check_navigation.py public --report .draft-checks/navigation-result.json
node scripts/check_search_runtime.cjs public .draft-checks/search-runtime-result.json
```

이번 구조 작업은 **커밋 전에** 변경 전 Git ref로 기존 9편 본문·기존
frontmatter 보존도 확인한다.

```bash
python scripts/check_navigation.py public --baseline HEAD --report .draft-checks/navigation-result.json
```

본문은 Git LF 줄바꿈 기준으로 나머지 바이트를 정확히 비교한다. 후속
정당한 내용 수정을 막지 않도록 CI는 baseline을 생략하며 JSON에 `skipped`로
명시한다. 새 커밋과 비교한 결과로 이전 변경 보존을 주장하지 않는다.

기존 production 검사는 canonical·RSS·사이트맵·로컬 참조·색인 정책을
확인한다. 탐색 검사는 원본과 HTML의 메뉴·주 안내·관련 글·안내본문 연결·
최신 목록·검색 집합·breadcrumb·BlogPosting 범위·기존 앵커·SVG 예약을
대조한다. Checks와 Pages는 production 빌드 후 탐색 검사를 실행한다.
새 draft는 공개 N을 늘리지 않으며 새 공개 글은 N+4를 자동으로 늘린다.

검색 runtime 검사는 생성된 JS와 실제 Fuse로 검색·무결과·clear·초점 처리,
HTTP/네트워크/JSON/timeout 오류·재시도를 확인한다. DOM 대역과 제어된
응답에서 실행하므로 실제 브라우저·네이티브 키보드·화면 검증은 별도로 한다.

## 실제 독자 과제

| 시작 상황 | 확인할 경로 |
|---|---|
| WSL 내부 삭제 후에도 C:가 줄지 않음 | 홈/Start here → Fixes → Sparse VHD |
| 기존 모델 캐시 이동 | Start here/Fixes → 모델 캐시 → Datasets 파일·공간 회수 구분 |
| HF_DATASETS_CACHE 밖에 파일이 남음 | Fixes → Datasets 캐시 → Streaming 적용 범위 |
| resize 0xc03a001a | 검색 또는 Fixes → resize 보고서; 축소와 구분 |
| CUDA False 또는 탐지 뒤 연산 실패 | Compatibility → 실패 단계 보고서 → 실제 연산·환경 |
| M4 긴 프롬프트 첫 응답·메모리 | Measurements → M4 → 지표·조건 |

실제 브라우저에서는 메뉴·긴 제목·위아래 주 안내·관련 글과 이유·검색
상태와 재시도·키보드 순서·표/코드 스크롤·테마·이미지 예약을 확인한다.
정적 링크 검사만으로 실제 과제 완료나 화면 정상 동작을 주장하지 않는다.

승인된 모아 클라우드 컴퓨터로 구현된 공개 사이트를 확인할 수 있다.
실제 창 크기·viewport·관찰 결과를 기록한다. 과거 글 검증은 새 홈·메뉴의
검증을 대신하지 않는다. 500px 데스크톱 창을 모바일 기기 검증으로 쓰지
않는다. 정확한 모바일 viewport·터치·CLS 등 미확인 항목을 명시하며
브라우저·조직 정책 제한을 다른 주소나 도구로 우회하지 않는다.

## 관찰·공개 경계

기존 무료 Cloudflare·공식 Search Console 수집과 월요일 보고를 먼저 쓴다.
중복 자동화·GA4·유료 Wizard를 요구하지 않는다. 비교 가능한 기간을
쌓아 관찰하며 구조 검사를 검색 순위·CTR 상승의 증거로 쓰지 않는다.
공개에는 개인 계정·비공개 시트 주소·토큰·원본 검색어를 넣지 않는다.
원본·비공개 작업 기록은 `vramlab_memory_backup` 대응 저장소에 둔다.
`Ubuntu-24.04`, `VRAMLab-RTX-Context`, 전역 WSL 상태를 변경하지 않는다.
