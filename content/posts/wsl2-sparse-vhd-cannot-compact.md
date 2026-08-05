---
title: "WSL2 vhdx Won't Shrink? How I Reclaimed 51 GB (sparse VHD, fstrim, Optimize-VHD)"
date: 2026-08-05
draft: true
tags: ["wsl2", "windows", "disk-space", "troubleshooting"]
description: "WSL2's ext4.vhdx keeps growing and compact does nothing — especially with sparse VHD enabled. Step-by-step how I reclaimed 51 GB, with measured numbers at each step."
showToc: true
---

<!-- ============================================================
첫 글 초안 스캐폴드 — 2026-08-05 WSL 삭제 전 실제로 한 51GB 회수 작업을 재구성.
각 섹션의 TODO를 실제 로그·수치로 채우면 발행 준비 완료.
target keyword: "wsl2 sparse vhd cannot compact" / "wsl2 vhdx shrink not working"
============================================================ -->

## The problem

<!-- TODO: 증상 서술 — C 드라이브가 가득 찼는데 WSL 안에서 파일을 지워도
     ext4.vhdx 크기가 줄지 않는 상황. 탐색기에서 본 vhdx 크기 스크린샷/수치. -->

You deleted tens of gigabytes inside WSL2 — Hugging Face model caches, conda environments, datasets — but `ext4.vhdx` on the Windows side is still the same size. Worse, if you ever enabled `sparseVhd=true`, the usual compact commands may silently do nothing.

Here is what actually happened on my machine, with the numbers at each step.

## Environment

<!-- TODO: 실제 버전 채우기 -->

| Component | Version |
|---|---|
| Windows 11 Home | 10.0.26200 |
| WSL | `wsl --version` 출력 |
| Distro | Ubuntu 22.04 (ext4.vhdx) |
| vhdx size before | ~XX GB |
| Actual usage inside WSL | ~XX GB |

## Why the vhdx doesn't shrink by itself

<!-- TODO: 원리 설명 — ext4.vhdx는 동적 확장 가상 디스크라 내부 삭제가
     호스트 파일 크기에 반영되지 않음. sparse VHD 모드의 동작과
     "sparse 상태에서는 수동 compact가 실패한다"는 함정 설명. -->

## What didn't work

<!-- TODO: 실패 경로 — 각각 실제로 시도한 결과와 회수량 0인 증거
1. `wsl --shutdown` 후 diskpart compact vdisk → sparse 상태라 실패/무효과 (에러 메시지)
2. Optimize-VHD (Home 에디션이라 Hyper-V 모듈 없음 → 대안 필요)
-->

## What worked: the full sequence

<!-- TODO: 성공 절차 — 단계마다 실측 회수량 기록
1. WSL 안에서 정리: HF 캐시/conda 정리 (du -sh 전후)
2. sudo fstrim -a -v  → trim된 용량 출력
3. wsl --manage <distro> --set-sparse false  (sparse 해제)
4. wsl --shutdown
5. diskpart: select vdisk file="..." / attach vdisk readonly / compact vdisk / detach vdisk
   → 단계별 vhdx 크기 변화 표
-->

| Step | vhdx size after | Reclaimed |
|---|---|---|
| (start) | XX GB | — |
| fstrim | XX GB | XX GB |
| sparse off + compact | XX GB | XX GB |
| **Total** | **XX GB** | **51 GB** |

## If your vhdx is bloated by ML caches specifically

<!-- TODO: 이 블로그 독자용 보너스 — HF_HOME 이동, pip/conda 캐시,
     다음 글(HF cache 관리) 내부 링크 예고 -->

## Verification

<!-- TODO: 회수 후 스크린샷 — 탐색기 vhdx 크기, WSL 정상 부팅 확인 -->

---

_Measured on my own machine on 2026-08-05. Commands are destructive-adjacent (diskpart) — double-check the vdisk path before running._
