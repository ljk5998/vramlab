---
title: "CUDA and GPU compatibility: tested configurations"
description: "Measured PyTorch and llama.cpp compatibility on consumer GPUs under WSL2, including driver mismatches, CUDA kernels, and mixed KV cache dispatch."
layout: "single"
url: "/compatibility/"
showToc: false
ShowReadingTime: false
ShowPostNavLinks: false
hideMeta: true
---

GPU detection, a working CUDA computation, and execution on the intended backend are separate checks. The reports below test those checks on specific Windows/WSL2 configurations. Each links to its commands and recorded output.

| Check you need | Tested report | What the result covers |
|---|---|---|
| CUDA availability is `False` | [RTX 3060 Laptop: four reproduced causes](/posts/torch-cuda-is-available-false-wsl2/) | Driver/wheel mismatch, CPU wheel, GPU visibility, and interpreter selection; recovery checked with a CUDA matrix multiplication |
| CUDA is available but an operation fails | [RTX 5060 Ti: PyTorch 2.13 cu126, cu130, and cu132](/posts/pytorch-2-13-rtx-5060-ti-cuda-wheels/) | A fixed matrix of tensor creation, copies, pointwise operations, dot, and GEMM; separate compiler prerequisite checks |
| A requested CUDA feature runs slowly | [RTX 5060 Ti: llama.cpp mixed KV cache](/posts/llama-cpp-mixed-kv-cache-rtx-5060-ti/) | Scheduler traces for mixed K/V Flash Attention at one pinned commit, plus measurements with the build flag changed |

## Match the environment before the recommendation

The RTX 3060 Laptop report tested a driver mismatch and a compatible wheel on that host. The RTX 5060 Ti report tested a different GPU, driver, and kernel support. A wheel recommendation from the first experiment is not a compatibility verdict for the second GPU.

Record your GPU model, Windows driver, WSL version, Python interpreter, PyTorch version, and `torch.version.cuda`. Use the diagnostic commands in the matching report to compare the actual failure stage. A displayed CUDA version alone does not establish that the operation you need will run.

## What “passed” means here

A pass applies to the commands and checks in the report. The PyTorch matrix is a compatibility probe, not a performance ranking or proof that every model works. The llama.cpp diagnostic proves scheduler placement for the inspected nodes at its pinned commit; registered CUDA buffers alone would not prove that placement.

For measured speed and memory results, see [Benchmarks](/benchmarks/). For disk and cache issues encountered before CUDA setup, see [Fixes](/fixes/).
