# VRAMLab 사이트 구조 개선 보고서

작성일: 2026-10-06 · 내부 검토 문서 · 구현 전 제안

보완일: 2026-10-07 · 관찰 사실과 설계 판단의 근거 수준 구분

이하 관찰은 변경 전 `ec95c25` 기준의 제안 기록이다. 이후 P1/P2 구현과 실제 검증·완료 상태는 [구현 기록](NAVIGATION_IMPLEMENTATION_2026-10-07.md)에서 확인한다. 현재 파일 링크는 수정된 소스를 가리킬 수 있으므로 당시 상태는 기준 commit으로 대조한다.

## 1. 권장 방향

기존 URL과 4개 안내 페이지를 유지하고, **문제별 진입 → 보고서 → 다음에 할 작업**이 이어지도록 탐색을 개선한다. 현재 9편 규모에서는 새 카테고리와 주제별 URL을 늘리기보다 상단 메뉴, 홈페이지 진입, 글의 공통 안내를 정리하는 것이 적합하다.

우선 구현할 내용은 다음 네 가지다.

1. 상단에 Fixes와 Measurements를 노출하고 메뉴 정의를 한곳에서 관리한다.
2. 홈페이지 첫 행동을 Start here로 연결하고, 디스크·캐시 / CUDA 실행 / 성능·메모리의 선택지를 제공한다.
3. 9편 모두에 주 안내 페이지를 제공하고, 문맥에 맞는 관련 글에는 선택 이유를 붙여 공통 형식으로 표시한다.
4. About의 장비·운영체제 설명에 이미 발행된 M4 실험을 반영한다.

이는 탐색과 유지보수 개선안이다. 검색 클릭 감소의 원인이나 개선 후 클릭 증가를 확정하는 근거는 현재 부족하다.

## 2. 조사 범위와 확인 수준

| 항목 | 기준 |
|---|---|
| 소스 | `C:/개인 프로젝트/vramlab-main`, HEAD `ec95c25` |
| 운영 방식 | Hugo 0.164.0 extended + LabDraft 테마 + PaperMod 공유 자원 + GitHub Pages |
| 콘텐츠 | 발행 보고서 9편, Start here / Fixes / Compatibility / Benchmarks |
| 참고 데이터 | 사용자가 공유한 2026-10-05 주간 운영 보고서와 후속 원본 대조 결과 |
| 정적 검증 | 2026-10-06 새 production 빌드, 생성 HTML·검색 JSON·내부 링크 확인 |
| 화면 검증 | 이번 조사에서는 새 브라우저 검증을 수행하지 않음. 레이아웃 제안은 구현 후 확인 필요 |
| 변경 범위 | 이 보고서와 로컬 감사 산출물만 작성. 사이트 구현·커밋·배포·자동화 설정 변경 없음 |

현재 변경되지 않은 소스로 production 빌드를 만들고 기존 검사를 실행했다.

```text
PASS: 9 reports, 19 sitemap URLs, 40 HTML files, 1049 local references;
production SEO and review isolation verified.
```

따라서 확인된 범위에서 기본 canonical·robots·사이트맵·RSS·내부 참조에 실패가 없다. 이 결과가 실제 Google 색인 상태, 검색 결과 문구, 모든 화면 크기의 정상 동작을 입증하지는 않는다. Hugo의 기존 LanguageCode 폐기 예정 경고 1개는 비치명적이며 별도 유지보수 대상으로 둔다.

## 3. 현재 구조에서 유지할 기반

- 홈페이지의 전체 목록에서 9편 모두에 직접 이동할 수 있다. 최신 Streaming 글도 이 목록에 있다. 글이 깊이 묻히거나 고립됐다는 진단은 맞지 않는다.
- Start here에는 증상별 선택표가 이미 있다. Fixes·Compatibility·Benchmarks는 서로 다른 과제로 보고서를 묶는다.
- 생성 HTML 본문에서 연결하는 고유 보고서는 Start here 6편, Fixes 6편, Compatibility 3편, Benchmarks 7편이다. Start here는 다른 글에 허브를 통해 연결한다. Benchmarks의 7편 중 1편은 성능 순위와 호환성 결과를 구분하는 PyTorch wheel 안내다.
- 같은 글이 여러 허브에 노출되는 것은 서로 다른 질문에 답하기 위한 교차 연결이다. 글 본문을 여러 URL로 복제한 상태가 아니다.
- 검색·자동 생성 태그·카테고리는 현재 `noindex, follow`이고 사이트맵에서 제외된다. 보고서와 큐레이션 안내는 색인 가능한 구조다.
- 보고서에 BreadcrumbList와 BlogPosting 구조화 데이터가 존재한다. 개선 대상은 화면에서 보이는 주제 안내이며, 구조화 데이터가 없다는 문제가 아니다.

현재 구조가 이미 제공하는 기능을 새 기능으로 제안하거나, 기존 링크를 제거한 뒤 다시 만드는 작업은 피한다. [탐색 정책](<C:/개인 프로젝트/vramlab-main/README.md:64>), [색인 설정](<C:/개인 프로젝트/vramlab-main/hugo.yaml:22>)

## 4. 문제와 해결책

우선순위는 P1=첫 적용 묶음, P2=후속 보완, P3=규모·데이터에 따라 재검토로 정의한다.

아래의 상태는 소스·빌드에서 확인했지만, 독자에게 미치는 영향과 해결책의 효과는 별도 설계 판단을 포함한다. P1은 필수 결함이나 긴급 장애 등급이 아니다. 홈 배치·메뉴 구성·검색 대상 선택은 효과 검증이 필요한 개선안이며, 근거 수준은 13절에 구분했다.

| 우선 | 관찰된 사실 | 예상 독자·운영 영향 | 제안 해결책 | 근거 |
|---|---|---|---|---|
| P1 | 상단 메뉴가 설정 파일과 다르다. Fixes·Benchmarks는 상단에 없고 하단에 있다 | 주 안내 페이지의 노출이 고르지 않고, 설정을 고쳐도 실제 메뉴에 반영되지 않을 수 있음 | 활성 테마에서 `site.Menus.main`을 렌더링하고 실제 표시할 항목을 명시 | [상단 메뉴](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/layouts/baseof.html:44>), [메뉴 설정](<C:/개인 프로젝트/vramlab-main/hugo.yaml:90>) |
| P1 | 홈의 주 버튼은 선정 실험 섹션, 보조 링크는 장비 섹션으로 이동 | 해결할 증상이 있는 독자는 선정 실험이나 다른 메뉴에서 시작점을 찾아야 함 | 첫 버튼을 Start here에 직접 연결하고, 기존 3개 주제 안내를 선정 실험 앞에 배치 | [홈 행동](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/layouts/home.html:8>) |
| P1 | 보고서 공통 안내는 위·아래 모두 날짜별 전체 목록 복귀다. 본문 허브 링크는 4/9편 | 검색으로 들어온 독자에게 같은 문제의 다음 단계 안내가 글마다 다름 | 주 허브 링크와 문맥에 맞는 관련 보고서를 공통 템플릿으로 출력 | [글 상단](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/layouts/single.html:4>), [글 하단](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/layouts/single.html:12>) |
| P1 | About의 발행 장비 목록은 RTX 두 종류만 설명 | M4 실험과 홈페이지의 실제 범위가 소개 페이지에 반영되지 않음 | macOS·16GB M4와 해당 측정 보고서 링크를 추가하고 소개 문구의 범위를 맞춤 | [About 장비](<C:/개인 프로젝트/vramlab-main/content/about.md:16>) |
| P2 | 홈 대표 실험은 세 글로 고정되어 있다 | 새 글은 전체 목록에 있으나 대표 영역만으로 최신 발행을 알기 어려움 | 대표 실험은 유지하고 근처에 최신 공개 보고서 1~2개를 자동 표시 | [선정 글](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/layouts/home.html:23>), [전체 목록](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/layouts/home.html:50>) |
| P2 | Fixes는 VHDX 회수·모델 캐시·Arrow 캐시·Streaming 설명이 한 섹션에 모여 있다 | 서로 다른 파일·작업을 구별하려면 여러 문단을 읽어야 함 | 위쪽에 과제 선택표를 두고 디스크 작업 / Hugging Face 파일 / CUDA 환경으로 나눔 | [Fixes](<C:/개인 프로젝트/vramlab-main/content/fixes.md:14>) |
| P2 | 검색의 17개 항목에 운영 수집 소개와 법률·연락 페이지도 포함 | 보고서·주제 안내를 찾는 검색에서 부수 정보가 섞일 수 있음. 실제 방해 빈도는 미측정 | 보고서·4개 안내를 기본 검색 대상으로 정하고 부수 페이지에 `searchHidden` 적용 | [검색 목적](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/layouts/search.html:3>), [검색 JSON](<C:/개인 프로젝트/vramlab-main/themes/PaperMod/layouts/index.json:2>) |
| P2 | 검색 색인 요청 실패와 검색 결과 없음의 표시가 구분되지 않는다 | 네트워크 실패 시 독자가 해당 글이 없다고 이해할 수 있음. 실제 장애는 미관측 | 로딩·준비 완료·오류·무결과 상태를 나누고 실패 시 전체 목록과 Start here 제공 | [검색 요청 처리](<C:/개인 프로젝트/vramlab-main/themes/PaperMod/assets/js/fastsearch.js:126>), [상태 안내](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/assets/lab/lab.js:45>) |
| P2 | Streaming SVG의 생성 HTML에 이미지 크기 속성이 없다 | 로딩 전 공간 확보가 부족할 가능성. CLS 수치는 미측정 | 원본 500×860 비율로 크기 또는 aspect-ratio를 예약 | [이미지 사용](<C:/개인 프로젝트/vramlab-main/content/posts/hf-datasets-streaming-cache-wsl2.md:86>), [SVG 원본](<C:/개인 프로젝트/vramlab-main/static/images/hf-streaming-cache-and-responses.svg:1>) |

상단 메뉴·공통 다음 읽기는 이번 구조 개선의 핵심이다. 검색 오류 처리와 이미지 공간 예약은 함께 기록한 품질 보완이며, 검색 CTR 감소의 원인으로 확인된 사항이 아니다.

## 5. 목표 탐색 구조

아래 구조는 탐색 관계다. 글을 `/posts/`에서 다른 폴더로 옮기는 URL 구조가 아니다.

```text
홈 /
├─ Start here /start-here/              증상별 첫 선택
├─ Fixes /fixes/                        디스크·캐시·환경 복구
├─ Compatibility /compatibility/        탐지·연산·백엔드 확인
├─ Measurements /benchmarks/            속도·메모리·I/O의 측정 조건
├─ All reports /posts/                  날짜별 전체 목록
├─ Search /search/                      오류 코드·라이브러리·작업 검색
└─ About / Contact / Privacy            소개·연락·정책

각 보고서 /posts/기존-slug/
├─ 주 안내 페이지로 돌아가기
├─ 기존 본문·목차·실측 표·공개 증거
└─ 다음 읽기: 관련 글 또는 주제·지표 안내
```

Search Collector의 공개 소개·정책 URL은 그대로 유지한다. 일반 실험 탐색 메뉴에는 추가하지 않는다.

### 상단 메뉴

권장 표시는 `Start here · Fixes · Compatibility · Measurements · All reports · Search`다. Measurements의 URL은 기존 `/benchmarks/`를 사용한다. About은 하단에 두고 소개가 필요한 위치에서 문맥 링크를 제공한다.

현재 `hugo.yaml` 메뉴에는 `/posts/`가 없으므로, 템플릿을 메뉴 기반으로 바꾸는 작업과 항목 정리를 함께 한다. 활성 테마의 상단·하단·안내 페이지 사이드바에서 같은 목적지를 서로 다르게 부르는 부분도 정리한다.

모바일에서는 기존 줄바꿈 방식을 먼저 유지한다. 6개 항목이 늘어난 상태의 좁은 화면·키보드 순서를 검증한 뒤 필요할 때 접이식 메뉴를 검토한다. 메뉴 변경만으로 새 JavaScript 의존성을 추가할 필요는 없다.

### 홈페이지 순서

1. 사이트 소개 + `Find your starting point` → `/start-here/`
2. `Disk and cache fixes` / `CUDA compatibility` / `Performance and memory` → 기존 허브
3. 최신 보고서 1~2개 + 날짜
4. 기존 선정 실험과 실측 카드
5. 실험 방법·장비·날짜별 전체 목록·RSS

3D 표현과 실측 카드는 유지할 수 있다. 좁은 화면에서는 주제 선택을 3D 표현보다 앞에 두는 안을 검증한다. 현재 CSS에서는 홈이 한 열로 바뀌어 3D 영역이 선정 글 앞에 놓이지만, 이번 조사에서 실제 첫 화면의 점유율·성능 저하를 측정하지는 않았다. [홈 반응형 설정](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/assets/lab/lab.css:237>)

최신 목록은 공개 보고서만 날짜순으로 출력한다. 선정 카드의 고정 실측 값과 주석은 임의로 최신 글에 재사용하지 않는다.

## 6. 안내 페이지별 개선안

| 페이지 | 맡을 질문 | 구체적 보완 |
|---|---|---|
| Start here | 지금 무엇이 막혔는가? | 기존 증상표에 모델 다운로드 위치·기존 Hub 캐시 이동 행을 직접 추가. 다른 증상표는 유지 |
| Fixes | 무엇을 바꾸고 어떤 결과를 확인해야 하는가? | 선택표: Windows 용량 회수 / 기존 모델 캐시 이동 / Arrow 파일 위치 / 일부 행 Streaming / resize 오류 / CUDA False |
| Compatibility | 장치 탐지·실제 연산·의도한 실행 경로 중 어디가 실패했는가? | 기존 세 단계 구분을 유지. 각 행에 테스트 환경과 다음에 확인할 동작을 짧게 표시 |
| Measurements | 내가 필요한 지표를 어느 글에서 측정했는가? | `Question / Metric / Tested environment / Report` 선택표를 추가. first response, KV memory, 파일·모델 로딩, 반복 HTTP 응답, Windows 할당량을 구별 |
| About | 어떤 장비와 방식으로 측정하는가? | M4·macOS/Metal을 이미 발행된 실험 범위로 추가. 16GB 시스템 메모리를 GPU 전용 VRAM과 같은 지표로 표현하지 않음 |

VHDX 축소와 resize 확장, 모델 Hub 캐시와 Datasets Arrow 캐시, 캐시 삭제와 Windows 공간 회수는 다른 작업이다. 안내 문구에서 이 차이를 유지해야 한다. Streaming도 항상 빠르거나 메모리가 적다는 식으로 일반화하지 않는다.

## 7. 9개 보고서의 주 안내·다음 읽기 초안

주 안내는 기본 복귀 경로이며 배타적 분류가 아니다. 동일 보고서를 다른 허브에서도 관련 질문에 맞게 연결할 수 있다.

| 보고서의 현재 slug | 주 안내 | 권장 다음 읽기와 이유 |
|---|---|---|
| `wsl2-sparse-vhd-cannot-compact` | Fixes | 모델 캐시 이동 / Datasets 캐시: 회수할 공간과 삭제·이동 대상 파일을 구분 |
| `move-huggingface-cache-wsl2` | Fixes | Datasets 캐시: Arrow 파일은 별도 위치 / Sparse VHD: 파일 삭제 뒤 Windows 공간 회수 |
| `wsl-resize-error-0xc03a001a` | Fixes | Sparse VHD: resize 확장과 공간 회수 작업의 차이를 확인 |
| `torch-cuda-is-available-false-wsl2` | Compatibility | PyTorch wheel matrix: GPU 탐지가 성공한 뒤 실제 연산도 확인 |
| `pytorch-2-13-rtx-5060-ti-cuda-wheels` | Compatibility | CUDA False 진단: 탐지 자체가 실패하는 경우의 시작점. 테스트 GPU·버전 차이 명시 |
| `llama-cpp-mixed-kv-cache-rtx-5060-ti` | Measurements | Compatibility 안내: CUDA 버퍼와 실제 실행 경로의 차이. 다른 라이브러리의 결과를 동일 조건 성능 비교로 묶지 않음 |
| `hf-datasets-cache-wsl2` | Fixes | 모델 캐시 이동: Hub 파일 위치 / Streaming: 전체 준비를 피할 때의 파일·읽기 동작 |
| `m4-16gb-long-context-memory` | Measurements | 추가 관련 글 없음. 주 안내에서 first response·RSS·KV·swap과 실험 범위를 확인. 같은 안내 링크를 다음 읽기에 중복 출력하지 않음 |
| `hf-datasets-streaming-cache-wsl2` | Fixes | Datasets 캐시: 일반 준비 방식의 파일 위치 / Measurements 안내: 반복 읽기·시간·메모리의 범위 |

다음 읽기는 공개 보고서 또는 기존 안내 페이지 중 0~2개로 둔다. 직접 관련된 대상이 없는 경우에는 억지로 개수를 채우지 않고 주 안내와 지표 설명으로 연결한다. M4 글처럼 같은 환경의 후속 글이 없는 경우도 이 기준을 적용한다. 현재 본문 안의 관련 링크는 유지하고, 공통 안내와 반복되는 경우에만 위치를 조정한다.

## 8. 구현 설계

### 메뉴와 링크 관리

- 상단 메뉴는 `hugo.yaml`의 `menu.main`에서 관리하고 LabDraft `baseof.html`이 이를 렌더링한다.
- 글의 주 안내·다음 읽기는 명시적 frontmatter에서 관리하고 공통 partial로 출력한다. `relatedReading`에는 공개 보고서와 기존 4개 안내 페이지만 허용한다.
- `archetypes/posts.md`에도 필드를 추가해 새 글 발행 시 누락을 줄인다.
- 링크는 일반 `<a href>`로 생성하고 글 제목과 연결 이유를 표시한다. JS 필터·검색이 없어도 안내와 전체 목록을 사용할 수 있게 한다.

예시: 모델 캐시 이동 보고서의 메타데이터.

```yaml
primaryHub: "/fixes"
relatedReading:
  - page: "/posts/hf-datasets-cache-wsl2"
    reason: "Hub downloads and generated Arrow files use separate cache locations."
  - page: "/posts/wsl2-sparse-vhd-cannot-compact"
    reason: "Deleting cache files and reclaiming Windows disk space are separate steps."
```

`page`에는 Hugo가 찾을 수 있는 콘텐츠 참조를 넣고, 템플릿은 `site.GetPage`로 찾은 페이지의 `.RelPermalink`를 사용한다. 공개 URL을 파일명으로 추측하지 않는다. 특히 resize 글은 파일명 `wsl2-vhd-uncompressed-unencrypted-not-sparse.md`와 공개 slug가 다르다. [Resize 소스](<C:/개인 프로젝트/vramlab-main/content/posts/wsl2-vhd-uncompressed-unencrypted-not-sparse.md:10>)

첫 적용에서는 위쪽에 `Topic: Fixes` 같은 간단한 복귀 링크, 아래쪽에 `Next reading`을 제공한다. 다음 읽기가 0개인 글에서는 그 목록을 생략하고 주 안내 복귀를 제공한다. 화면 breadcrumb를 추가하는 후속 작업에서는 기존 JSON-LD와 함께 경로를 검토하고, 같은 메타데이터에서 생성한다. 기존 BlogPosting·실측 본문은 유지한다.

### 검색과 유지보수

- 권장 기본 검색 대상은 보고서 N편 + 안내 페이지 4개다. 현재 기준 13개다. 제외할 운영·소개·연락·정책 페이지의 직접 URL과 하단 접근은 유지한다.
- 검색 실패 상태를 보완할 때는 LabDraft의 assets override를 사용한다. 고정된 PaperMod submodule을 직접 수정하지 않는다.
- `ShowBreadCrumbs`, `ShowPostNavLinks`를 설정하는 것만으로 활성 LabDraft 화면이 바뀌지 않는다. 실제로 읽는 템플릿을 구현하거나 미사용 설정을 문서화한다.
- 새 주제 허브를 만들기 전에는 현재 허브의 선택표와 섹션으로 수용한다. 독립된 독자 과제와 여러 실측 보고서가 쌓여 기존 안내가 길어질 때 분리를 검토한다. 특정 글 수는 Google의 필수 기준이 아니다.

## 9. 실행 순서와 변경 파일

| 단계 | 작업 묶음 | 예상 변경 파일 | 완료 결과 |
|---|---|---|---|
| 1: 첫 구조 개선 | 상단 메뉴 통일, 홈 증상 진입, 9편 주 안내·관련 글, About 범위 정리 | `hugo.yaml`, LabDraft `baseof.html`·`home.html`·`single.html`·새 안내 partial·`lab.css`, 9편 frontmatter, `archetypes/posts.md`, `content/about.md` | 기존 글 URL 유지, 9편 모두 일관된 탐색 제공 |
| 2: 안내 정리 | Fixes·Measurements 선택표, Start here 캐시 이동 행, 최신 보고서 자동 표시 | 4개 안내 콘텐츠, LabDraft `home.html` | 작업·지표별 선택이 짧아지고 새 발행을 자동 노출 |
| 3: 품질 보완 | 검색 대상·실패 상태, 화면 breadcrumb 일치, SVG 공간 예약 | 정보 페이지 frontmatter, LabDraft 검색 assets·템플릿·필요한 이미지 render hook | 검색 실패와 무결과 구분, 화면과 메타데이터 일치, 이미지 비율 유지 |
| 4: 운영 확인 | 체크 스크립트 보완, 실제 화면 검증, 완료 후 배포 검증, 주간 비교 | `scripts/check_production.py` 등 필요한 검사와 내부 운영 기록 | 구조 완료 기준 확인, 배포 시점과 후속 관찰 기록 |

단계별로 diff를 작게 유지한다. 실험 본문·수치·코드·로그·발행 URL의 변경은 구조 작업에 포함하지 않는다. 현재 요청은 해결책 준비와 보고서 작성이므로 위 구현은 아직 수행하지 않았다.

## 10. 완료·검증 기준

### 정적·콘텐츠 검사

1. 기존 9개 공개 글 URL·canonical·보고서 RSS·색인 정책이 유지된다.
2. 상단 실제 HTML과 메뉴 정의가 일치하고 3개 주제 허브·Start here·전체 목록·검색에 접근할 수 있다.
3. 9편 모두 유효한 주 안내를 갖는다. 다음 읽기는 공개 보고서·지정 안내만 가리키고 본인·중복·주 안내와 같은 URL·draft·없는 페이지를 제외한다. 직접 관련 대상이 없는 글은 0개를 허용한다.
4. 모든 보고서는 적어도 하나의 관련 허브에서 연결된다. 현재의 전체 목록 링크도 유지된다.
5. 최신 목록은 새 공개 날짜를 자동 반영하고 draft를 제외한다.
6. 검색 JSON은 정한 범위를 반영한다. JSON-LD와 화면 안내의 경로가 모순되지 않는다.
7. 기존 production 검사와 필요한 새 구조 검사가 통과한다. 링크가 있다는 사실만 복제하는 테스트보다 누락·잘못된 참조·draft 노출을 검사한다.

### 실제 독자 과제

| 시작 상황 | 완료할 탐색 |
|---|---|
| WSL 내부에서 삭제했는데 C:가 줄지 않음 | 홈/Start here → Fixes → Sparse VHD 보고서 |
| 기존 모델 캐시를 다른 위치로 옮기고 싶음 | Start here 또는 Fixes → 모델 캐시 이동 → Datasets 파일과 공간 회수 구분 |
| `HF_DATASETS_CACHE`를 바꿨는데 다른 파일이 남음 | Fixes → Datasets 캐시 → Streaming의 적용 범위 확인 |
| `0xc03a001a` 오류로 resize가 실패 | 검색 또는 Fixes → resize 보고서. 축소 안내와 구분 |
| CUDA False 또는 GPU 탐지 뒤 연산 실패 | Compatibility → 해당 단계의 보고서 → 환경·실제 연산 확인 |
| M4 긴 프롬프트의 첫 응답과 메모리가 궁금함 | Measurements → M4 보고서 → 지표와 테스트 조건 확인 |

모아의 클라우드 컴퓨터를 통해 구현된 공개 페이지의 메뉴·관련 글·긴 제목·표·코드·테마를 점검할 수 있다. 정책상 허용되는 창 크기와 실제 viewport를 기록한다. 과거 Streaming 검증의 1180×757·500×757 결과는 새 메뉴·홈 변경 검증을 대신하지 않으며, 500px 창을 모바일 기기 검증으로 기록하지 않는다. 정확한 모바일 viewport·터치 동작을 확인하지 못하면 그 범위를 미확인으로 남긴다.

## 11. 효과 관찰과 보류할 작업

구조 완료는 메뉴·링크·과제별 탐색 검사로 판단한다. 검색 클릭과 방문 지표는 배포일을 기록한 뒤 후속 관찰로 평가한다.

- GSC는 동일 길이·요일의 7일 및 28일 기간을 비교한다. 사이트 총계는 Daily, 페이지별 변화는 Pages를 사용하고 빈 응답·익명 검색어 누락을 계속 구분한다.
- 9/30·10/1 Pages 공백은 10/6 자동 재조회에서 각각 7행으로 해소됐다. 이 공백을 사이트 구조 결함으로 분류하지 않는다.
- Cloudflare는 EMPTY·표본 차이가 없는 비교 가능 기간을 우선한다. 기존 추정값에 다시 표본 배수를 곱하지 않는다.
- 기존 수집 자료는 허브별 페이지뷰를 관찰하는 데 쓸 수 있지만 메뉴 클릭률·독자별 탐색 경로·과제 완료율을 직접 제공하지 않는다. 방문 수를 이런 전환 지표로 이름만 바꿔 쓰지 않는다.
- 실제 Google 제목·스니펫이 이번 구조 감사에서 확인된 것은 아니다. 제목 수정은 구조 변경과 분리해 필요성·본문 일치를 검토한다.

현재 9편을 위해 `/wsl2/`, `/hugging-face/`, `/apple-silicon/`, 장비별 허브를 동시에 신설하거나 기존 글을 다른 URL로 이동할 필요는 없다. React 재구축, 유료 검색 서비스, 새로운 분석 서비스도 이 개선안의 전제 조건이 아니다. 기존 무료 수집과 정적 사이트 운영을 활용한다.

Google도 논리적 사이트 구성과 설명적인 내부 링크를 권장하지만 작은 사이트에 대규모 재분류를 먼저 수행하도록 요구하지는 않는다. 내부 링크·breadcrumb를 정리하는 것은 페이지 관계를 이해하도록 돕는 조치이며 순위나 CTR 상승을 보장하지 않는다. [SEO 기본 가이드](https://developers.google.com/search/docs/fundamentals/seo-starter-guide), [링크 권장사항](https://developers.google.com/search/docs/crawling-indexing/links-crawlable), [Breadcrumb 안내](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb)

## 12. 근거와 산출물

| 근거 | 위치 |
|---|---|
| 사이트 운영·탐색 정책 | [README.md](<C:/개인 프로젝트/vramlab-main/README.md>) |
| 기존 디자인과 운영 적용 범위 | [PRODUCTION.md](<C:/개인 프로젝트/vramlab-main/design/PRODUCTION.md>) |
| 상단·하단·SEO 출력 | [baseof.html](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/layouts/baseof.html>) |
| 홈 선정·장비·전체 목록 | [home.html](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/layouts/home.html>) |
| 글 공통 탐색 | [single.html](<C:/개인 프로젝트/vramlab-main/themes/LabDraft/layouts/single.html>) |
| 기존 증상·문제·측정 안내 | [Start here](<C:/개인 프로젝트/vramlab-main/content/start-here.md>), [Fixes](<C:/개인 프로젝트/vramlab-main/content/fixes.md>), [Compatibility](<C:/개인 프로젝트/vramlab-main/content/compatibility.md>), [Benchmarks](<C:/개인 프로젝트/vramlab-main/content/benchmarks.md>) |
| 기본 production 검증 | [check_production.py](<C:/개인 프로젝트/vramlab-main/scripts/check_production.py>) |
| 이번 로컬 감사 빌드 | `C:/개인 프로젝트/vramlab-main/.draft-checks/structure-audit-20261006/` — Git 제외, 공개 배포용 아님 |

이 문서는 `content/` 밖의 내부 설계 보고서다. 비공개 원본 시트 주소·원본 검색어·인증 정보는 포함하지 않았다. 다음 구현 작업은 9절의 단계 1을 기준으로 시작할 수 있다.

## 13. 수정·보완 제안의 근거 수준 — 2026-10-07 보완

근거는 세 종류다. 첫째는 실제 저장소와 생성 HTML·검색 JSON에서 확인한 상태, 둘째는 그 상태를 개선하기 위한 설계 판단, 셋째는 일반 원칙을 설명하는 공식 자료다. 공식 자료만으로 이 사이트의 클릭 감소 원인이나 특정 배치의 효과를 입증할 수는 없다.

| 제안 | 직접 확인된 근거 | 판단의 성격과 한계 |
|---|---|---|
| 메뉴 정의 통일 | `hugo.yaml`의 메뉴와 LabDraft 상단 하드코딩 항목이 다름 | 유지보수 정합성 보완. 메뉴를 한곳에서 관리하면 변경 경로를 명확히 할 수 있음. 현재 링크가 동작하지 않는다는 뜻은 아님 |
| 상단 항목 6개·Measurements 명칭 | 기존 허브와 전체 글 목록이 존재하고 실제 상단은 5개 항목 | 항목 수·순서·명칭은 선택적 설계안. 6개가 최적이라는 사용자 시험이나 Google 요구사항은 없음 |
| About의 M4 추가 | 발행된 M4 보고서가 있지만 About의 발행 장비 목록에는 RTX 두 종류만 있음 | 확인된 정보 누락을 보완하는 조치. 클릭·방문 증가와는 별도 목적 |
| 주 안내·다음 읽기 통일 | 공통 복귀는 `/posts/`, 본문에서 허브로 연결되는 글은 4/9 | 탐색 일관성 보완. 홈과 다른 허브를 통해 9편 모두 접근 가능함. 다음 읽기의 실제 사용 증가·편의성은 미측정 |
| 홈의 Start here 진입·주제 선택 우선 | 첫 버튼은 선정 실험으로 이동하고 좁은 화면에서 3D가 선정 글 앞에 배치됨 | 과제 중심 탐색을 위한 가설. 잘못된 버튼 연결은 아님. 실제 화면·과제별 탐색으로 비교 필요 |
| 최신 보고서 자동 표시 | 선정 카드 3개는 고정, 전체 목록은 날짜순으로 9편을 표시 | 최신 발행 안내를 강화하는 선택안. 새 글이 누락되거나 고립된 상태는 아님 |
| 검색 대상 17개에서 13개로 정리 | 현재 색인에 9개 보고서·4개 안내와 정보 페이지 4개가 포함됨 | 검색 목적에 맞춘 범위 선택안. 13은 색인 대상 수이며 결과 표시 상한이 아님. 정보 페이지가 실제 검색을 방해한 빈도는 미측정 |
| 검색 실패 상태 구분 | 검색 코드가 색인 요청 오류와 무결과를 독자에게 별도 안내하지 않음 | 소스에서 확인한 실패 처리 보완점. 이번 조사에서 실제 요청 실패를 재현하지는 않음 |
| SVG 공간 예약 | 출력 이미지에 크기 속성이 없고 원본 비율은 500×860 | 소스와 이전 화면 관찰에 근거한 로딩 안정성 보완. CLS 값과 개선 폭은 미측정 |

메뉴 항목 수·홈 순서·다음 읽기 개수는 보고서 작성자의 설계 제안이다. Google의 공식 권장사항은 문맥에 맞는 설명적인 링크와 크롤 가능한 `<a href>` 등 일반 원칙을 뒷받침한다. 특정 메뉴 구성이나 검색 대상 13개를 요구하지 않는다. [링크 공식 지침](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

새 production 빌드의 기존 검사 통과는 URL·메타데이터·내부 참조의 기본 상태를 확인한 근거다. 탐색 편의성은 구현 전후 동일한 독자 과제로 비교하고, 검색 성과는 별도 기간 관찰로 평가해야 한다. 정보 누락·정의 불일치 보완을 먼저 적용할 수 있으며, 홈 배치·메뉴 항목·검색 범위는 선택적 개선안으로 검토한다.
