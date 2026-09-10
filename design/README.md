# VRAM Lab — Design study 01

작성: 2026-09-10. 아래는 최초 초안 검토 기록이다. 이후 사용자가 운영 적용과
커밋·푸시를 승인했다. 현재 운영 설정과 검증은 [PRODUCTION.md](PRODUCTION.md)를
기준으로 하며, 아래의 미발행·운영 분리 설명은 최초 검토 시점에 해당한다.

## 확정한 방향

- 여러 GPU의 성능 순위를 매기는 사이트가 아니라, 가진 장비의 가능성과
  한계를 깊게 파고드는 로컬 AI 실험실.
- React는 이번 초안에서 제외. Hugo, 정적 HTML/CSS, 작은 vanilla JavaScript,
  독립적인 Three.js 장면으로 구성한다.
- 향후 구조·흐름·관계 도식은 Archify를 사용한다. 실제 측정 수치의 표와
  정량 그래프는 도식과 구분하며, 숫자·축·단위·조건을 유지한다.
- 현재 장비는 RTX 5060 Ti 8 GB 데스크톱과 MacBook M4 16 GB.
  M4는 가용 장비이지 검증된 실험 결과가 아니다. 미발행 상태를 표시했다.
- 기존 영문 보고서, 고정 URL, 원본 코드·표·로그, 작성자 신분 경계를 유지한다.

## 초안에 구현한 것

1. 홈: `Small hardware. Deep experiments.`를 중심으로 한 새 구성.
   기존 글의 질문과 결과를 먼저 보여주고, 실험 방법·장비·전체 기록으로 연결한다.
2. 3D: 부품이 분리된 추상적인 층 구조. 실제 GPU 외형·VRAM 사용량·실시간
   계측이 아닌 개념 표현임을 명시했다. 조립/분리, 재생/일시정지 가능.
3. 대표 실험: Datasets 캐시 위치, mixed KV cache 실행 경로, PyTorch wheel
   감지와 실제 연산. 각 카드는 실제 기존 보고서로 연결된다.
4. 글 상세: 큰 제목, 목차, 실험 환경, 코드 복사, 스크롤 가능한 표.
   7편의 본문 파일은 수정하지 않았다.
5. Archify: 글 7의 원본 CSV와 Arrow 저장 위치를 설명하는 구조 도식 한 개.
   독립 HTML로 열거나 본문에서 펼칠 수 있다. 다른 글 도식의 전면 교체는
   이번 초안 범위가 아니다.
6. 기존 전체 기록, 검색, 주제 안내, RSS, About/Contact/Privacy로 이동 가능.
   밝은/어두운 테마와 모바일 레이아웃 제공.

파일 위치 카드는 실제 경로 목록, 호환성 카드는 실제 결과 표다. 도식 대신
임의의 연결선을 그리지 않았다. 정량 막대는 0을 기준으로 같은 축을 쓴다.

## 초안을 여는 방법

Hugo **0.164.0 extended**와 기존 PaperMod 서브모듈이 필요하다.
Three.js와 생성 완료된 Archify HTML은 저장소의 초안 테마에 포함되어 있으므로
미리보기를 위해 npm 설치나 Archify 재설치가 필요하지 않다.

```powershell
hugo server --config hugo.yaml,hugo.draft.yaml --environment development --bind 127.0.0.1 --port 1313 --baseURL http://127.0.0.1:1313/ --disableFastRender --noHTTPCache
```

이번 작업 환경에는 전역 설치 대신 `.local-tools/hugo/hugo.exe`를 두었다.
위 명령의 `hugo`를 해당 경로로 바꿔 실행해도 된다.

- 홈: http://127.0.0.1:1313/
- 글 상세: http://127.0.0.1:1313/posts/hf-datasets-cache-wsl2/
- Archify 도식: http://127.0.0.1:1313/lab/diagrams/dataset-cache.html
- 검색: http://127.0.0.1:1313/search/

## 운영 사이트와의 분리

최초 검토 시에는 `hugo.draft.yaml`을 명시한 경우에만 `LabDraft` 테마가 먼저 선택됐다.
기존 `hugo.yaml`, PaperMod, 콘텐츠, SEO override, GitHub Actions는 변경하지
않았다. 기본 `hugo` 빌드에는 초안 HTML·Three.js·Archify 자산이 들어가지 않는다.

초안 HTML은 `noindex, nofollow`, 초안 robots.txt는 전체 경로 Disallow다.
초안에서는 방문 분석도 껐다. 이는 초안 보호 설정이지 운영 SEO 변경이 아니다.
운영 승인 후 robots/SEO와 테마 선택을 별도 전환했다. 상세는 PRODUCTION.md를 참조한다.
`.draft-build`를 Pages에 업로드하지 않는다.

## 확인 기록

- Hugo 초안 빌드 성공. 기존 운영 설정의 일반 빌드·minify 빌드도 성공.
- `scripts/check_design_draft.mjs`: 검사군 8개 통과. 7편의 URL,
  코드 블록·표 HTML 일치, 실제 날짜, 로컬 참조, 운영 빌드 분리, 고정 의존성,
  Archify 산출물 해시를 확인한다. 소스 비교용 두 빌드는 모두 비압축으로 실행한다.
- 기존 콘텐츠 검사: 글 7편, 실패 0, 경고 0.
- 실제 브라우저: 390×844 모바일 홈·글·검색, 1440×900 데스크톱 홈·글,
  다크/라이트 전환, 3D 조립/분리·일시정지, 검색 일치 결과·빈 결과,
  본문 도식 펼침 확인. 검사한 화면에 문서 가로 넘침 없음.
- 3D 라이브러리 내부 상대경로를 수정했고, 잘못 고정되던 월 표기와 모바일
  줄바꿈 사이 공백, 작은 보조 문구 크기를 검수 중 수정했다.
- 초안은 운영 콘텐츠/실험 결과를 바꾸지 않으므로 실험을 재실행하지 않았다.
- 기존 PaperMod의 언어 속성 폐기 예정 경고 2개는 그대로이며 비치명적이다.
  초안 빌드에서는 같은 계열 경고 1개가 남아 있다.

다시 확인하려면:

```powershell
hugo --config hugo.yaml,hugo.draft.yaml --environment development --baseURL http://127.0.0.1:1313/
hugo --config hugo.yaml --destination .draft-checks/production --environment production --baseURL https://vramlab.com/
node scripts/check_design_draft.mjs
python scripts/lint_content.py
```

콘텐츠 검사에는 PyYAML이 필요하다. 이번 작업에서는 `.local-tools/python-libs`에
PyYAML 6.0.3만 설치하고, 검사 프로세스의 PYTHONPATH에 해당 경로를 전달했다.
전역 Python 환경은 변경하지 않았다.

## Archify 수락 기록

```text
diagram_type: architecture
output: themes/LabDraft/static/lab/diagrams/dataset-cache.html
specification_sha256: d42dce91e0918aee8b2fa75d9d6fcdfd261399422239f793e149281473250039
artifact_sha256: 1cb401089c336ce53ef94dc2a2f2dfc670d5989c2f3a107187f7d997594d396d
validation: 9/9 showcase, 0 errors, 0 warnings
browser_evidence: passed
visual_review: passed
correction_rounds: 1
```

`deliver`는 구조 검사와 산출물 바이트를 검증했다. 동일 해시의 복사본에 실행한
`visual-check`는 1440×900, 1600×1000, 1920×1080, 2048×1320의 데스크톱
넘침 검사와 양 끝 크기의 밝은/어두운 캡처를 통과했다. 별도로 생성된
1440×900 dark 및 2048×1320 light 이미지를 직접 확인했다. 자동 검사는
실험 내용의 진실성이나 미적 완성도를 증명하는 것이 아니다.

로컬 증거: `.draft-checks/archify/dataset-cache.visual-check.json` 및 PNG.
전체 수치와 사실의 근거는 기존 `content/posts/hf-datasets-cache-wsl2.md`다.
도식 주석은 한국어, 고정 Viewer UI와 HTML lang은 영어 fallback이다.

## 의도적으로 남겨 둔 후속 범위

- 전체 기존 글을 Archify 도식으로 재편집하는 작업.
- 모바일 저사양 기기의 실제 배터리·프레임 성능 측정.
- WebGL 미지원/모듈 실패 시 정적 설명, 모션 감소 설정, 화면 밖 렌더링 정지,
  탭 비활성 시 정지 처리는 구현했다. 이 모든 조건을 브라우저에서 강제
  재현했다고 주장하지 않는다.
- 신규 Mac 실험, 대시보드·계산기, 새로운 측정값, 새 호스팅 서비스.
- 최종 운영 적용, Git 커밋/푸시, Pages 발행.

의존성 버전·라이선스·해시는 [THIRD_PARTY.md](THIRD_PARTY.md)에 기록했다.
