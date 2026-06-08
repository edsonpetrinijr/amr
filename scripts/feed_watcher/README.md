# feed_watcher

A **throwaway diagnostic** to empirically confirm how often the Caterpillar ERP
order-feed file updates on a Windows UNC share, and to capture the exact
wall-clock times each change lands. This is **not** part of the main app — it is
self-contained and uses the **Python standard library only**.

## Safety rule (read this first)

The script **never opens or holds the original feed file open in place.** If a
handle is held while the ERP writes, the data can corrupt. The script only:

1. `os.stat()` the original (cheap metadata: size + mtime), and
2. `shutil.copy2()` the original to a **local** file (opens, reads, closes fast).

All inspection — sha256 hashing and line counting — runs on the **local copy**,
never the original. Treat the source as strictly read-only.

## Usage

```powershell
python scripts\feed_watcher\feed_watcher.py --source "\\b8nas01.brazil.cat.com\accfiles\B8HK\12345.txt"
```

The exact filename (`12345.txt`) is unknown ahead of time (date or sequence
number), so `--source` is **required** and not hardcoded.

### Options

| Flag | Default | Meaning |
|------|---------|---------|
| `--source` | *(required)* | UNC path to the feed file. |
| `--interval` | `60` | Poll interval in seconds. Changes are expected ~every 15 min; polling faster pins the exact clock time. |
| `--out-dir` | this folder | Where `snapshots/`, `change_log.csv`, `errors.log`, `latest_copy.txt` are written. |
| `--keep-snapshots` | on | Archive a dated copy of the file on every change. |
| `--no-snapshots` | — | Skip per-change archives (still keeps the latest copy + CSV). |
| `--max-snapshots N` | `0` (unlimited) | Ring buffer: keep only the newest N snapshot files. |

`--help` prints all options.

## Outputs

- **`change_log.csv`** — one row per detected change (and the first baseline):

  | column | meaning |
  |--------|---------|
  | `local_timestamp_iso` | when we observed the change (local tz, with offset) |
  | `utc_timestamp_iso` | same instant in UTC |
  | `original_mtime_iso` | the original file's mtime |
  | `size_bytes` | file size |
  | `sha256` | content hash of the local copy |
  | `line_count` | number of newlines in the file |
  | `seconds_since_previous_change` | delta from the previous change (blank for baseline) |

- **`snapshots/feed_<timestamp>.txt`** — dated copies kept as history
  (e.g. `feed_2026-06-08T09-41-00_-03.txt`). Disable with `--no-snapshots`.
- **`latest_copy.txt`** — the most recent local copy (always refreshed).
- **`errors.log`** — transient failures (share down, locked file, copy error).
  The loop logs and **keeps running**; it never crashes on a network blip.

## Live console

```
[BASELINE] 2026-06-08T09:26:00-03:00  size=20480B  lines=512  sha=9f2b1c...
[CHANGE #1] 2026-06-08T09:41:00-03:00  size=20612B  lines=515  sha=a1c8e4...  since_prev=900.0s (~15.0 min)
```

Press **Ctrl+C** for a clean shutdown summary with min / median / max interval
between changes — eyeball that against the expected ~15-minute cadence.
