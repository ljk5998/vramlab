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

| What needs to change? | Report | What to check afterward |
|---|---|---|
| Reclaim Windows allocation after deleting WSL files | [Sparse VHD and diskpart](/posts/wsl2-sparse-vhd-cannot-compact/) | Compare VHDX logical length and allocated size on Windows |
| Move an existing model cache or change new download locations | [HF_HOME, Hub cache and cleanup](/posts/move-huggingface-cache-wsl2/) | Check snapshot symlinks, file locations and model loading |
| Put generated Arrow files in the expected directory | [HF_DATASETS_CACHE and Hub downloads](/posts/hf-datasets-cache-wsl2/) | Inspect both cache roots; settings do not relocate existing files |
| Read a dataset prefix without preparing the full dataset | [Streaming cache and repeated reads](/posts/hf-datasets-streaming-cache-wsl2/) | Check residual files and fetched responses for the chosen format |
| Expand a VHDX when resize returns `0xc03a001a` | [Resize failure and recovery](/posts/wsl-resize-error-0xc03a001a/) | Identify the tested file attribute and retry expansion |
| Recover from `torch.cuda.is_available() == False` | [Four reproduced CUDA detection failures](/posts/torch-cuda-is-available-false-wsl2/) | Run an actual CUDA computation with the same interpreter |

## Windows disk space {#disk-space-and-model-caches}

[Shrink WSL2 ext4.vhdx: sparse VHD versus diskpart](/posts/wsl2-sparse-vhd-cannot-compact/) follows a fill-and-delete experiment through the Windows disk-reclaim steps. It distinguishes the VHDX's logical file length from its allocated size on disk, records the sparse-mode warning, and tests what happens when sparse mode is disabled. Start here when `df` shows free space but Windows still reports a large VHDX.

### Resize fails with 0xc03a001a

[Fix WSL2 resize error Wsl/Service/0xc03a001a](/posts/wsl-resize-error-0xc03a001a/) compares normal launch with `wsl --manage --resize`. On the tested WSL 2.7.3 host, the distributions started, but resize failed for compressed and sparse VHDX conditions. The report measures recovery after clearing the relevant attribute.

This is an expansion failure. For an error from `diskpart compact`, use the shrink report instead. The operation matters even when the error wording looks similar.

## Hugging Face files

### Existing Hub caches and model downloads

[Hugging Face cache on WSL2](/posts/move-huggingface-cache-wsl2/) tests cache variables, moving an existing cache, preserving snapshot symlinks, and the current cleanup commands. It also measures model loading from ext4 and `/mnt/c`. Start here when downloads land in an unexpected directory or you need to understand which files a cache cleanup actually removes.

### Generated Arrow files

[HF_DATASETS_CACHE: where the other files go](/posts/hf-datasets-cache-wsl2/) follows Hub CSV downloads, generated Arrow files, and saved-dataset transforms through different cache settings. It tests import order, scoped cleanup, and reading a copied cache offline. Use this when the model cache moved but dataset files keep appearing elsewhere.

### Dataset prefixes and repeated reads

[Streaming instead of preparing dataset files](/posts/hf-datasets-streaming-cache-wsl2/) tests whether `streaming=True` avoids those files and what a second process reads again. Use this when you want a small prefix without preparing the entire dataset; the measured response ranges show why consumed rows and fetched bytes differ.

Changing a cache directory inside the same WSL filesystem does not move its VHDX to another Windows drive. Deleting cache files and reclaiming Windows disk allocation are separate steps. Streaming's time and memory tradeoffs also differ by format and the amount read.

## CUDA environment

[Four tested causes of `torch.cuda.is_available() == False`](/posts/torch-cuda-is-available-false-wsl2/) separates a driver mismatch, a CPU-only wheel, a hidden GPU, and the wrong Python interpreter. Its diagnostic includes an actual CUDA computation after the environment check.

If availability is already `True` but a computation fails, continue to [the compatibility reports](/compatibility/). The RTX 5060 Ti wheel experiment found working operations and missing kernels within the same wheel.

Read [the measurement policy](/about/) for scope and corrections, or use [Search](/search/) for an exact error string.
