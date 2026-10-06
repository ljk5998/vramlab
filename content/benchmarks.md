---
title: "Local AI benchmarks: measured results and limits"
description: "Measured M4 prompt latency and memory, CUDA KV-cache throughput, WSL2 model loading, and VHDX allocation, with versions and logs."
layout: "single"
url: "/benchmarks/"
showToc: false
ShowReadingTime: false
ShowPostNavLinks: false
hideMeta: true
---

These reports measure a specific operation under recorded conditions. Choose a report by the metric you need, then read its test setup before carrying a number into another system.

| Question | Metric | Tested environment | Report |
|---|---|---|---|
| How long does a long prompt take before content appears? | First-content latency, completion time, process RSS, runtime KV allocation, compression and swap | 16GB M4, macOS 26.6.2, Qwen3-8B Q4_K_M, llama.cpp Metal | [M4 long prompts](/posts/m4-16gb-long-context-memory/) |
| Where does mixed KV Flash Attention run, and what does that change? | Synthetic prompt-processing and token-generation throughput, KV buffer sizes, scheduler placement | RTX 5060 Ti 8 GB, WSL2, llama.cpp f280b2698, Qwen3 1.7B Q4_K_M | [Mixed KV cache](/posts/llama-cpp-mixed-kv-cache-rtx-5060-ti/) |
| Does a second streaming process reuse the same files and responses? | Persistent file lengths, first-row time, RSS high-water at exit, HTTP response-body bytes | WSL2 ext4, datasets 5.0.1, CSV and Parquet served by a loopback server | [Streaming and repeated reads](/posts/hf-datasets-streaming-cache-wsl2/) |
| Does moving a model to /mnt/c change loading costs? | Sequential file reads, tokenizer and model loading, loading plus first forward pass | WSL2 Ubuntu 26.04, ext4 and /mnt/c on one physical Samsung NVMe SSD | [Model cache location](/posts/move-huggingface-cache-wsl2/) |
| How much Windows disk allocation returns after WSL files are deleted? | VHDX logical length and allocated size during fill, delete and reclaim | Windows 11, WSL 2.7.3, fresh Ubuntu 26.04 | [Sparse VHD and diskpart](/posts/wsl2-sparse-vhd-cannot-compact/) |
| Which file attributes prevent VHDX expansion? | Resize failure and recovery checks, logical length and allocated size | Windows 11, WSL 2.7.3, compressed and sparse VHDX conditions | [Resize error 0xc03a001a](/posts/wsl-resize-error-0xc03a001a/) |

The rows measure different operations and environments. They are not a shared hardware ranking. For pass/fail CUDA operation results, use [Compatibility](/compatibility/).

## Long prompts on Apple Silicon

[Qwen3-8B on a 16GB M4](/posts/m4-16gb-long-context-memory/) measures first-content latency, completion time, process RSS, runtime KV allocation, compression and swap. Nine primary runs cover 2K/4K/8K capacities with progressively longer input and 128 output tokens. A separate 16K scout reached the 120-second first-content cutoff; it is not an OOM or maximum-context result.

The public records include every repeat and distinguish process, runtime and system memory. This is one AC-powered Mac with ordinary apps retained, not a cross-device performance comparison.

## Inference throughput and KV memory

[llama.cpp mixed KV cache on RTX 5060 Ti](/posts/llama-cpp-mixed-kv-cache-rtx-5060-ti/) compares prompt processing and token generation for several K/V cache types and context depths. The experiment changes one CUDA build option and uses separate scheduler traces to verify where mixed-cache Flash Attention runs.

The report includes llama.cpp's KV buffer sizes, build cost, and timing samples. Its synthetic-token measurements exclude tokenization and sampling. It does not compare model quality, and process-wide GPU telemetry is not presented as the exact memory use of an individual timed step.

## Dataset streaming and repeated reads

[Hugging Face streaming on WSL2](/posts/hf-datasets-streaming-cache-wsl2/) measures persistent cache files, first-row time, RSS high-water at atexit and repeated HTTP responses. Sixty fresh processes compare normal and streaming reads, CSV and Parquet, a 1,000-row prefix and all 200,000 rows. The response counters are from a loopback server; streaming's time and memory tradeoffs differ by format.

## Model files on ext4 versus /mnt/c

[Hugging Face cache location on WSL2](/posts/move-huggingface-cache-wsl2/) measures sequential file reads, tokenizer loading, model loading, and loading followed by a first forward pass. The paths were on one physical SSD so the comparison did not also change storage hardware.

The first forward pass matters: memory-mapped model loading can defer reading weight data until inference. The experiment clears Linux page cache between runs but does not claim control of Windows caching or Defender scanning.

## Windows disk allocation

[WSL2 sparse VHD and diskpart measurements](/posts/wsl2-sparse-vhd-cannot-compact/) track logical VHDX length and allocated size through a fill, delete, and reclaim sequence. [The resize error experiment](/posts/wsl-resize-error-0xc03a001a/) separately measures compressed and sparse VHDX behavior during expansion and recovery.

These are storage measurements. A smaller allocation or a successful launch does not establish faster inference or long-term disk integrity.

## Compatibility results have a different purpose

[The PyTorch 2.13 wheel matrix](/posts/pytorch-2-13-rtx-5060-ti-cuda-wheels/) records which operations completed correctly on an RTX 5060 Ti. It does not rank wheel performance. Use [Compatibility](/compatibility/) for those pass/fail results and [About](/about/) for the lab's reporting and correction policy.
