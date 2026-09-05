---
title: "Local AI benchmarks: measured results and limits"
description: "Measured WSL2 model-loading costs, llama.cpp mixed KV cache throughput, and VHDX disk allocation, with versions, sample definitions, and logs."
layout: "single"
url: "/benchmarks/"
showToc: false
ShowReadingTime: false
ShowPostNavLinks: false
hideMeta: true
---

These reports measure a specific operation under recorded conditions. Choose a report by the metric you need, then read its test setup before carrying a number into another system.

## Inference throughput and KV memory

[llama.cpp mixed KV cache on RTX 5060 Ti](/posts/llama-cpp-mixed-kv-cache-rtx-5060-ti/) compares prompt processing and token generation for several K/V cache types and context depths. The experiment changes one CUDA build option and uses separate scheduler traces to verify where mixed-cache Flash Attention runs.

The report includes llama.cpp's KV buffer sizes, build cost, and timing samples. Its synthetic-token measurements exclude tokenization and sampling. It does not compare model quality, and process-wide GPU telemetry is not presented as the exact memory use of an individual timed step.

## Model files on ext4 versus /mnt/c

[Hugging Face cache location on WSL2](/posts/move-huggingface-cache-wsl2/) measures sequential file reads, tokenizer loading, model loading, and loading followed by a first forward pass. The paths were on one physical SSD so the comparison did not also change storage hardware.

The first forward pass matters: memory-mapped model loading can defer reading weight data until inference. The experiment clears Linux page cache between runs but does not claim control of Windows caching or Defender scanning.

## Windows disk allocation

[WSL2 sparse VHD and diskpart measurements](/posts/wsl2-sparse-vhd-cannot-compact/) track logical VHDX length and allocated size through a fill, delete, and reclaim sequence. [The resize error experiment](/posts/wsl-resize-error-0xc03a001a/) separately measures compressed and sparse VHDX behavior during expansion and recovery.

These are storage measurements. A smaller allocation or a successful launch does not establish faster inference or long-term disk integrity.

## Compatibility results have a different purpose

[The PyTorch 2.13 wheel matrix](/posts/pytorch-2-13-rtx-5060-ti-cuda-wheels/) records which operations completed correctly on an RTX 5060 Ti. It does not rank wheel performance. Use [Compatibility](/compatibility/) for those pass/fail results and [About](/about/) for the lab's reporting and correction policy.
