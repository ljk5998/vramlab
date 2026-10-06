# VRAMLab 프로젝트 메모리

공통 release ID: `nav-2026-10-07`

후속 작업의 진입점이다. 실제 검증·화면 확인·커밋·푸시·배포 상태는
[`구현 기록`](design/NAVIGATION_IMPLEMENTATION_2026-10-07.md)을 확인한다.
코드에 반영됐다는 사실만으로 배포 완료를 가정하지 않는다. `AGENTS.md` → 이 파일 →
`docs/SITE_NAVIGATION.md` → `WRITING_STYLE.md` 순서로 읽는다.

## 소스와 기록

- 공개 사이트 `https://vramlab.com/`, 공개 `vramlab` 저장소의 `main`, 발행 작업 사본 `vramlab-main`.
- Hugo 0.164.0 extended + LabDraft + PaperMod 공유 자원 + GitHub Pages.
- 비공개 대응 Git 저장소는 `vramlab_memory_backup` 프로젝트다. 원본 실험·개별 수집 검증·사적인 작업 기록은 그곳에만 둔다.
- 두 저장소의 SHA는 서로 다르다. 공통 release ID와 비공개 저장소의 공개 버전 참조를 기록한다. 동일 커밋으로 재설정하지 않는다.
- `public/` preview나 `.draft-checks/` 원본을 운영 배포물로 올리지 않는다. Pages가 커밋 소스로 새 production 빌드를 만든다. 승인된 화면 검수용 별도 preview는 소스·asset 해시와 실제 검수 범위를 기록한다.

## 콘텐츠와 연결

현재 공개 보고서는 9편이며 이 수는 제한이 아니다. 안내는 4개다.

| 안내 | 기존 URL | 독자 질문 |
|---|---|---|
| Start here | `/start-here/` | 현재 무엇이 막혔는가? |
| Fixes | `/fixes/` | 어떤 파일·디스크·환경 작업을 바꾸는가? |
| Compatibility | `/compatibility/` | 탐지·연산·백엔드 중 어느 단계가 실패하는가? |
| Measurements | `/benchmarks/` | 어떤 지표를 어느 환경에서 측정했는가? |

상단 메뉴는 `hugo.yaml`의 `menu.main` 한곳에서 Start here, Fixes,
Compatibility, Measurements, All reports, Search 6개를 관리한다.
Measurements라는 이름 때문에 `/benchmarks/` URL을 변경하지 않는다.
`/posts/`는 날짜별 전체 목록이며 홈 전체 목록·RSS는 공개 보고서만 포함한다.

| 기존 공개 slug | 주 안내 |
|---|---|
| `wsl2-sparse-vhd-cannot-compact` | Fixes |
| `move-huggingface-cache-wsl2` | Fixes |
| `wsl-resize-error-0xc03a001a` | Fixes |
| `torch-cuda-is-available-false-wsl2` | Compatibility |
| `pytorch-2-13-rtx-5060-ti-cuda-wheels` | Compatibility |
| `llama-cpp-mixed-kv-cache-rtx-5060-ti` | Measurements |
| `hf-datasets-cache-wsl2` | Fixes |
| `m4-16gb-long-context-memory` | Measurements |
| `hf-datasets-streaming-cache-wsl2` | Fixes |

`primaryHub`는 `/start-here`, `/fixes`, `/compatibility`, `/benchmarks` 중
실제 과제에 맞는 콘텐츠 참조다. 현재 9편은 3개 주제 안내에 분배했으며
향후 Start here도 허용한다. 배타적 분류가 아니므로 다른 안내에서 교차 연결해도
된다. `relatedReading`은 공개 보고서·4개 안내 중 직접 관련된 0~2개이며
실제 콘텐츠 참조 `page`와 dry English 연결 이유 `reason`을 갖는다.
본인·중복·주 안내와 동일 목적지·draft·미래 발행·없는 페이지·허용 밖
페이지를 제외한다. 관련 대상이 없으면 M4처럼 빈 배열을 유지한다.

Resize 소스는 `wsl2-vhd-uncompressed-unencrypted-not-sparse.md`로 공개
slug와 다르다. `site.GetPage`로 찾은 페이지의 `.RelPermalink`를 쓴다.
파일명으로 공개 URL을 조립하지 않는다. 구조 정리로 기존 본문·제목·수치·
코드·로그·URL을 바꾸지 않는다.

## 공통 출력

- 보고서 위·아래는 같은 주 안내로 복귀한다. 관련 글에는 제목과 연결 이유를 표시한다.
- 화면 breadcrumb와 JSON-LD는 `lab/breadcrumb-data.html`의 같은 경로를 사용한다. `BlogPosting`은 보고서에만 유지한다.
- 홈 최신 목록은 공개 `PublishDate`순 2편이며 draft·미래 발행을 제외한다. 선정 카드의 수치·주석을 새 글에 재사용하지 않는다.
- 검색은 공개 보고서 N편 + 안내 4개다. 현재 13개는 대상 수이며 검색 결과 상한이 아니다.
- About·Contact·Privacy Policy·Search Collector는 `searchHidden: true`지만 직접 URL과 문맥·하단 접근은 유지한다.
- Search·tag/category의 기존 `noindex, follow`·사이트맵 제외 정책을 유지한다. 보고서·큐레이션 안내는 색인 가능하다.
- `/fixes/#disk-space-and-model-caches` 앵커와 Streaming SVG의 500×860 예약을 보존한다. CLS 개선 폭은 실측 없이 기록하지 않는다.
- 고정 PaperMod를 직접 수정하지 않는다. LabDraft assets/layouts 또는 저장소 override를 사용한다.

## 측정과 분석 범위

M4의 16GB는 CPU·GPU가 공유하는 시스템 메모리이며 RTX 전용 VRAM과 같은
지표가 아니다. 결과는 해당 macOS·native arm64·llama.cpp Metal·모델·
조건에 한한다. VHDX 확장/축소, 파일 삭제/Windows 할당량 회수,
Hub 다운로드/Arrow 파일, CUDA 탐지/실제 연산을 구분한다. Streaming의
시간·메모리 결과를 모든 형식과 작업에 일반화하지 않는다.

기존 Cloudflare Web Analytics를 방문·유입의 첫 경로로 확인하고 검색
성과는 공식 Search Console API로 보완한다. 기존 일별 수집·월요일 보고를
활용한다. 중복 자동화·GA4·유료 Wizard를 새 필수 조건으로 추가하지 않는다.

GSC 총계는 Daily를 사용한다. 상세 빈 응답·익명 검색어 누락을 0이나 전체
총계로 바꾸지 않는다. Cloudflare Visits는 고유 방문자가 아니며 EMPTY·
표본 차이를 구분한다. 이미 확대된 추정값에 표본 배수를 다시 곱하지 않는다.
현재 자료로 메뉴 클릭률·개별 경로·과제 완료율은 직접 측정하지 않는다.
구조 개선을 클릭 감소의 원인 확정이나 CTR 상승 보장으로 쓰지 않는다.

공개 메모리에 개인 계정·비공개 시트 URL·토큰·인증 값·원본 검색어를
넣지 않는다. 세부 원본 비교는 비공개 대응 저장소에 둔다.

## 다음 작업

새 글은 기존 허브·메타데이터·검증 기준을 함께 갱신한다. 실제 환경을
보호하고 관련 없는 변경을 보존한다. `Ubuntu-24.04`, `VRAMLab-RTX-Context`
시작·종료·삭제·수정과 전역 `wsl --shutdown`은 하지 않는다.

검증 명령·6개 독자 과제는 `docs/SITE_NAVIGATION.md`에 있다.
`check_navigation.py --baseline REF`는 이번 기존 9편 본문·메타데이터
보존의 일회성 비교다. CI에서는 생략한다. 후속 정당한 내용 수정에 고정
불변 조건을 적용하지 않는다. 실제 Git·검사·배포 증거로 완료 기록을 갱신한다.
