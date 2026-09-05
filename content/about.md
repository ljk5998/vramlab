---
title: "About"
layout: "single"
url: "/about/"
summary: "About VRAM Lab"
description: "How VRAM Lab tests local AI on Windows, WSL2, and consumer GPUs: versioned experiments, measured results, and published session logs."
showToc: false
ShowReadingTime: false
ShowBreadCrumbs: false
---

**VRAM Lab** tests local AI on Windows, WSL2, and consumer GPUs. The reports cover the steps between a full disk, a working CUDA environment, and a model that runs within limited VRAM.

I write under the name **Sinhyeok Lee**. I turn environment problems and hardware experiments into reproducible reports: what I ran, what failed, what changed, and how I checked the result. [Start here](/start-here/) to find the report that matches your problem.

## Hardware in the published reports

- **RTX 5060 Ti (8 GB VRAM)** — Windows 11 + WSL2, a consumer Blackwell desktop GPU
- **RTX 3060 Laptop GPU (6 GB VRAM)** — Windows 11 + WSL2

The storage reports also record the host disk, filesystem, WSL version, and guest distribution. Results from one machine or version do not establish behavior on every Windows or Linux system.

## How measurements are done

Each experiment identifies its tested environment and publishes a session log alongside the results. Performance reports state the measurement conditions and the samples used. Public logs remove credentials and private paths; the article explains any exclusions or follow-up corrections that affect its claims.

A successful GPU check, a completed computation, and a useful performance result answer different questions. I keep those distinctions in the reports. Failed attempts and results that contradict the starting hypothesis are part of the evidence.

Behavior on this stack is version-dependent. Posts state the version they were verified on and receive a visible update note when re-measured. Official documentation and source-code explanations are linked separately from observations made in the lab.

## Disclosure

Some posts may contain affiliate links, and they are identified as such where they appear. Measurements and conclusions are never influenced by affiliate relationships — negative results are published regardless of who sells the hardware. There are no sponsored posts on this site.

## Corrections

If you ran one of my benchmarks and got different numbers, or spotted an error, please tell me — see [Contact](/contact/). Confirmed corrections are applied to the post with a visible update note; I would rather be corrected than wrong.
