---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
lastmod: {{ .Date }}
draft: true
tags: []
description: "" # 검색 결과에 노출되는 한 줄 요약 — 150자 이내, 키워드 포함
images: [] # 발행 전 OG 카드 경로 추가 (예: /images/og-슬러그.png)
showToc: true
primaryHub: "/fixes" # /start-here, /fixes, /compatibility, /benchmarks 중 실제 독자 과제에 맞는 안내 선택
relatedReading: [] # 0~2개: page에는 실제 콘텐츠 참조, reason에는 연결 이유를 dry English로 작성
---

<!--
글 템플릿 (실측 글 공통 구조):
1. 문제/에러 — 검색자가 만난 상황 그대로 (에러 전문, 스크린샷)
2. 환경 — 버전 표 (hugo에서 표로: GPU/드라이버/OS/라이브러리 버전, nvidia-smi 출력)
3. 실패한 경로 — 시도했지만 안 된 것과 그 이유
4. 해법/실측 — 재현 가능한 명령과 측정 표
5. 검증 — 해결/측정 확인 스크린샷·로그
마지막: 재현 스크립트 링크, 측정 조건 명시 (TGP, 전원 상태 등)

발행 전 탐색 확인:
- AGENTS.md → PROJECT_MEMORY.md → docs/SITE_NAVIGATION.md의 운영 순서와 연결 규칙 확인
- 관련 안내 페이지 선택표에 새 글 추가; 제목·공개 URL 확정 후 허브 연결
- relatedReading의 page는 site.GetPage가 찾을 수 있는 콘텐츠 경로 사용
  (slug와 파일명이 다른 글은 파일명을 기준으로 참조; 본인·중복·주 안내·draft 제외)
- 관련 대상이 없으면 relatedReading: [] 유지; 이유 없이 개수를 채우지 않음
- 모든 변경 후 저장소의 production·구조 검사와 실제 독자 과제 검증 수행
-->
