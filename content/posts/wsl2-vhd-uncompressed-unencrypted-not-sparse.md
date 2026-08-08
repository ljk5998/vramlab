---
title: 'Fix "Virtual hard disk files must be uncompressed and unencrypted and must not be sparse" (WSL2, 2026)'
date: 2026-08-08
lastmod: 2026-08-08
tags: ["wsl2", "windows", "disk-space", "troubleshooting"]
description: "WSL2 refuses to start with error 0xc03a001a. Measured on WSL 2.7.3: which of the three states — compressed, encrypted, sparse — actually triggers it, and which fix re-inflates your vhdx."
showToc: true
draft: true
---

<!--
AUTHOR NOTES (delete before publishing):
- Every [TODO: ...] is a number or output to measure/capture on this machine.
- Experiment protocol is in "Reproducing it". Budget ~30-40 min with a throwaway distro.
- Verify the exact error text/code WSL 2.7.3 prints — newer builds show
  Wsl/Service/CreateInstance/MountVhd/HCS/ERROR_VIRTDISK_UNSUPPORTED_DISK instead of bare 0xc03a001a.
  Whichever this build prints, quote it verbatim — that string is the SEO target.
- Per WRITING_STYLE.md: 발행 게이트 전부 미통과 상태 (실측 0%). draft: true 유지.
-->

<div class="lab-conditions">
<strong>Measured on:</strong> [TODO: Windows build] · [TODO: WSL version (kernel)] ·
[TODO: distro] · [TODO: date] · every state below forced on purpose on a throwaway
<code>ext4.vhdx</code>, then verified against a healthy control
</div>

Your WSL distro won't start, or `wsl --set-version` dies with:

```text
The requested operation could not be completed due to a virtual disk system limitation.
Virtual hard disk files must be uncompressed and unencrypted and must not be sparse.
```

[TODO: paste the exact error block from this build, including the error code line]

The message names three separate conditions — compressed, encrypted, sparse — but never tells you which one your `ext4.vhdx` is actually in. I put a test distro's vhdx into each of the three states on purpose, recorded which operations break, and timed what the fixes cost. One of the fixes needs more free disk space than you might have.

## The problem

WSL2 stores each distro as a virtual disk file (`ext4.vhdx`) and mounts it through the same Windows virtual-disk stack that Hyper-V uses. That stack refuses to mount a vhdx if the *host file itself* is NTFS-compressed, EFS-encrypted, or flagged sparse.

None of those states are exotic. You can get there without ever touching WSL:

- **Compressed** — you (or a tool like CompactGUI) ran "Compress contents to save disk space" over a parent folder. `AppData\Local` is a popular target for people trying to reclaim space, and the WSL vhdx lives right inside it.
- **Encrypted** — "Encrypt contents to secure data" (EFS) was applied to a parent folder.
- **Sparse** — you enabled WSL's sparse VHD mode back when it was allowed, or a third-party tool set the sparse flag. If you read [the previous post](/posts/wsl2-sparse-vhd-cannot-compact/), you already know current WSL gates this feature as unsafe — this error is the other half of that story: the mount layer that rejects the file the feature creates.

One scope note before the numbers: this post is about **WSL itself throwing this error** (on start, `--set-version`, or import). If you're seeing the same sentence from **diskpart** while trying `compact vdisk`, that's the sparse-file rejection I measured in [the previous post](/posts/wsl2-sparse-vhd-cannot-compact/) — go there instead.

## One command tells you which state you're in

Don't guess. Shut WSL down and read the file's attributes:

```powershell
wsl --shutdown
(Get-Item "<path-to>\ext4.vhdx").Attributes
```

[TODO: paste real output for a broken and a healthy file]

The output is a comma-separated list. You're looking for any of these three words:

| Attribute in output | State | Typical cause |
|---|---|---|
| `Compressed` | NTFS compression | Explorer checkbox, `compact.exe`, CompactGUI |
| `Encrypted` | EFS encryption | Explorer checkbox, `cipher.exe` |
| `SparseFile` | Sparse flag | WSL sparse mode, third-party tools |

A healthy vhdx shows just `Archive`.

If you don't know where your `ext4.vhdx` is, the registry knows:

```powershell
Get-ChildItem HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss |
  Get-ItemProperty | Select-Object DistributionName, BasePath
```

The vhdx is at `<BasePath>\ext4.vhdx` (Store-installed distros sit under `%LOCALAPPDATA%\Packages\...\LocalState`).

## Reproducing it

I took a throwaway distro ([TODO: distro + vhdx size]) and forced each state onto its vhdx, then tried to start it. All commands run with WSL shut down (`wsl --shutdown`).

Force compression:

```powershell
compact /c /f "<path>\ext4.vhdx"
```

Force encryption:

```powershell
cipher /e "<path-to-LocalState-folder>"
```

Force the sparse flag:

```powershell
fsutil sparse setflag "<path>\ext4.vhdx"
```

## Finding 1: any one of the three states kills the mount

| State forced | `wsl -d <distro>` starts? | Error shown |
|---|---|---|
| None (control) | [TODO] | — |
| Compressed | [TODO] | [TODO: verbatim] |
| Encrypted | [TODO] | [TODO: verbatim] |
| Sparse | [TODO] | [TODO: verbatim] |

[TODO: 2-3 sentences on the result. Sub-question worth capturing: is the error text identical for
all three states, or does the code path differ? If identical, say so explicitly — "the error will
not tell you which state you're in, which is why the Attributes check above matters."]

## Finding 2: what NTFS compression actually saved before it broke WSL

The reason people compress `AppData` is disk space. So before uncompressing, I measured what compression was even buying on an ext4 image:

| | Logical size | On disk |
|---|---|---|
| ext4.vhdx, uncompressed | [TODO] | [TODO] |
| ext4.vhdx, NTFS-compressed | [TODO] | [TODO] |

[TODO: punchline depends on the numbers. Expected shape: a mostly-full ext4 image compresses
poorly, so you traded a broken WSL for a small saving. If the saving is genuinely large on the
test image, report that honestly and note it's because the image was mostly empty space — and
point to the previous post's compact workflow as the correct way to reclaim that space.]

## Finding 3: two fixes are instant, one re-inflates the file

Uncompress (fixes `Compressed`):

```powershell
compact /u /f "<path>\ext4.vhdx"
```

Took [TODO: time] on my [TODO: GB] vhdx.

Decrypt (fixes `Encrypted`): Explorer → right-click the folder → Properties → Advanced → uncheck *Encrypt contents to secure data* → apply to subfolders and files. Or:

```powershell
cipher /d "<path-to-folder>"
```

Took [TODO: time]. Note: only the account that encrypted the folder can decrypt it.

Clear the sparse flag (fixes `SparseFile`) — this is the one that costs you:

```powershell
fsutil sparse setflag "<path>\ext4.vhdx" 0
```

[TODO: verify whether clearing the flag alone re-inflates, or whether it re-inflates on next
write / copy. Measure on-disk size before/after, and after first WSL start. Cross-check against
the previous post's Finding 5 (sparse-off re-inflation) and link it.]

A sparse vhdx occupies less on disk than its logical size. Clearing the flag means NTFS must back the full logical size with real allocation — if your vhdx is logically [TODO] GB but you only have [TODO] GB free, this fix fails on a full disk. Check free space first. Why sparse files behave this way is in [the previous post](/posts/wsl2-sparse-vhd-cannot-compact/).

## What to actually do

1. **Identify the state, don't guess.** `wsl --shutdown`, then `(Get-Item "<path>\ext4.vhdx").Attributes`. The error message won't tell you which of the three conditions you hit; the attributes will.
2. **Fix the state you found.** `compact /u /f` for compression, `cipher /d` (or the Explorer checkbox) for encryption, `fsutil sparse setflag <file> 0` for sparse — after confirming free space ≥ the vhdx's logical size.
3. **Fix the parent folder too, or it comes back.** If `LocalState` (or any ancestor) still carries the compress/encrypt attribute, new files WSL creates there inherit it. Clear it at the folder level, not just the file.
4. **Stop compressing `AppData\Local\Packages`.** If you run CompactGUI or `compact /c` sweeps, exclude WSL and Docker Desktop folders (`DockerDesktopWSL` holds a vhdx too). The measured saving on a vhdx was [TODO: X %] — not worth a distro that won't boot. To actually shrink a vhdx, use the compact workflow from [the previous post](/posts/wsl2-sparse-vhd-cannot-compact/).

---

_Everything above was measured on my own machine on [TODO: date]; the full session log with timestamps is published at [TODO: /logs/ path]. Behavior is version-dependent — if you get different results on another WSL build, I want to know: [Contact](/contact/)._
