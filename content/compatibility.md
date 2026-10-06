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

| Failed stage | Tested environment | Report | Next operation to check |
|---|---|---|---|
| 1. Device detection: CUDA availability is `False` | RTX 3060 Laptop GPU 6 GB, WSL 2.7.3, driver 572.60, PyTorch 2.13 cu130/cu126/CPU | [Four reproduced causes](/posts/torch-cuda-is-available-false-wsl2/) | After matching the driver, wheel and interpreter, run a CUDA matrix multiplication |
| 2. Computation: CUDA is available but an operation fails | RTX 5060 Ti 8 GB, WSL 2.7.12, driver 610.88, PyTorch 2.13 cu126/cu130/cu132 | [Wheel operation matrix](/posts/pytorch-2-13-rtx-5060-ti-cuda-wheels/) | Run native tensor creation and pointwise operations as well as copies, dot and GEMM; check compiler prerequisites separately |
| 3. Backend selection: a requested CUDA feature runs slowly | RTX 5060 Ti 8 GB, WSL2, llama.cpp f280b2698, mixed K/V Flash Attention | [Mixed KV cache dispatch](/posts/llama-cpp-mixed-kv-cache-rtx-5060-ti/) | Inspect scheduler placement at the tested commit; CUDA buffer registration alone does not prove CUDA execution |

## Match the environment before the recommendation

The RTX 3060 Laptop report tested a driver mismatch and a compatible wheel on that host. The RTX 5060 Ti report tested a different GPU, driver, and kernel support. A wheel recommendation from the first experiment is not a compatibility verdict for the second GPU.

Record your GPU model, Windows driver, WSL version, Python interpreter, PyTorch version, and `torch.version.cuda`. Use the diagnostic commands in the matching report to compare the actual failure stage. A displayed CUDA version alone does not establish that the operation you need will run.

## What “passed” means here

A pass applies to the commands and checks in the report. The PyTorch matrix is a compatibility probe, not a performance ranking or proof that every model works. The llama.cpp diagnostic proves scheduler placement for the inspected nodes at its pinned commit; registered CUDA buffers alone would not prove that placement.

For measured speed and memory results, see [Measurements](/benchmarks/). For disk and cache issues encountered before CUDA setup, see [Fixes](/fixes/).
