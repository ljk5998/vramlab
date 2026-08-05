---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
draft: true
tags: []
description: "" # 검색 결과에 노출되는 한 줄 요약 — 150자 이내, 키워드 포함
showToc: true
---

<!--
글 템플릿 (실측 글 공통 구조):
1. 문제/에러 — 검색자가 만난 상황 그대로 (에러 전문, 스크린샷)
2. 환경 — 버전 표 (hugo에서 표로: GPU/드라이버/OS/라이브러리 버전, nvidia-smi 출력)
3. 실패한 경로 — 시도했지만 안 된 것과 그 이유
4. 해법/실측 — 재현 가능한 명령과 측정 표
5. 검증 — 해결/측정 확인 스크린샷·로그
마지막: 재현 스크립트 링크, 측정 조건 명시 (TGP, 전원 상태 등)
-->
