---
title: "Shrink WSL2 ext4.vhdx in 2026: Sparse VHD vs diskpart, Measured"
date: 2026-08-06
lastmod: 2026-08-06
tags: ["wsl2", "windows", "disk-space", "troubleshooting"]
images: ["/images/og-wsl2-vhdx.png"]
description: "Deleted 20 GB inside WSL but ext4.vhdx stayed huge? Measured on WSL 2.7.3: fstrim no longer needed, sparse VHD gated as unsafe, diskpart rejects sparse files."
showToc: true
---

<div class="lab-conditions">
<strong>Measured on:</strong> Windows 11 Home 10.0.26200 · WSL 2.7.3.0 (kernel 6.6.114.1-1) ·
Ubuntu 26.04 LTS (fresh install) · 2026-08-06 · every size below read from the actual
<code>ext4.vhdx</code>, both logical size and size-on-disk
</div>

## The problem

My main ML distro once grew to ~47 GB — conda environments, Hugging Face caches, PyTorch checkpoints. I deleted files inside WSL, watched `df -h` drop, and the `ext4.vhdx` on the Windows side did not give back a single byte. Back then I gave up and nuked the whole distro with `wsl --unregister`.

While rebuilding it, I did what I should have done the first time: reproduced the bloat on purpose and measured **every** reclaim path people recommend. It turns out most of the advice you will find — `fstrim` first, enable `sparseVhd=true` — no longer matches how current WSL behaves, and one of those options is now explicitly gated by Microsoft as unsafe.

One scope note before the numbers: everything below was verified on **WSL 2.7.3.0 on Windows 11 build 26200** with a fresh Ubuntu 26.04 distro. WSL changes fast — on an older WSL (check with `wsl --version`) the fstrim advice may still apply. The raw session log is [here](/logs/wsl2-vhdx-experiment-20260806.txt).

![Measured ext4.vhdx size at each experiment step — logical size vs size on disk](/images/wsl2-vhdx-size-steps.svg)

Here is the reproduction, with real numbers at every step.

## Reproducing the bloat

Fresh Ubuntu 26.04 distro. I wrote 20 GB of **random** data (random matters — zeroed blocks would let `compact` cheat) to simulate a model cache, then deleted it:

```bash
mkdir -p ~/fakecache && cd ~/fakecache
for i in 1 2 3 4; do dd if=/dev/urandom of=blob_$i bs=4M count=1280 status=none; done
# ... later ...
rm -rf ~/fakecache
```

| Step | vhdx logical size | vhdx size on disk |
|---|---|---|
| Fresh distro | 1.41 GB | 1.41 GB |
| After writing 20 GB | 21.41 GB | 21.41 GB |
| After deleting all of it inside WSL | **21.41 GB** | **21.41 GB** |

`df -h` inside WSL showed usage back down to 1.3 GB. The vhdx did not move. This is expected — Microsoft's [`compact vdisk` reference](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/compact-vdisk) says it plainly: a dynamically expanding VHD's physical size does not shrink automatically when you delete files from it.

So far this matches the old guides. Everything after this point does not.

## Finding 1: you don't need fstrim anymore

Every guide from 2020–2022 says the same thing: run `sudo fstrim -a` inside WSL first, *then* compact, otherwise the freed blocks won't be reclaimable.

On current WSL that step is already done for you. Check the root mount:

```text
$ grep -E ' / ' /proc/mounts
/dev/sdd / ext4 rw,relatime,discard,errors=remount-ro,data=ordered 0 0
```

`discard` is in the default mount options — deletes send TRIM to the virtual disk immediately, online. To verify, I went straight from `rm` to compact **without any fstrim**:

```text
wsl --shutdown
diskpart /s compact.txt      # (elevated; script below)
```

| Step | vhdx logical size |
|---|---|
| Before compact (garbage blocks, no fstrim) | 21.41 GB |
| After `wsl --shutdown` + `diskpart compact` | **1.38 GB** |

Full reclaim, zero fstrim. If a guide tells you `compact` won't work without fstrim, it was written for an older WSL. (Running `fstrim` anyway is harmless — it just re-trims free space.)

The `compact.txt` script for diskpart's [`compact vdisk`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/compact-vdisk) (per the docs, the VHD must be detached or attached read-only — hence the `readonly` below). The commonly suggested alternative, [`Optimize-VHD`](https://learn.microsoft.com/en-us/powershell/module/hyper-v/optimize-vhd), is a Hyper-V-module cmdlet — if your edition has no Hyper-V tooling (Windows Home, my case), that cmdlet simply isn't there, and diskpart is the path that works everywhere:

```text
select vdisk file="C:\Users\<you>\AppData\Local\wsl\{your-guid}\ext4.vhdx"
attach vdisk readonly
compact vdisk
detach vdisk
exit
```

Find your vhdx path with:

```powershell
Get-ChildItem HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss |
  Get-ItemProperty | Select-Object DistributionName, BasePath
```

(Microsoft's [WSL disk-space guide](https://learn.microsoft.com/en-us/windows/wsl/disk-space) documents the same lookup. Notably, its current revision covers **expanding** the disk and repairing it — not shrinking it. The shrink procedure lives in the diskpart reference above, which is part of why so many people end up on random blog posts for this.)

> **Before you run this**: ① double-check the `file=` path — diskpart operates on whatever you point it at; ② make sure WSL is fully stopped (`wsl --shutdown`, then give it a few seconds); ③ if the distro holds anything you care about, take a backup first — `wsl --export <distro> backup.tar` gives you a full restorable copy. `compact` is a read-only-attach operation and completed cleanly in my runs, but you are operating on the disk image itself.

## Finding 2: sparse VHD is now disabled as unsafe

The other classic recommendation is [`sparseVhd=true` in `.wslconfig`](https://learn.microsoft.com/en-us/windows/wsl/wsl-config) — an experimental setting [introduced with the September 2023 WSL update](https://devblogs.microsoft.com/commandline/windows-subsystem-for-linux-september-2023-update/), applied to existing distros via `wsl --manage <distro> --set-sparse true` — so the vhdx shrinks automatically. Here is what WSL 2.7.3 says today:

```text
$ wsl --manage Ubuntu --set-sparse true
Sparse VHD support is currently disabled due to potential data corruption.
To force a distribution to use a sparse vhd, please run:
wsl.exe --manage <DistributionName> --set-sparse true --allow-unsafe
Error code: Wsl/Service/E_INVALIDARG
```

The gate shipped in [WSL 2.5.6 (April 2025)](https://github.com/microsoft/WSL/releases/tag/2.5.6) — the release note is one line: *"Put sparse vhd support behind an --allow-unsafe flag."* The note doesn't give a reason; the error text does ("potential data corruption"), and it is literal enough that a GitHub issue [carries it as its title](https://github.com/microsoft/WSL/issues/13075). Users had reported corrupted vhdx files on sparse-enabled distros before the gate (for example [#10609](https://github.com/microsoft/WSL/issues/10609) — repeated ext4 corruption after enabling `sparseVhd`; the cause was never conclusively pinned, but reports like it are presumably what the gate is protecting against). That should end the "just enable sparse" advice for any distro whose contents you care about.

Since my distro was still empty scratch, I forced it on to measure what sparse mode actually does.

## Finding 3: sparse mode works — but not where you're looking

With sparse forced on, I repeated the 20 GB fill-and-delete. Five seconds after `rm`:

| | vhdx logical size | vhdx size on disk |
|---|---|---|
| Sparse on, 20 GB written | 21.38 GB | 21.38 GB |
| 5 s after deleting inside WSL | **21.42 GB** | **1.45 GB** |

Read that row again. The **real disk usage auto-reclaimed within seconds** — no shutdown, no compact. But the **logical file size never shrinks**, and that is the number Explorer's default view, `dir`, and most cleanup tools show you.

This is, I believe, the entire source of the "sparse VHD doesn't shrink" confusion in the Microsoft Q&A threads: sparse mode is working, but you are looking at the logical size. To see the truth, check the file's **Size on disk** in Properties, or:

```powershell
fsutil sparse queryflag <path-to-vhdx>   # is it sparse?
# size on disk ≈ "compressed" size:
(Get-Item <vhdx>).Length                 # logical
```

## Finding 4: diskpart refuses sparse files — the exact error

And if you try to fix that big logical number with diskpart while the file is sparse:

```text
DiskPart has encountered an error: The requested operation could not be completed
due to a virtual disk system limitation. Virtual hard disk files must be
uncompressed and unencrypted and must not be sparse.
```

(My Windows is Korean-locale; that is the canonical English text of the same error — it fails at `attach vdisk`.)

So with sparse enabled you get: real space reclaimed automatically, a scary-looking logical size you cannot compact away, and a corruption warning from Microsoft. That combination is why "wsl2 sparse vhd cannot compact" has so many unresolved threads — [this Microsoft Q&A question](https://learn.microsoft.com/en-us/answers/questions/1526083/in-wsl2-with-sparse-vhd-the-storage-usage-does-not), titled *"the storage usage does not shrink automatically, cannot compact it anymore manually"*, is Findings 3 and 4 happening to one person at the same time.

## Finding 5: turning sparse off re-inflates the file

One more trap on the way out. Converting back with `--set-sparse false` **re-materializes the holes**:

| | vhdx logical size | vhdx size on disk |
|---|---|---|
| Sparse on, after auto-reclaim | 21.39 GB | 1.45 GB |
| Right after `--set-sparse false` | 21.39 GB | **21.39 GB** |
| After one final diskpart compact | **1.39 GB** | 1.39 GB |

If you ever used sparse mode and later disable it, budget the disk space for that re-inflation and finish with a compact.

## What to actually do (on WSL 2.7.3)

Full measurement series (fresh Ubuntu 26.04, WSL 2.7.3.0, Windows 11 build 26200):

| # | Action | Logical | On disk |
|---|---|---|---|
| 0 | Fresh distro | 1.41 GB | 1.41 GB |
| 1 | Write 20 GB (random) | 21.41 | 21.41 |
| 2 | Delete inside WSL | 21.41 | 21.41 |
| 3 | `wsl --shutdown` + diskpart compact — **no fstrim** | 1.38 | 1.38 |
| 4 | `--set-sparse true` → blocked, needs `--allow-unsafe` | — | — |
| 5 | (forced sparse) write 20 GB | 21.38 | 21.38 |
| 6 | Delete → auto-reclaim in ~5 s | 21.42 | 1.45 |
| 7 | diskpart compact while sparse → **fails** | — | — |
| 8 | `--set-sparse false` → re-inflates | 21.39 | 21.39 |
| 9 | Final diskpart compact | 1.39 | 1.39 |

My recommendations, in order:

1. **Stay non-sparse** (the default). When the vhdx gets fat, run `wsl --shutdown` then the diskpart script above. On WSL 2.7+ you can skip fstrim — `discard` is already in the mount options.
2. **Don't force `--allow-unsafe` sparse** on a distro you care about. Microsoft gated it for corruption risk; the auto-reclaim is nice but not worth your conda environments.
3. **If you already have sparse enabled** and the file "won't shrink": check *size on disk* first — it probably already shrank. The logical size is cosmetic until you convert back (Finding 5).
4. **Check what is using the space**: the usual suspects are Hugging Face caches, pip/conda caches, and checkpoints. The [Hub cache experiment](/posts/move-huggingface-cache-wsl2/) measures cache placement and the cost of using `/mnt/c`; the [Datasets cache follow-up](/posts/hf-datasets-cache-wsl2/) distinguishes downloaded sources from generated Arrow files. Moving a directory within the same VHDX does not reclaim Windows disk space.

---

_Everything above was measured on my own machine on 2026-08-06; the full session log with timestamps is published at [/logs/wsl2-vhdx-experiment-20260806.txt](/logs/wsl2-vhdx-experiment-20260806.txt), and the fill/measure/compact commands in it are enough to reproduce the whole run. Behavior is version-dependent — if you get different results on another WSL build, I want to know: [Contact](/contact/)._
