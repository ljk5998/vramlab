# VRAMLab 구조 개선 구현·검증 기록

공통 기록 ID: `nav-2026-10-07` · 기준 공개 commit: `ec95c259590a6b41d844838f8c5c02eea66cfadf`

## 상태

P1/P2 소스 수정과 공개·비공개 메모리 진입점 작성은 완료했다. 모든 수정 후 정적·검색 runtime 최종 검증 묶음을 실행해 통과했다. 이후 실제 화면에서 발견한 두 보완을 적용하고 영향 범위만 재검사했다.

사용자가 화면 검수 재개 및 임시 HTTPS 검토본 게시·검수 후 비활성화/보관을 승인했다. 정적·검색 runtime·모아 실제 화면 검수와 공개 운영 배포 확인을 완료했다. 구현 commit과 실행 증거는 아래에 있다. 과거 Streaming 페이지의 화면 확인을 이번 변경의 증거로 재사용하지 않는다.

## 반영한 내용

| 범위 | 구현 |
|---|---|
| 상단 메뉴 | `menu.main`에서 6개 항목 출력; 상단·주 안내·breadcrumb의 표시명 공유 |
| 홈 | Start here 첫 행동, 주제 선택 3개를 3D 앞에 배치, 최신 공개 2편 자동 표시; 선정 카드·전체 목록 유지 |
| 보고서 9편 | 본문을 바꾸지 않고 `primaryHub`와 관련 글 0~2개/선택 이유 추가; 위·아래 주 안내 복귀 |
| 안내 4개 | Start here 캐시 이동, Fixes 과제 선택표/섹션, Compatibility 단계·환경·다음 행동, Measurements 지표 선택표 |
| About | M4/macOS/Metal 및 공유 시스템 메모리 범위 반영 |
| 검색 | N+4 색인, 정보 4페이지 searchHidden; 로딩·준비·빈 입력·결과·무결과·오류, 재시도·대체 탐색 |
| 품질 | 화면/JSON-LD breadcrumb 공통 데이터, Streaming SVG 500×860 예약, 긴 제목/초점/좁은 화면 CSS |
| 운영 | AGENTS → PROJECT_MEMORY → SITE_NAVIGATION → WRITING_STYLE 읽기 순서; 새 글 메타데이터·허브 연결·검증·두 repo 경계 기록 |
| 회귀 검사 | source/build 탐색 비교, 실제 생성 검색 JS/Fuse의 제어된 요청 실패 검사, Checks/Pages 배포 전 gate |

기존 9편의 URL·제목·본문·수치·코드·공개 실험 근거는 구조 작업의 변경 대상이 아니다. canonical/RSS/색인 정책과 기존 Fixes 앵커를 유지한다. 고정 PaperMod, 실험 환경, 분석 연결, 월요일 자동화는 변경하지 않는다.

## 제안의 근거와 한계

메뉴 설정 불일치·About 정보 누락·검색 실패 처리 구분은 소스에서 확인한 보완점이다. 주 안내/다음 읽기는 탐색 일관성 판단이며 메뉴 수·홈 순서·검색 범위는 검증할 설계 선택이다. 실제 클릭 감소의 원인이나 CTR 상승을 입증하지 않는다. 자세한 근거 구분은 [제안 보고서 13절](SITE_STRUCTURE_IMPROVEMENT_2026-10-06.md#13-수정보완-제안의-근거-수준--2026-10-07-보완)에 있다.

## 최종 검증 결과

2026-10-07 로컬 실제 실행 결과:

| 검사 | 결과 |
|---|---|
| 콘텐츠 lint | PASS — 9편 검사 exit 0 |
| 일반 production 빌드 | PASS — Hugo 0.164.0 extended, draft/future 포함 옵션 없음 |
| 기존 production checker | PASS — 9 reports, 19 sitemap URLs, 40 HTML files, 1,196 local references |
| navigation source/build 대조 | PASS — 624검사; 메뉴·주 안내·관련 글/이유·허브 본문·최신 목록·검색 13개·breadcrumb·SVG 등 |
| 변경 전 Git baseline 대조 | PASS — `ec95c25`의 기존 9편 본문·기존 frontmatter 보존 |
| 실제 생성 검색 JS/Fuse runtime | PASS — 10사례; resize 검색, 무결과·삭제·초점 이벤트, HTTP/네트워크/JSON/잘못된 색인/다른 origin/timeout 오류와 재시도 |
| 변경 whitespace | PASS |

검사 로그와 JSON은 Git 제외 로컬 `.draft-checks/navigation-final-20261007/`에 있다. 첫 실행은 콘텐츠 lint가 통과한 뒤 검사 실행기의 Windows 콘솔 인코딩 출력에서 중단됐다. 실행기 출력 인코딩만 바로잡고 콘텐츠 lint를 반복하지 않은 채 나머지 검사를 이어갔다. 사이트 소스에 검사 실패로 추가 수정한 사항은 없다.

기존 `.Language.LanguageCode` 폐기 예정 경고 1개가 있다. 기존 비치명적 유지보수 항목이며 이번 탐색 완료나 Google 실제 색인을 증명하는 지표가 아니다. private staged-memory 검사와 별도 소스/공개 경계 검사는 대응 기록에서 확인한다.

검색 runtime 검사는 실제 생성 bundle과 실제 Fuse를 사용하지만 DOM 대역과 제어된 응답에서 실행한다. 실제 브라우저 키보드·화면 크기·접근성·CLS 검증을 대신하지 않는다.

## 새 화면 검수에서 발견한 보완

- 390×844 데스크톱 viewport에서 홈 설명의 `compatibility.Tested` 문장 붙음이 확인됐다. 변경 전에도 있던 좁은 화면의 `<br>` 숨김 규칙이 원인이었다. 해당 CSS 규칙만 제거했으며 문구·원본 HTML·실험 수치는 그대로다. 같은 viewport와 1280×900에서 문장 경계·주 버튼·과제 선택 배치와 가로 넘침을 실제 브라우저로 다시 확인했다.
- 초기 GitHub Pages 하위 경로 검토본은 허브 허용 판정에서 prefix가 붙은 `.RelPermalink`를 비교해 보고서 주 안내와 breadcrumb가 누락됐다. 이 버전의 해당 화면 검수는 유효하지 않다. 허용 판정은 콘텐츠 `.Path`, 실제 링크는 `.RelPermalink`를 사용하도록 고쳤다. 운영 루트 주소와 검토 하위 경로에서 같은 콘텐츠 관계를 출력한다.
- 두 수정 후 fresh production 빌드, production 검사 9/19/40/1,196 및 navigation 624검사와 기존 `ec95c25` 본문·기존 메타데이터 보존은 다시 PASS다. 콘텐츠나 검색 JS/Fuse는 바뀌지 않아 이미 통과한 lint/runtime 검사는 반복하지 않았다.
- 새 HTTPS 검토본은 `a04eebda14343f87c9867fa095312f6f44640102`, Pages run `37494722860` 성공이다. 모든 HTML에 noindex/nofollow를 적용하고 기존 Cloudflare beacon 및 CNAME을 제외했다. 검색 실패 검수 helper는 임시 검토본에만 있으며 운영 소스·배포에 포함하지 않는다.
- Codex 실제 브라우저에서 오류 코드 검색→화살표/Enter→resize, HTTP404 오류→Retry→검색 준비 복구를 관찰했다. 오류는 임시 opt-in fixture의 제어된 실패이며 실제 운영 장애라고 해석하지 않는다.

## 모아 실제 화면 검수

대상은 수정 검토본 `a04eebda14343f87c9867fa095312f6f44640102`다. 모아 클라우드 Chrome의 실제 CSS viewport는 1181×757 / 500×757이며, 최종 native 보고와 새 버전 스크린샷 20개를 확인했다. 이전 `f614d33`의 결과는 최종 증거에 섞지 않았다.

| 실제 확인 범위 | 결과 |
|---|---|
| 공간 회수·모델 캐시·Datasets→Streaming·resize 오류·CUDA 실패 단계·M4 해석의 독자 과제 6개 | PASS |
| 메뉴 6개와 메뉴 페이지의 현재 위치 표시, 주제 breadcrumb·상하단 복귀·다음 읽기 | PASS |
| 홈 과제 카드·최신 2편·선정 3편·전체 9편, 좁은 창에서 과제 카드가 3D보다 앞 | PASS |
| 긴 제목·표·코드 스크롤·밝은/어두운 테마 | PASS |
| 검색 정상·무결과·Tab·위/아래 화살표·Enter·Escape 초기화 | PASS |
| 제어된 HTTP 오류·잘못된 JSON·네트워크 실패·timeout 4종의 오류 UI와 Retry 복구 | PASS |
| Streaming 그래프의 로딩 전후 공간 유지 | PASS — CLS 수치 측정은 아님 |

실제 휴대폰·터치·모아의 500px 미만 화면은 미확인이다. Codex의 390px viewport 추가 관찰도 휴대폰 기기 시험은 아니다. 모아의 3D는 대체 텍스트만 관찰돼 애니메이션은 미확인으로 남긴다. 기존 3D 원본은 보존했고 Codex 브라우저에서는 렌더링을 관찰했다.

경미한 후속 항목: 모아 Chrome에서 `↗` 장식이 네모로 보이지만 링크 작동에 영향은 없다. 보고서의 주 메뉴는 정확히 일치하는 메뉴 페이지에만 현재 위치를 표시하며, 개별 글의 주제 경로는 breadcrumb와 복귀 링크로 제공한다. 검토본 전용 JSON-LD logo/RSS 이미지 일부의 하위 경로 한계는 실제 GUI·운영 루트 메타데이터와 구분했다. 현재 검색 성과·접근성 인증·CLS 개선 폭을 입증하는 검사는 아니다.

## 운영 배포와 저장소 동기화

공개 기능 commit `729fcb15286815844e885fe3f1a849dbe6d5bfa7`을 정상 main push했다. 해당 SHA의 [Checks 37545310426](https://github.com/ljk5998/vramlab/actions/runs/37545310426)와 [Pages 37545310536](https://github.com/ljk5998/vramlab/actions/runs/37545310536)는 모두 success다.

실제 운영 `https://vramlab.com/`에서 큐레이션/정보/보고서 19개와 검색을 합한 20페이지, 자산 38개를 확인했다. 메뉴·9편 상하 주 안내·새 CSS·검수 helper 부재가 정상이며 검색 13항목·RSS 9편·사이트맵 19 URL을 확인했다. 운영 Pages는 기존 `vramlab.com`·HTTPS·workflow 설정을 유지한다.

처음 운영 대조에서 Windows 작업 사본의 줄바꿈과 Linux Git checkout의 차이가 나타났다. 정적 파일은 커밋된 Git blob 바이트와 대조하고, 검색 bundle은 실제 HTML의 URL과 SRI를 검증해 원본과 줄바꿈만 다른 것을 확인했다. 검색 JSON은 메타데이터가 정확히 같고 content/summary의 공백 정규화 후 단어열이 같다. 존재하지 않는 Windows 산출물의 fingerprint URL을 운영 검색 URL로 요구하지 않는다. 수정한 것은 대조 실행기이며 사이트 소스는 추가 변경하지 않았다.

임시 검토 Pages는 사용자 승인대로 비활성화했고 설정 API와 실제 HTTPS 모두 404다. 새 검토 repo는 archive 확인 완료다. 운영 CNAME·DNS나 기존 repo를 삭제/변경하지 않았다.

이 배포 기록의 후속 커밋은 문서만 갱신한다. 최신 main의 실제 SHA/Checks/Pages는 Git에서 확인한다. 비공개 저장소에는 같은 `nav-2026-10-07` ID와 최종 공개 SHA, 무료 수집·발행·실험 경계·모아 증거·원본 RTX 보존 결과를 기록한다. 서로 다른 repo의 SHA를 같게 만드는 동기화는 하지 않는다. private 원본·계정·Sheet·토큰·상세 수집 자료는 이 문서에 포함하지 않는다.
