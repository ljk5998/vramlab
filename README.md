# vramlab.com

메모리 제약 AI 하드웨어 실측 블로그 — Hugo + PaperMod + GitHub Pages.

## 로컬 미리보기

```bash
hugo server -D        # -D = draft 포함. http://localhost:1313
```

## 새 글 쓰기

```bash
hugo new content posts/my-post-slug.md   # archetypes/posts.md 템플릿 적용됨
```

- 파일명 = URL 슬러그 = 타겟 키워드 (예: `ollama-wsl2-gpu-not-detected.md`)
- front matter의 `draft: true`를 지우면(또는 false) 발행됨
- 발행: `git add . && git commit && git push` → GitHub Actions가 자동 배포 (1~2분)

## 최초 배포 절차 (1회)

1. GitHub에 **public** 저장소 생성 (이름 자유, 예: `vramlab`)
2. `git remote add origin <repo-url> && git push -u origin main`
3. 저장소 **Settings > Pages > Build and deployment > Source = "GitHub Actions"** 선택
4. **Settings > Pages > Custom domain**에 `vramlab.com` 입력 → 검증 후 **Enforce HTTPS** 체크
   (인증서 발급에 몇 분~몇 시간 걸릴 수 있음)
5. Cloudflare DNS (vramlab.com 대시보드 > DNS > Records):
   | Type | Name | Content | Proxy |
   |---|---|---|---|
   | A | @ | 185.199.108.153 | DNS only (회색 구름) |
   | A | @ | 185.199.109.153 | DNS only |
   | A | @ | 185.199.110.153 | DNS only |
   | A | @ | 185.199.111.153 | DNS only |
   | CNAME | www | `<계정명>.github.io` | DNS only |

   처음에는 Proxy를 꺼야(DNS only) GitHub이 HTTPS 인증서를 발급할 수 있음.

## 구조

```
hugo.yaml                      # 사이트 설정 (메뉴·SEO·테마 옵션)
content/posts/                 # 글 (마크다운)
content/{about,contact,privacy-policy,search}.md
archetypes/posts.md            # 새 글 템플릿 (실측 글 5단 구조)
assets/css/extended/custom.css # 커스텀 CSS (벤치마크 표 스타일 등)
themes/PaperMod/               # 테마 (git submodule — 직접 수정 금지, 오버라이드로)
.github/workflows/hugo.yaml    # 자동 배포
static/CNAME                   # 커스텀 도메인
```

## 커스텀 규칙

- 테마 파일은 절대 직접 수정하지 않는다 — 같은 경로를 프로젝트 루트에 만들어 오버라이드
  (예: 헤더 수정 = `themes/PaperMod/layouts/partials/header.html`을 `layouts/partials/header.html`로 복사 후 수정)
- CSS는 `assets/css/extended/custom.css`에만 추가
- 벤치마크 글은 상단에 `.lab-conditions` 박스로 측정 조건(TGP·전원·버전) 명시

## clone 시 주의

테마가 서브모듈이라 clone 후 한 번 필요:

```bash
git submodule update --init --recursive
```
