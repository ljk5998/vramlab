---
title: "Tested Windows and WSL2 fixes for local AI"
description: "Find measured fixes for WSL2 VHDX disk space, Hugging Face caches, resize error 0xc03a001a, and PyTorch CUDA detection."
layout: "single"
url: "/fixes/"
showToc: false
ShowReadingTime: false
ShowPostNavLinks: false
hideMeta: true
---

Choose the report by the operation that failed. These experiments cover disk space, model caches, and CUDA setup on Windows with WSL2. Their fixes are tied to the versions and conditions shown in each report.

## Disk space and model caches

[Shrink WSL2 ext4.vhdx: sparse VHD versus diskpart](/posts/wsl2-sparse-vhd-cannot-compact/) follows a fill-and-delete experiment through the Windows disk-reclaim steps. It distinguishes the VHDX's logical file length from its allocated size on disk, records the sparse-mode warning, and tests what happens when sparse mode is disabled. Start here when `df` shows free space but Windows still reports a large VHDX.

[Hugging Face cache on WSL2](/posts/move-huggingface-cache-wsl2/) tests cache variables, moving an existing cache, preserving snapshot symlinks, and the current cleanup commands. It also measures model loading from ext4 and `/mnt/c`. Start here when downloads land in an unexpected directory or you need to understand which files a cache cleanup actually removes.

[HF_DATASETS_CACHE: where the other files go](/posts/hf-datasets-cache-wsl2/) follows Hub CSV downloads, generated Arrow files, and saved-dataset transforms through different cache settings. It tests import order, scoped cleanup, and reading a copied cache offline. Use this when the model cache moved but dataset files keep appearing elsewhere.

Changing a cache directory inside the same WSL filesystem does not move its VHDX to another Windows drive. Deleting cache files and reclaiming Windows disk allocation are separate steps; these reports connect those steps.

## Resize fails with 0xc03a001a

[Fix WSL2 resize error Wsl/Service/0xc03a001a](/posts/wsl-resize-error-0xc03a001a/) compares normal launch with `wsl --manage --resize`. On the tested WSL 2.7.3 host, the distributions started, but resize failed for compressed and sparse VHDX conditions. The report measures recovery after clearing the relevant attribute.

This is an expansion failure. For an error from `diskpart compact`, use the shrink report instead. The operation matters even when the error wording looks similar.

## CUDA is unavailable or a kernel fails

[Four tested causes of `torch.cuda.is_available() == False`](/posts/torch-cuda-is-available-false-wsl2/) separates a driver mismatch, a CPU-only wheel, a hidden GPU, and the wrong Python interpreter. Its diagnostic includes an actual CUDA computation after the environment check.

If availability is already `True` but a computation fails, continue to [the compatibility reports](/compatibility/). The RTX 5060 Ti wheel experiment found working operations and missing kernels within the same wheel.

Read [the measurement policy](/about/) for scope and corrections, or use [Search](/search/) for an exact error string.
