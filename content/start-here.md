---
title: "Start here: local AI on Windows and WSL2"
description: "Find a tested route from WSL2 disk and cache problems to CUDA compatibility and inference benchmarks on consumer GPUs."
layout: "single"
url: "/start-here/"
showToc: false
ShowReadingTime: false
ShowPostNavLinks: false
hideMeta: true
---

Start with the symptom you have now. These reports follow a local AI setup from Windows disk space through the CUDA environment to inference on an 8 GB GPU. Every linked experiment names the environment it tested and includes a session log.

| What is stopping you? | Start with |
|---|---|
| C: is still full after deleting files inside WSL | [WSL2 storage and cache fixes](/fixes/#disk-space-and-model-caches) |
| Dataset files remain outside the cache directory you configured | [Hub downloads versus generated Arrow caches](/posts/hf-datasets-cache-wsl2/) |
| WSL starts, but `--resize` returns `0xc03a001a` | [The measured resize failure and recovery](/posts/wsl-resize-error-0xc03a001a/) |
| PyTorch says CUDA is unavailable | [Four reproduced causes on WSL2](/posts/torch-cuda-is-available-false-wsl2/) |
| PyTorch sees the GPU, but a CUDA operation fails | [CUDA and GPU compatibility](/compatibility/) |
| llama.cpp runs unusually slowly with mixed KV cache | [The measured CPU/CUDA dispatch difference](/posts/llama-cpp-mixed-kv-cache-rtx-5060-ti/) |
| You want the performance numbers and their limits | [Benchmarks and measurement conditions](/benchmarks/) |

## Before applying a fix

Match the operation and the tested versions to your own setup. A VHDX that starts normally can still fail during resize. A GPU listed by PyTorch can still lack the kernel needed by the next operation. The reports preserve these distinctions so that an error from one step does not become a diagnosis of the entire system.

Storage commands deserve particular care: find the exact distribution and disk path, read the backup instructions, and verify the result before deleting an original copy. Each storage report explains which changes it actually tested.

## How to read a result

The environment box states where and when a result was measured. Tables describe the operations and samples in that experiment. The linked log contains commands and output; the limitations section identifies what remains untested.

For example, a raw file read and the first model inference measure different parts of model loading. Likewise, the llama.cpp throughput report uses synthetic tokens and does not measure answer quality. Follow the metric definition as well as the number.

Browse [all reports by date](/posts/), read [how the lab works](/about/), or [search for an exact error](/search/).
