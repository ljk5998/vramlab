---
title: "Hugging Face Cache on WSL2: HF_HOME, /mnt/c, and Cleanup"
date: 2026-08-07
lastmod: 2026-08-07
tags: ["huggingface", "wsl2", "disk-space", "cache"]
images: ["/images/og-hf-cache-wsl2.png"]
description: "I tested HF_HOME, HF_HUB_CACHE, symlinks, and /mnt/c on WSL2, then measured cleanup behavior with the current hf cache commands."
showToc: true
---

<div class="lab-conditions">
<strong>Measured on:</strong> WSL2 Ubuntu 26.04 (kernel 6.6.114.1) on Windows 11 build 26200 ·
huggingface_hub 1.26.0 · transformers 5.14.1 (plus 4.57.6 for one comparison) ·
single Samsung NVMe SSD (MZVL2512) holding both <code>C:</code> and the WSL vhdx · AC power, balanced plan ·
2026-08-06 · <a href="/logs/hf-cache-experiments-20260806.txt">raw session log</a>
</div>

## The problem

You download a few models, and your disk is gone. Three questions worth answering precisely: where does the Hugging Face cache actually put things, how do you move an existing cache safely (and where should it go), and what can the current CLI clean up — and what can't it.

One reason to re-answer these in 2026: the tooling changed underneath most of the guides you will find. The CLI was renamed and its cache commands were replaced ([`hf` replaced `huggingface-cli` in July 2025](https://huggingface.co/blog/hf-cli), and [huggingface_hub v1.0 removed the old cache subcommands](https://github.com/huggingface/huggingface_hub/releases/tag/v1.0.0)), and [transformers v5 removed `TRANSFORMERS_CACHE`](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md) — the environment variable that many top-ranking tutorials still recommend. Everything below is measured on the current stack.

## Test setup

| Component | Value |
|---|---|
| Host | Windows 11 build 26200, WSL 2.7.3.0 |
| Guest | Ubuntu 26.04, kernel 6.6.114.1-microsoft-standard-WSL2 |
| Libraries | huggingface_hub 1.26.0, transformers 5.14.1 (one v4 comparison: 4.57.6), torch 2.13.0 CPU for the load benchmarks |
| Disk | one physical NVMe SSD (Samsung MZVL2512) — `C:` and the WSL `ext4.vhdx` live on the same drive, so filesystem differences below are not hardware differences |
| `/mnt/c` mount | `9p` with `aname=drvfs;...cache=5,...,msize=65536,trans=fd` (from `/proc/mounts`) |
| Test model | `Qwen/Qwen2.5-0.5B-Instruct` @ revision `7ae55760`, 954 MB in cache (`du`) |
| Cold reads | `sync; echo 3 > /proc/sys/vm/drop_caches` before every run |

One honest limitation: `drop_caches` clears the Linux page cache only. Windows-side caching and Defender scanning on `/mnt/c` are outside my control, so treat the `/mnt/c` numbers as "what a WSL user actually experiences", not as a pure filesystem microbenchmark.

## What is actually inside the cache

Fresh distro, one model downloaded:

```text
~/.cache/huggingface
├── hub
│   └── models--Qwen--Qwen2.5-0.5B-Instruct
│       ├── blobs          # the actual bytes, named by hash
│       ├── refs           # branch → revision mapping
│       ├── snapshots      # one dir per revision, symlinks into blobs
│       ├── trees
│       └── .no_exist      # negative cache: files the repo does NOT have
└── xet                    # shard/staging metadata for Xet downloads
```

`snapshots/` looks like it holds a full copy of the model. It doesn't — every file is a symlink:

```text
model.safetensors -> ../../blobs/fdf756fa7fcbe...
```

`du` confirms there is no double counting: `blobs` is 954 MB, `snapshots` is 12 KB as links (954 MB only if you force-dereference with `du -shL`), and the repo total is 954 MB.

Two measured de-duplication facts. First, downloading with the CLI and then loading the same model through `transformers` did not re-download anything — the blob count stayed at 10. Second, revisions share storage: I pulled two revisions of a repo whose files mostly didn't change between commits, and 18 file entries across the two snapshots mapped to only 11 blobs — 7 blobs shared. So keeping two revisions of a model does not necessarily cost you double.

Small print, measured: `.no_exist` is a negative cache (it recorded `special_tokens_map.json` and friends for my model — files the loader asked for that don't exist upstream), and `xet/` held 92 KB of shard/staging metadata here — per the [official cache guide](https://huggingface.co/docs/huggingface_hub/en/guides/manage-cache), its chunk cache is disabled by default, so don't expect model-sized data there, but don't be surprised the directory exists either.

## Which variable wins

The [environment-variable reference](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables) documents the defaults, but not what happens when guides tell you to set several at once. So I set every combination and checked where the files actually landed, for both the `hf` CLI and `transformers` v5:

| Variables set | Where files landed (both tools agreed) |
|---|---|
| none | `~/.cache/huggingface/hub` |
| `HF_HOME` | `$HF_HOME/hub` |
| `HF_HOME` + `HF_HUB_CACHE` | `$HF_HUB_CACHE` — the specific variable wins |
| `HF_HUB_CACHE` only | `$HF_HUB_CACHE` |
| `HF_HOME` + `TRANSFORMERS_CACHE` | `$HF_HOME/hub` — `TRANSFORMERS_CACHE` ignored |
| `HF_HUB_CACHE` + legacy `HUGGINGFACE_HUB_CACHE` | `$HF_HUB_CACHE` — legacy variable loses |

The row that deserves attention: **transformers v5 ignores `TRANSFORMERS_CACHE` silently.** No warning, no log line — your files just go somewhere else. I ran the same combination against transformers 4.57.6, and v4 behaved differently in both respects: it *honored* the variable (files landed in `$TRANSFORMERS_CACHE`) and it *warned*:

```text
FutureWarning: Using `TRANSFORMERS_CACHE` is deprecated and will be removed
in v5 of Transformers. Use `HF_HOME` instead.
```

v5 followed through on the removal ([release notes](https://github.com/huggingface/transformers/releases/tag/v5.0.0)) but the transition period is over, so the warning is gone too. If you followed an older tutorial and your cache "isn't moving", this is likely why — and nothing will tell you.

My recommendation is boring: set `HF_HOME` and nothing else. It relocates `hub`, `xet`, and assets together. `HF_HUB_CACHE` exists if you need to split just the hub cache, and `cache_dir=` on `from_pretrained`/`snapshot_download` handles one-off cases.

## How to move an existing cache safely

There is no official "move my cache" command — the [feature request](https://github.com/huggingface/huggingface_hub/issues/2117) has been open since 2024. The manual procedure that survived my testing:

1. Stop anything that might be writing — running downloads, Python processes.
2. Copy with symlinks and permissions preserved: `cp -a ~/.cache/huggingface /new/location/` (or `rsync -a`). **Do not use `cp -rL`**: it dereferences the snapshot symlinks into real copies. On my 954 MB cache that produced a 1.9 GB copy — double, from a single revision. With several revisions sharing blobs it would be worse.
3. Point `HF_HOME` at the new location (in `~/.bashrc` or wherever your shell reads), open a new shell.
4. Verify before deleting the original: `hf cache ls` should list your repos from the new path, and `hf cache verify Qwen/Qwen2.5-0.5B-Instruct` checksums the files — mine reported all 10 files matching after the move.

> **The token caveat.** `$HF_HOME` is not just cache: if you ever logged in, `$HF_HOME/token` holds your access token ([documented here](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables)). Copy the folder somewhere world-readable — a shared drive, a Windows filesystem, a published debug log — and the token goes with it. Check what you are copying, and exclude `token` from anything you post.

A symlink works too: I pointed the cache path at a symlinked directory and everything functioned — `hf cache ls`, offline loads, no errors. It is a reasonable escape hatch for tools where you can't control the environment. On performance, the three realistic metrics in the next section (tokenizer load, model load, load + forward) matched the direct path within 1%; only the raw-read runs were too variable (0.58–1.01 s vs 0.59–0.68 s direct) to call either way from this sample.

## Where to put it: ext4 vs /mnt/c, measured

Separate question from *how* to move: *where to*. On the three end-to-end metrics below, the symlink path matched direct ext4 within 1% — the raw-read runs were too noisy to judge either way. What moved the numbers was the target filesystem.

The tempting move on WSL2 is "my C: is full, I'll put the cache on the Windows side" — `/mnt/c` or `/mnt/d`. That path goes through the 9p/drvfs protocol layer, and people have hit it before: this [forum question about using `/mnt` as cache dir](https://discuss.huggingface.co/t/cant-use-mnt-drive-letter-cache-as-cache-dir/28417) sat unanswered for four years.

Cold-cache numbers, five runs per cell, same physical SSD (individual values in the [log](/logs/hf-cache-experiments-20260806.txt)):

| Cold, N=5 median | ext4 | ext4, symlink | `/mnt/c` (9p) |
|---|---|---|---|
| `dd` read (943 MB) | **0.64 s** | 0.84 s † | **4.95 s (≈7.7×)** |
| Tokenizer load | 2.68 s | 2.74 s | 3.30 s (+23%) |
| Model load (CPU, mmap) | 5.83 s | 5.83 s | 5.99 s (**+3%**) |
| **Load + first forward** | 7.67 s | 7.71 s | **11.06 s (+44%)** |

The four rows: a sequential read of the 943 MB safetensors file with `dd`, a cold `AutoTokenizer.from_pretrained`, a cold `AutoModelForCausalLM.from_pretrained` on CPU, and the same load followed by one forward pass.

† raw-read runs through the symlink varied widely (0.58–1.01 s vs 0.59–0.68 s direct) — too noisy to judge from this sample; on the three realistic metrics the symlink matched the direct path within 1%.

![Cold-cache timings by cache location: the /mnt/c cost is invisible at model load and appears at the first forward pass](/images/hf-cache-bench.svg)

This table tells a sneakier story than one number would. The raw pipe to `/mnt/c` is **about 7.7× slower** on this metric (~198 MB/s effective vs ~1.5 GB/s). Yet the full `from_pretrained` barely moves: +3%. The cost did not vanish — safetensors on CPU memory-maps the weights, so "loading the model" reads structure and metadata, not the 943 MB. The bytes are pulled when something actually touches them. Add a single forward pass and the bill arrives: **+44% (+3.4 s) on `/mnt/c`**, right where the deferred reads happen.

So the accurate conclusion is not "never touch /mnt/c", and it is also not "from_pretrained looks fine, so 9p is fine". It is: **if repeated model loading and inference matter to you, don't put the weights on `/mnt` — and don't let a fast load time fool you, because the slowdown surfaces at first inference.** Operations that read the file eagerly and fully (checksums, copies, `hf cache verify`) are exposed to more of the same read penalty; the case I measured is the sequential read, at about 7.7×. I did not benchmark each operation separately, nor GPU loading.

Also note what moving within ext4 does *not* do: it frees nothing on the Windows side. The cache still lives inside `ext4.vhdx`, same drive, same file. If your actual problem is C: running out of space, jump to [the last section](#why-your-windows-disk-is-still-full).

If you genuinely need another physical drive, the documented route is moving the distro's VHDX itself — Microsoft describes the export/import procedure in the [WSL FAQ](https://learn.microsoft.com/en-us/windows/wsl/faq) — rather than pointing the cache at `/mnt`. I did not measure that configuration in this post.

## Cleaning up with the current commands

The command set changed twice in two years, which is why half the guides disagree with your shell:

| Era | Command | Today |
|---|---|---|
| ≤2025 | `huggingface-cli scan-cache` / `delete-cache` | refuses to run: `huggingface-cli is deprecated and no longer works. Use hf instead.` |
| 2025 (`hf` v0.x) | `hf cache scan` / `hf cache delete` | removed: `Error: No such command 'scan'.` |
| current | `hf cache ls` / `rm` / `prune` / `verify` | works |

The workflow that did what I expected:

```text
$ hf cache ls
ID                                 SIZE  LAST_ACCESSED  REFS
model/Qwen/Qwen2.5-0.5B-Instruct  999.6M 1 minute ago   main
model/hf-internal-testing/tin...   12.5M a few seconds  main

$ hf cache rm model/hf-internal-testing/tiny-random-gpt2 --dry-run   # preview first
$ hf cache rm model/hf-internal-testing/tiny-random-gpt2 --yes
✓ Deleted 1 repo(s) and 1 revision(s); freed 12.5M.

$ hf cache prune    # detached revisions + incomplete downloads
```

That `freed 12.5M` removed `model/hf-internal-testing/tiny-random-gpt2` — one repo, one revision. Two details worth knowing:

- **Use the ID exactly as `hf cache ls` prints it** (`model/...`; [the CLI also accepts `hf://` URIs](https://huggingface.co/docs/huggingface_hub/en/guides/cli)). My first attempt without the `model/` prefix returned `Could not find in cache` and deleted nothing.
- The CLI and `du` won't quite agree on sizes — `hf cache ls` reported `999.6M` for a tree `du -sh` calls `966M`, a decimal-vs-binary units difference, not missing data.

## What the cleanup commands do not remove

`hf cache rm`/`prune` manage the **hub cache** — `$HF_HOME/hub`. Two neighbors are out of their reach:

| Cache | Location | How to clean |
|---|---|---|
| Hub cache (models, datasets-as-repos) | `$HF_HOME/hub` | `hf cache rm` / `prune` |
| Xet metadata | `$HF_HOME/xet` | manual (small by default — 92 KB here) |
| Datasets' Arrow cache | `$HF_HOME/datasets` (`HF_DATASETS_CACHE`) | [datasets' own cleanup](https://huggingface.co/docs/datasets/main/cache) or manual |

If you process datasets, the Arrow cache is often the real disk hog, and no `hf cache` command will show it to you.

## Why your Windows disk is still full

The WSL-specific ending. I deleted the 954 MB model plus experiment copies — usage inside WSL dropped from ~5 GB to 1.9 GB. The `ext4.vhdx` on the Windows side:

| | Inside WSL (`df`) | `ext4.vhdx` on Windows |
|---|---|---|
| before cleanup | ~5 GB used | 5.11 GB |
| after `hf cache rm` + cleanup | 1.9 GB used | **5.11 GB — unchanged** |

Deleting cache frees space *inside* the virtual disk, not the virtual disk itself. That reclaim step — and its several traps — is exactly what [the previous post measured](/posts/wsl2-sparse-vhd-cannot-compact/).

## Decision table

| Your situation | What actually helps |
|---|---|
| C: full, single drive (my case) | clean the cache, then [compact the vhdx](/posts/wsl2-sparse-vhd-cannot-compact/) — moving within ext4 frees nothing on C: |
| second physical drive available | move the distro's VHDX there via the documented export/import procedure — not `/mnt/d` |
| need the cache visible from Windows | `/mnt/c` works; the cost hides behind mmap and lands at first inference (+44% here) and on any full-file read (~7.7×) |
| followed an old guide, cache "won't move" | you probably set `TRANSFORMERS_CACHE`; v5 ignores it silently — use `HF_HOME` |
| routine hygiene | `hf cache ls` → `rm --dry-run` → `rm` → `prune`; check `$HF_HOME/datasets` separately |

---

_All numbers measured 2026-08-06 on the setup above; the full session log, including individual benchmark runs and the exact commands, is at [/logs/hf-cache-experiments-20260806.txt](/logs/hf-cache-experiments-20260806.txt). If your WSL or huggingface_hub version behaves differently, [tell me](/contact/)._
