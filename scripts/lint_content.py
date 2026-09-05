#!/usr/bin/env python3
"""콘텐츠 린트 — CI와 로컬에서 동일하게 실행.

검사 항목:
  1. posts front matter: title(<=70자 권고)·date·lastmod·description(10~160자)·tags 필수
  2. 발행 글(draft 아님)에 TODO/CHANGEME/FIXME/PLACEHOLDER 마커가 남아 있으면 실패 (초안 유출 방지)
  3. front matter images 경로와 본문에서 참조하는 /images/, /logs/, /data/, /code/ 파일이 static/에 실재하는지
  4. 브랜딩 필수 자산(favicon 등) 존재
종료 코드: 실패 있으면 1.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
STATIC = ROOT / "static"

REQUIRED_ASSETS = [
    "favicon.ico", "favicon-16x16.png", "favicon-32x32.png",
    "apple-touch-icon.png", "safari-pinned-tab.svg", "images/og-default.png", "images/og-local-ai.png",
]
LEAK_MARKERS = re.compile(r"\b(TODO|CHANGEME|FIXME|PLACEHOLDER)\b")

errors, warnings = [], []


def front_matter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None, text
    return yaml.safe_load(m.group(1)), m.group(2)


for post in sorted(POSTS.glob("*.md")):
    rel = post.relative_to(ROOT)
    fm, body = front_matter(post.read_text(encoding="utf-8"))
    if fm is None:
        errors.append(f"{rel}: front matter 없음")
        continue
    draft = bool(fm.get("draft", False))

    for key in ("title", "date", "description"):
        if not fm.get(key):
            (warnings if draft else errors).append(f"{rel}: '{key}' 누락")
    if not draft and not fm.get("lastmod"):
        errors.append(f"{rel}: 'lastmod' 누락 (발행 글은 검증 날짜 명시)")
    if not draft and not fm.get("tags"):
        errors.append(f"{rel}: 'tags' 비어 있음")

    title = str(fm.get("title", ""))
    if len(title) > 70:
        warnings.append(f"{rel}: 제목 {len(title)}자 (>70, SERP 잘림 가능)")
    desc = str(fm.get("description", ""))
    if desc and not (10 <= len(desc) <= 160):
        (warnings if draft else errors).append(f"{rel}: description {len(desc)}자 (10~160 범위 밖)")

    if not draft:
        if LEAK_MARKERS.search(body):
            found = sorted(set(LEAK_MARKERS.findall(body)))
            errors.append(f"{rel}: 발행 글에 마커 잔존 {found} — 초안 유출 의심")
        if not fm.get("images"):
            warnings.append(f"{rel}: 'images'(OG 카드) 없음 — 사이트 기본 카드로 대체됨")

    refs = list(fm.get("images") or [])
    refs += re.findall(r"\]\((/(?:images|logs|data|code)/[^)#?\s]+)\)", body)
    refs += re.findall(r'src="(/(?:images|logs|data|code)/[^"#?\s]+)"', body)
    for ref in refs:
        if not (STATIC / ref.lstrip("/")).is_file():
            errors.append(f"{rel}: 참조 파일 없음 {ref}")

for asset in REQUIRED_ASSETS:
    if not (STATIC / asset).is_file():
        errors.append(f"static/{asset}: 필수 브랜딩 자산 없음")

for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"FAIL  {e}")
print(f"\n검사 완료: 글 {len(list(POSTS.glob('*.md')))}편, 실패 {len(errors)}, 경고 {len(warnings)}")
sys.exit(1 if errors else 0)
