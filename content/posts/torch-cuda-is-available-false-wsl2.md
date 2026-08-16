---
title: "torch.cuda.is_available() Returns False on WSL2: 4 Tested Causes"
date: 2026-08-17
lastmod: 2026-08-17
tags: ["pytorch", "wsl2", "cuda", "troubleshooting"]
images: ["/images/og-default.png"]
description: "I tested four reasons torch.cuda.is_available() returns False on WSL2: a CUDA 13 driver mismatch, CPU-only wheel, hidden GPU, and wrong Python."
showToc: true
draft: false
slug: "torch-cuda-is-available-false-wsl2"
---

On WSL2, `nvidia-smi` saw my GPU and `torch.cuda.device_count()` returned 1, but `torch.cuda.is_available()` returned `False`:

```text
$ python -c "import torch; print(torch.cuda.is_available())"
False
```

The version fields explained why:

```text
torch.__version__                 2.13.0+cu130
torch.version.cuda                13.0
torch.backends.cuda.is_built()    True
torch.cuda.device_count()         1
torch.cuda.is_available()         False
```

`torch.cuda.is_available()` also emitted a driver-too-old warning. Calling `torch.cuda.init()` raised the same cause as a `RuntimeError`:

```text
RuntimeError: The NVIDIA driver on your system is too old (found version 12080).
```

On this WSL2 host, public PyPI had installed PyTorch 2.13's default CUDA 13.0 wheel. The Windows NVIDIA driver was 572.60. NVIDIA's [minor-version compatibility table](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html) sets the floor at R580 for CUDA 13.x and R525 for CUDA 12.x, subject to its feature and PTX caveats. I kept the driver unchanged and installed the same PyTorch base release from the cu126 index. CUDA initialization and a real tensor operation then passed six out of six fresh processes.

That was one cause, not the definition of `False`. I also reproduced a CPU-only wheel, a process-hidden GPU, and the wrong Python interpreter. All four returned the same Boolean, but their version, visibility, or path fields separated them.

<div class="lab-conditions">
<strong>Measured on:</strong> Windows 25H2 build 26200.9168 · WSL 2.7.3.0 (kernel 6.6.114.1-1) · Ubuntu 24.04 LTS · RTX 3060 Laptop GPU 6 GB · NVIDIA driver 572.60 · Python 3.12.3 · PyTorch 2.13.0 · three fresh processes per condition · 2026-08-17 · <a href="/logs/torch-cuda-is-available-false-wsl2-20260817.txt">publication log</a>
</div>

**Quick answer:** [run the diagnostic probe](#print-the-fields-that-separate-the-causes) with the same Python that launches your code before changing drivers or reinstalling WSL. It prints the interpreter path, PyTorch build, embedded CUDA runtime, visibility, device count, and explicit initialization error. If PyTorch 2.13 installed `+cu130` and driver 572.60 reports that it is too old, a fresh cu126 environment is the repair I measured. [Jump to the tested command](#the-fix-i-tested-a-fresh-cu126-environment).

## Test setup

[PyTorch 2.13 keeps CUDA 13.0 as its default build](https://pytorch.org/blog/pytorch-2-13-release-blog/). On Linux x86-64 with CPython 3.12, an explicit public-PyPI install resolved to this wheel in my run:

```text
torch-2.13.0-cp312-cp312-manylinux_2_28_x86_64.whl
torch.__version__: 2.13.0+cu130
```

I made three isolated virtual environments in one disposable Ubuntu 24.04 WSL distro:

```bash
# PyPI default
python -m pip install --no-cache-dir torch==2.13.0 \
  --index-url https://pypi.org/simple

# Same PyTorch release, CUDA 12.6 build
python -m pip install --no-cache-dir torch==2.13.0 \
  --index-url https://download.pytorch.org/whl/cu126

# CPU-only control
python -m pip install --no-cache-dir torch==2.13.0 \
  --index-url https://download.pytorch.org/whl/cpu
```

The [official cu126 wheel index](https://download.pytorch.org/whl/cu126/torch/) contained the `2.13.0+cu126` build used here. All three environments passed `pip check`. I cleared pip configuration, proxy variables, `PYTHONPATH`, `LD_LIBRARY_PATH`, and `PYTORCH_NVML_BASED_CUDA_CHECK` so a host setting could not silently change the condition.

No native/system CUDA Toolkit or Linux NVIDIA display driver was installed in the guest, and `nvcc` was absent. The PyTorch CUDA environments did include wheel-managed runtime packages. WSL exposes the Windows driver through `/usr/lib/wsl/lib/libcuda.so.1`. NVIDIA's [CUDA on WSL guide](https://docs.nvidia.com/cuda/wsl-user-guide/index.html) is explicit that the Windows display driver is the only driver to install; a Linux display driver inside WSL can overwrite the injected path.

Each probe was a new Python process. Each condition ran three times:

| Condition | What changed | Expected diagnostic role |
|---|---|---|
| cu126 control | `2.13.0+cu126`, normal visibility | Prove the WSL GPU bridge can run CUDA work |
| PyPI default, pre | `2.13.0+cu130`, normal visibility | Observe the unmodified default result |
| CPU wheel | `2.13.0+cpu` | Separate “not compiled with CUDA” |
| Hidden device | cu126 with `CUDA_VISIBLE_DEVICES=-1` | Separate process-level hiding |
| Wrong interpreter | cu126 first on `PATH`, but CPU Python executed | Separate shell/notebook environment drift |
| cu126 recovery | Repeat the positive control | Check that later probes did not break CUDA |
| PyPI default, post | Repeat the original failure | Check that the failure persisted |

The positive controls did more than call [`torch.cuda.is_available()`](https://docs.pytorch.org/docs/main/generated/torch.cuda.is_available.html). They allocated two 512×512 matrices on `cuda:0`, multiplied them, synchronized, and verified that every output value was 512.

## Finding 1: `nvidia-smi` and `device_count()` were not enough

The host and guest both saw the GPU:

```text
NVIDIA GeForce RTX 3060 Laptop GPU, driver 572.60, 6144 MiB
/dev/dxg present
libcuda.so.1 -> /usr/lib/wsl/lib/libcuda.so.1
torch.cuda.device_count() -> 1
```

Yet every PyPI-default process returned `False`. Its warning and forced initialization both named the driver:

```text
CUDA initialization: The NVIDIA driver on your system is too old
(found version 12080).
```

`12080` is the encoded CUDA driver API level (12.8), not the Windows package number 572.60. NVIDIA documents the encoding as [`1000 × major + 10 × minor`](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__VERSION.html).

The distinction is small but useful. `nvidia-smi` proves that the WSL driver bridge can enumerate the GPU. `device_count()` showed that PyTorch could enumerate one device. Neither proved that this wheel's CUDA runtime could initialize against that driver.

The `CUDA Version: 12.8` line from `nvidia-smi` is also easy to misread. It is a capability reported by the driver, not evidence that CUDA Toolkit 12.8 is installed in Ubuntu. This guest had no `nvcc` at all.

## Finding 2: the same PyTorch 2.13.0 base release worked with cu126

The two main conditions split cleanly:

| PyTorch wheel | Embedded runtime | Driver | `is_available()` | Real CUDA operation |
|---|---:|---:|---:|---:|
| PyPI default `2.13.0+cu130` | 13.0 | 572.60 | 0/6 true | Not attempted after failed init |
| cu126 index `2.13.0+cu126` | 12.6 | 572.60 | **6/6 true** | **6/6 passed** |

The six PyPI runs were three before and three after the other controls. All six had the same driver-too-old warning and `RuntimeError`. The six cu126 runs were three initial controls and three recovery controls. All six reported the RTX 3060, compute capability 8.6, and a correct matrix result. Peak allocation was 11,929,088 bytes in every successful process.

This isolates the measured failure. The Windows driver, WSL runtime, GPU bridge, distro, and hardware stayed fixed. Only the PyTorch wheel environment changed. On this host, the bridge was working and the cu130 runtime/driver pairing was not.

NVIDIA's current compatibility table explains the boundary: CUDA 13.x requires R580 or newer for minor-version compatibility, while CUDA 12.x starts at R525. Driver 572.60 sits on the CUDA 12 side of that line.

I did not update the driver, so this post does not claim a measured “driver update fixed it” result. Updating the **Windows** NVIDIA driver to a compatible branch is the other documented route. The route I actually ran was selecting the cu126 wheel.

## Finding 3: the same `False` had four measured causes

Here is the useful diagnostic table:

| Observed state | `torch.version.cuda` | CUDA built | Count | Forced-init result | Measured cause |
|---|---:|---:|---:|---|---|
| cu130 on driver 572.60 | `13.0` | yes | **1** | Driver too old | Runtime/driver mismatch |
| CPU wheel | `None` | no | 0 | Not compiled with CUDA | CPU-only install |
| cu126 + `CUDA_VISIBLE_DEVICES=-1` | `12.6` | yes | 0 | No CUDA GPUs available | GPU hidden from this process |
| CPU Python while cu126 was on `PATH` | `None` | no | 0 | Not compiled with CUDA | Wrong interpreter |
| Working cu126 | `12.6` | yes | 1 | Not needed | CUDA tensor passed |

The CPU wheel and wrong-interpreter rows emitted the same error. The difference appeared only in provenance:

```text
wrong-interpreter condition
which python:    /opt/vramlab-post4/cu126/bin/python
sys.executable:  /opt/vramlab-post4/cpu/bin/python
torch.__file__:  /opt/vramlab-post4/cpu/lib/python3.12/site-packages/torch/__init__.py
```

That is why “reinstall CUDA” is a poor first response. If a notebook kernel or shell is running a different Python, reinstalling into the environment on `PATH` changes nothing in the process that imports PyTorch.

These are four reproduced causes, not an exhaustive list. A missing Windows GPU driver, broken WSL bridge, container configuration, permissions, unsupported GPU, loader override, or damaged installation can also return `False` or fail later.

## Print the fields that separate the causes

Run `nvidia-smi` inside WSL first. Then run this with the same `python` command that launches your code or notebook kernel:

```bash
nvidia-smi

python - <<'PY'
import os
import shutil
import sys
import torch

print("sys.executable:", sys.executable)
print("which python:", shutil.which("python"))
print("torch.__file__:", torch.__file__)
print("torch.__version__:", torch.__version__)
print("torch.version.cuda:", torch.version.cuda)
print("CUDA built:", torch.backends.cuda.is_built())
print("CUDA_VISIBLE_DEVICES:", os.environ.get("CUDA_VISIBLE_DEVICES"))
available = torch.cuda.is_available()
print("is_available:", available)
print("device_count:", torch.cuda.device_count())

if not available:
    try:
        torch.cuda.init()
        print("forced init: succeeded after initial False")
    except Exception as exc:
        print("forced init:", type(exc).__name__, str(exc))
PY
```

Read it in this order:

| Result | Next check |
|---|---|
| `nvidia-smi` cannot see the GPU | Fix the Windows driver/WSL GPU bridge first; changing the PyTorch wheel is not yet justified |
| `torch.version.cuda is None` or CUDA built is false | You imported a non-CUDA build; in my controls it was the CPU wheel. Compare `sys.executable`, `which python`, and `torch.__file__` |
| CUDA is built, count is 0, visibility is `-1` or empty | Check who set `CUDA_VISIBLE_DEVICES`; unset it only if hiding was not intentional |
| CUDA is built, count is 1, and forced init says driver too old | Compare the wheel's runtime with the Windows driver compatibility branch |
| CUDA is built, but forced init shows another error | Preserve the exact error; the cu126 repair below was not tested for that branch |
| Availability is true but your workload fails | Run a small allocation/operation; availability is not a workload or memory test |

The order is deliberate: the snippet records `is_available()` once before calling `device_count()`. My structured probe used the same order, captured the warning, and then called `torch.cuda.init()` separately if availability was false.

## The fix I tested: a fresh cu126 environment

A new environment avoids mixing cu130 and cu126 packages in place. Run this from a directory where `.venv-cu126` does not already exist:

```bash
test ! -e .venv-cu126 && \
python3 -m venv .venv-cu126 && \
.venv-cu126/bin/python -m pip install --no-cache-dir torch==2.13.0 \
  --index-url https://download.pytorch.org/whl/cu126
```

Verify the environment and actual CUDA execution:

```bash
.venv-cu126/bin/python - <<'PY'
import sys
import torch

print("python:", sys.executable)
print("torch:", torch.__version__)
print("runtime:", torch.version.cuda)
print("available:", torch.cuda.is_available())

assert torch.cuda.is_available()
a = torch.ones((512, 512), device="cuda")
b = torch.ones((512, 512), device="cuda")
c = a @ b
torch.cuda.synchronize()
assert torch.all(c == 512).item()
print("device:", torch.cuda.get_device_name(0))
print("tensor check: pass")
PY
```

My output was:

```text
torch: 2.13.0+cu126
runtime: 12.6
available: True
device: NVIDIA GeForce RTX 3060 Laptop GPU
tensor check: pass
```

If your project also needs `torchvision` or `torchaudio`, install versions matched to the same PyTorch release and index rather than copying this torch-only experiment verbatim. Check PyTorch's [current install selector](https://pytorch.org/get-started/locally/) for the supported set.

Do not install a Linux NVIDIA display driver inside WSL. If you choose the driver-update route instead, update the Windows NVIDIA driver and verify its compatibility with the wheel you intend to use. I did not measure that route here.

## What I excluded before the valid run

The valid run was not my first harness attempt. Two unbooted imports hit a transient Windows VHDX read lock while I was capturing setup evidence. A later fresh boot stopped at an over-strict PID 1 gate: `/proc/1/comm` had the expected WSL name truncated to 15 bytes. That attempt exited before its bootstrap sentinel, network package setup, or any PyTorch probe.

I preserved those setup records, removed the disposable distro, imported the clean rootfs again, corrected the gate to require the truncated name plus the full `/init` executable and command line, and then ran the matrix once. The three setup attempts are not counted in the 21 probe records.

The final validator found all 21 expected JSON files, no unexpected probe files, and no signature errors. A separate host-side manifest recorded 78 files after WSL exited, and all 78 matched the frozen post-run snapshot. The later experiment-design completion note and audited clone-cleanup records are outside the snapshot.

## Scope and limitations

- One Windows host, one RTX 3060 Laptop GPU, driver 572.60, WSL 2.7.3.0, and one disposable Ubuntu 24.04 distro.
- Three fresh Python processes per condition, but one host and one installed environment per wheel. This is repeatability on one machine, not three independent systems.
- The PyPI default is platform- and date-dependent. This run resolved to `2.13.0+cu130` on Linux x86-64/CPython 3.12 on 2026-08-17.
- The matrix multiplication was a functional smoke test. It says nothing about training speed, long-running stability, memory pressure, or model compatibility.
- Driver update, WSL update, conda, Docker, multi-GPU, other PyTorch versions, native Linux, AMD/ROCm, and macOS/MPS were not tested.
- Minimal venvs did not include NumPy, so PyTorch emitted an unrelated “Failed to initialize NumPy” warning while importing a functional-tensor module. The CUDA checks did not convert tensors through NumPy.

---

_Measured on my own machine on 2026-08-17. The [sanitized publication log](/logs/torch-cuda-is-available-false-wsl2-20260817.txt) contains every condition, repetition, and validation result. If another PyTorch build or driver branch produces a different signature, [tell me](/contact/)._
