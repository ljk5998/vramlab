---
title: "HF_DATASETS_CACHE on WSL2: Where the Other Files Go"
date: 2026-09-06
lastmod: 2026-09-06
draft: false
tags: ["huggingface", "wsl2", "cache", "disk-space"]
description: "Measured Hub downloads, Arrow files, import order, saved datasets, and cleanup on WSL2. Why HF_DATASETS_CACHE and cache_dir leave other files behind."
images: ["/images/og-hf-datasets-cache-wsl2.png"]
showToc: true
---

<div class="lab-conditions">
<strong>Measured on:</strong> Windows 11 Home build 26200.9168 · WSL 2.7.12.0, kernel 6.18.33.2-2 ·
fresh Ubuntu Base 24.04.4 · Python 3.12.3 · datasets 5.0.1 · huggingface_hub 1.30.0 ·
transformers 5.16.1 · pyarrow 25.0.1 · 2026-09-06. All test files were inside the disposable distro's ext4 filesystem.
</div>

Setting `HF_DATASETS_CACHE` put newly prepared Arrow files in the directory I chose. It left the dataset's downloaded CSVs in the Hub cache. Passing `cache_dir=` to `load_dataset()` did the same thing. The settings controlled different files; they did not relocate existing ones.

I tested ten location settings, four import-order cases, and three cache lifecycle cases in fresh processes, three times each. I checked the files and their hashes, not just the environment variables. The [results and sanitized log](/logs/hf-datasets-cache-wsl2-20260906.txt) include all 51 primary cases; the [JSON results](/data/hf-datasets-cache-wsl2-20260906.json) and [CSV summary](/data/hf-datasets-cache-wsl2-20260906.csv) are available separately.

This extends the earlier [Hub cache and WSL storage experiment](/posts/move-huggingface-cache-wsl2/). That article covers model caches and `/mnt/c` loading costs. This one covers the extra files created when processing datasets.

## Finding 1: one dataset uses two cache roots

The test input was `lhoestq/demo1`, pinned to `87ecf163bedca9d80598b528940a9c4f99e14c11`. It has five train rows and five test rows. I also downloaded a BERT configuration with `AutoConfig`, without installing PyTorch or downloading model weights.

The actual files followed this layout:

```text
HF_HOME/
├── hub/
│   ├── datasets--lhoestq--demo1/
│   │   ├── blobs/                         # downloaded README and CSV bytes
│   │   └── snapshots/<revision>/data/    # links to the CSV blobs
│   └── models--hf-internal-testing--tiny-random-bert/
│       └── snapshots/<revision>/config.json
└── datasets/
    └── lhoestq___demo1/default/0.0.0/<revision>/
        ├── demo1-train.arrow              # prepared train data
        ├── demo1-test.arrow               # prepared test data
        └── cache-<fingerprint>.arrow      # a map() result
```

Requesting `split="train"` still downloaded and prepared both splits for this dataset. The returned object had five rows. Its `cache_files` listed the train Arrow file, not the raw CSVs or the test Arrow file.

The table below records where those files actually appeared. `H`, `U`, `D`, `X`, and `C` were different empty test directories. “Default” means `~/.cache/huggingface` inside that run's isolated home.

| Setting before starting Python | Hub CSVs and model config | Prepared Arrow and default map output |
|---|---|---|
| No overrides | default `/hub` | default `/datasets` |
| `HF_HOME=H` | `H/hub` | `H/datasets` |
| `HF_DATASETS_CACHE=D` only | default `/hub` | `D` |
| `HF_HUB_CACHE=U` only | `U` | default `/datasets` |
| `HF_HOME=H`, `HF_HUB_CACHE=U`, `HF_DATASETS_CACHE=D` | `U` | `D` |
| `XDG_CACHE_HOME=X` only | `X/huggingface/hub` | `X/huggingface/datasets` |
| `XDG_CACHE_HOME=X`, `HF_HOME=H` | `H/hub` | `H/datasets` |
| `TRANSFORMERS_CACHE=C` only | default `/hub` | default `/datasets` |
| `HF_HOME=H`, `HF_DATASETS_CACHE=D`, `load_dataset(cache_dir=C)` | `H/hub` | `C` |
| `HF_HOME=H`, `AutoConfig.from_pretrained(cache_dir=C)` | CSVs: `H/hub`; config: `C` | `H/datasets` |

Each row agreed across three runs. `HF_HOME` supplies defaults; it does not override a separately configured `HF_HUB_CACHE` or `HF_DATASETS_CACHE`. The `TRANSFORMERS_CACHE` result applies to the tested Transformers 5.16.1 configuration download. The earlier article compares the older v4 behavior.

The [Datasets cache guide](https://huggingface.co/docs/datasets/cache) documents the two roots. In the [5.0.1 source](https://github.com/huggingface/datasets/blob/5.0.1/src/datasets/utils/file_utils.py#L174-L195), the Hub-download branch does not pass the dataset builder's `cache_dir` into the Hub downloader. That explains why the same keyword has different effects in the last two rows.

This table concerns this non-streaming Hub CSV dataset. It does not describe every external URL, archive, media loader, or streaming dataset.

## A small reproduction inside WSL

Run these Bash blocks in the same WSL shell. They create a new temporary lab directory and a separate Python environment. They do not copy your existing cache or its login token. `python3-venv` must already be installed; this is a CPU-only example.

```bash
export LAB=$(mktemp -d /tmp/vramlab-datasets.XXXXXX)
python3 -m venv "$LAB/venv"
source "$LAB/venv/bin/activate"
python -m pip install 'datasets==5.0.1' 'huggingface_hub==1.30.0' 'transformers==5.16.1'
unset HF_HUB_CACHE HF_DATASETS_CACHE TRANSFORMERS_CACHE HUGGINGFACE_HUB_CACHE XDG_CACHE_HOME
export HF_HOME="$LAB/hf"
export HF_HUB_DISABLE_IMPLICIT_TOKEN=1 HF_HUB_DISABLE_TELEMETRY=1
python - <<'PY'
from datasets import load_dataset
from transformers import AutoConfig

config = AutoConfig.from_pretrained(
    "hf-internal-testing/tiny-random-bert",
    revision="f171d7baecaf37b5da5a3616d8833b9969753535", token=False,
)
ds = load_dataset("lhoestq/demo1",
    revision="87ecf163bedca9d80598b528940a9c4f99e14c11",
    split="train", token=False)
mapped = ds.map(lambda row: {"review_length": len(row["review"])})
print(type(config).__name__, len(ds), len(mapped))
print("base:", ds.cache_files)
print("mapped:", mapped.cache_files)
assert config.model_type == "bert" and len(ds) == len(mapped) == 5
PY
```

The first line of the final output is `BertConfig 5 5`. Both Arrow paths are below `$LAB/hf/datasets`. The model config and dataset CSVs are under `$LAB/hf/hub`. The complete [dependency lock](/data/hf-datasets-cache-requirements-20260906.txt) records the transitive versions used in the experiment.

For your own jobs, set the intended variables before launching Python. If you want one shared root, clear conflicting specific overrides in that shell and set `HF_HOME`. This changes where future calls look; it does not move existing files. An existing logged-in `HF_HOME` can contain credentials—see the [token caveat](/posts/move-huggingface-cache-wsl2/#how-to-move-an-existing-cache-safely) before copying it.

## Finding 2: import order can split the roots

I started each process with `HF_HOME=early`, changed it to `late`, and then produced real files. The result depended on which configuration modules had already loaded.

| Before changing `HF_HOME` | Hub files | Dataset Arrow | Runs |
|---|---|---|---|
| No relevant import | `late/hub` | `late/datasets` | 3/3 |
| Import Hub constants and `datasets` | `early/hub` | `early/datasets` | 3/3 |
| Import only Hub constants | `early/hub` | `late/datasets` | 3/3 |
| Only `import huggingface_hub` | `late/hub` | `late/datasets` | 3/3 |

The last row matters. Hub 1.30.0 uses lazy imports: importing its package root did not load its constants in this test. I recorded `sys.modules` before the change to distinguish that from importing `huggingface_hub.constants`. “Any import freezes everything” would be an inaccurate description.

Here is the split-root case, using separate directories within the lab:

```bash
HF_HOME="$LAB/early" python - <<'PY'
import os
from pathlib import Path
from huggingface_hub import constants

os.environ["HF_HOME"] = str(Path(os.environ["LAB"]) / "late")
from datasets import config, load_dataset
ds = load_dataset("lhoestq/demo1",
    revision="87ecf163bedca9d80598b528940a9c4f99e14c11",
    split="train", token=False)
print("Hub:", constants.HF_HUB_CACHE)
print("Arrow:", config.HF_DATASETS_CACHE)
print(ds.cache_files)
assert "/early/hub" in constants.HF_HUB_CACHE
assert "/late/datasets/" in ds.cache_files[0]["filename"]
PY
```

Setting variables in a notebook cell after other imports can therefore be too late. Restart the kernel with the intended environment, or use the specific API argument for the operation you are controlling. The [Hub environment reference](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables) describes import-time configuration; the table above records the more precise behavior of this version.

## Finding 3: saved datasets produce files beside the export

`save_to_disk()` creates a materialized dataset at the path you supply. After loading that export, default `map()` output appeared beside its Arrow file, even when `HF_DATASETS_CACHE` pointed elsewhere. All three runs behaved this way.

| Operation | Observed output |
|---|---|
| `save_to_disk("export")` | `export/data-00000-of-00001.arrow` plus metadata |
| `load_from_disk("export").map(...)` | `export/cache-<fingerprint>.arrow` |
| Same map with `cache_file_name="elsewhere/result.arrow"` | exactly `elsewhere/result.arrow` |
| `Dataset.from_dict(...).map(...)`, no explicit output | no persistent `cache_files` in the two-row control |

The [default map path implementation](https://github.com/huggingface/datasets/blob/5.0.1/src/datasets/arrow_dataset.py#L3203-L3211) uses the existing dataset's backing-file directory. It does not read `HF_DATASETS_CACHE` again for every map call.

```bash
HF_DATASETS_CACHE="$LAB/arrow-override" python - <<'PY'
import os
from pathlib import Path
from datasets import load_dataset, load_from_disk

root = Path(os.environ["LAB"])
ds = load_dataset("lhoestq/demo1",
    revision="87ecf163bedca9d80598b528940a9c4f99e14c11",
    split="train", token=False)
export = root / "saved"
assert not export.exists()
ds.save_to_disk(str(export))
saved = load_from_disk(str(export))
mapped = saved.map(lambda row: {"review_length": len(row["review"])})
print("default map:", mapped.cache_files)
assert Path(mapped.cache_files[0]["filename"]).parent == export
target = root / "map-output"
target.mkdir()
explicit = saved.map(lambda row: {"review_length": len(row["review"])},
                     cache_file_name=str(target / "result.arrow"))
print("explicit map:", explicit.cache_files)
assert Path(explicit.cache_files[0]["filename"]) == target / "result.arrow"
PY
```

This is why an export directory can keep growing while the configured cache looks small. `save_to_disk` output is data you chose to retain, not something the Hub CLI manages as a repository cache.

## Finding 4: a copied cache worked without its original path

For each relocation run I copied the complete isolated `HF_HOME` with `cp -a`. Relative filenames, symlink targets, sizes and SHA-256 values matched. I then renamed the original directory so its old path was unavailable.

A new process loaded the pinned config and dataset from the copied root with Hub and Datasets offline modes enabled. All five rows and the mapped result matched their original digests in all three runs. The recorded Arrow paths were under the copy.

The measurement harness also intercepted Python socket connections, proved that interception with an intentional blocked attempt, and checked that an empty-cache local-only lookup failed. No connection attempt occurred during the actual copied-cache load. This was a Python-level check, not an operating-system network disconnect.

The smaller reader reproduction uses the libraries' offline modes:

```bash
(
set -e
test ! -e "$LAB/copied-hf"
test ! -e "$LAB/retained-hf"
cp -a "$HF_HOME" "$LAB/copied-hf"
mv "$HF_HOME" "$LAB/retained-hf"
HF_HOME="$LAB/copied-hf" HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 python - <<'PY'
import os
from pathlib import Path
from datasets import load_dataset
from transformers import AutoConfig

config = AutoConfig.from_pretrained("hf-internal-testing/tiny-random-bert",
    revision="f171d7baecaf37b5da5a3616d8833b9969753535",
    local_files_only=True, token=False)
ds = load_dataset("lhoestq/demo1",
    revision="87ecf163bedca9d80598b528940a9c4f99e14c11",
    split="train", token=False)
rows = list(ds)
print(type(config).__name__, len(rows), ds.cache_files)
assert len(rows) == 5
assert Path(ds.cache_files[0]["filename"]).is_relative_to(Path(os.environ["HF_HOME"]))
PY
test ! -e "$HF_HOME"
mv "$LAB/retained-hf" "$HF_HOME"
)
```

The final commands restore the original lab path. The parentheses run this block in a fail-stop subshell. If the offline load fails after the rename, the block stops and the original remains at `$LAB/retained-hf`; inspect the error before restoring it. This experiment establishes reuse for these small pinned inputs. Moving within the same WSL filesystem does not free space on Windows C:.

## Finding 5: the two cleanup commands remove different things

I created two different map results in one dedicated builder directory, released the first object, and called `cleanup_cache_files()` on the second. It removed one stale `cache-*.arrow` file in each run. The current map output and the base train/test Arrow files remained.

Then `hf cache rm dataset/lhoestq/demo1 --yes` removed the Hub dataset repository. The CLI reported `freed 5.0K`. The generated Arrow files still existed, their hashes were unchanged, and the loaded base/current objects still produced the same rows.

| Action, each repeated in three fresh runs | Removed | Retained |
|---|---|---|
| Current object's `cleanup_cache_files()` | one other map cache file | current map, base Arrow, Hub CSVs |
| `hf cache rm dataset/lhoestq/demo1 --yes` | dataset Hub repository | generated Arrow, model config |

`cleanup_cache_files()` is not a global garbage collector. The [tested implementation](https://github.com/huggingface/datasets/blob/5.0.1/src/datasets/arrow_dataset.py#L3166-L3201) scans the first backing file's directory and protects the receiver's cache files. It does not know whether another object or process still needs a different map cache there. Stop other users of that directory first.

This final example targets only files created in the lab:

```bash
python - <<'PY'
import gc
import os
from pathlib import Path
from datasets import load_dataset

ds = load_dataset("lhoestq/demo1",
    revision="87ecf163bedca9d80598b528940a9c4f99e14c11",
    split="train", cache_dir=str(Path(os.environ["LAB"]) / "cleanup"), token=False)
old = ds.map(lambda row: {"review_length": len(row["review"])})
old_path = Path(old.cache_files[0]["filename"])
del old
gc.collect()
current = ds.map(lambda row: {"upper_review": row["review"].upper()})
removed = current.cleanup_cache_files()
print("removed:", removed)
assert removed == 1 and not old_path.exists()
assert all(Path(item["filename"]).is_file() for item in ds.cache_files + current.cache_files)
PY
hf cache rm dataset/lhoestq/demo1 --dry-run
hf cache rm dataset/lhoestq/demo1 --yes
```

Do not point that command at your real cache until you have checked its target and stopped relevant jobs. The lab directory, its venv, copies and exports remain available for inspection; none of the examples deletes it recursively.

## What this does and does not establish

The 51 cases test storage placement and correctness on one pinned software stack. The dataset is intentionally tiny. It establishes neither large-dataset space ratios nor loading-speed differences. The unchanged path/hash/size/mtime of an identical second map call is file-reuse evidence, not a throughput benchmark.

The public results contain raw-source checksums, row digests, exact versions, per-case outcomes and the three offline-copy checks. A second fresh Ubuntu rootfs was used to replay the reader commands separately from the primary matrix. The initial scout's wrong column-name assumption was corrected before measurement; its failures are retained in the lab record, not counted as library failures.

If the remaining problem is Windows disk usage after removing cache files, the next operation is different: [the WSL VHDX reclaim experiment](/posts/wsl2-sparse-vhd-cannot-compact/) measures that boundary. For other setup failures, use the [local AI fixes index](/fixes/).
