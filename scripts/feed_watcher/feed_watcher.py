#!/usr/bin/env python3
"""
feed_watcher.py — throwaway diagnostic to verify how often a Caterpillar ERP
order-feed file updates on a Windows UNC share, and capture the wall-clock
times it changes.

SAFETY RULE (non-negotiable):
    We NEVER open or hold the original feed file open in place. If the ERP is
    mid-write while we hold a handle, the data can corrupt. We only ever:
      - os.stat() the original (cheap metadata read), and
      - shutil.copy2() it to a LOCAL folder (opens, reads, closes quickly).
    All inspection (hashing, line counting) happens on the LOCAL COPY.

Stdlib only. Tested on Windows Python 3.

Example:
    python feed_watcher.py --source "\\\\b8nas01.brazil.cat.com\\accfiles\\B8HK\\12345.txt"
"""

import argparse
import csv
import hashlib
import os
import shutil
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# --------------------------------------------------------------------------- #
# Time helpers
# --------------------------------------------------------------------------- #
def now_local() -> datetime:
    """Timezone-aware local 'now' (so we capture UTC offset, e.g. -03:00)."""
    return datetime.now().astimezone()


def iso_local(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def fs_timestamp(dt: datetime) -> str:
    """Filesystem-safe timestamp for snapshot filenames.

    Example: 2026-06-08T09-41-00_-03
    """
    base = dt.strftime("%Y-%m-%dT%H-%M-%S")
    # UTC offset like -0300 -> _-03
    off = dt.strftime("%z")  # e.g. -0300
    hh = off[:3] if off else "+00"
    return f"{base}_{hh}"


# --------------------------------------------------------------------------- #
# Snapshot data
# --------------------------------------------------------------------------- #
class Snapshot:
    """A point-in-time observation of the feed file."""

    __slots__ = ("size", "mtime", "sha256", "line_count", "observed_at")

    def __init__(self, size, mtime, sha256, line_count, observed_at):
        self.size = size
        self.mtime = mtime              # original file mtime (epoch float)
        self.sha256 = sha256
        self.line_count = line_count
        self.observed_at = observed_at  # aware datetime when we observed it

    def differs_from(self, other) -> bool:
        """A change is anything where size, mtime, or content hash moved.

        Hash is the authoritative signal (mtime can be flaky on shares), but we
        treat any of the three changing as a change.
        """
        if other is None:
            return True
        return (
            self.sha256 != other.sha256
            or self.size != other.size
            or int(self.mtime) != int(other.mtime)
        )


# --------------------------------------------------------------------------- #
# Core inspection (always operates on a LOCAL copy)
# --------------------------------------------------------------------------- #
def hash_and_count(local_path: Path):
    """Compute sha256 + line count of a LOCAL file in a single streamed read."""
    h = hashlib.sha256()
    line_count = 0
    with open(local_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
            line_count += chunk.count(b"\n")
    return h.hexdigest(), line_count


def safe_copy(source: Path, dest: Path) -> None:
    """Copy original -> dest. copy2 opens/reads/closes quickly (metadata too)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
CSV_COLUMNS = [
    "local_timestamp_iso",
    "utc_timestamp_iso",
    "original_mtime_iso",
    "size_bytes",
    "sha256",
    "line_count",
    "seconds_since_previous_change",
]


def ensure_csv_header(csv_path: Path) -> None:
    if not csv_path.exists():
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(CSV_COLUMNS)


def append_csv_row(csv_path: Path, row: list) -> None:
    with open(csv_path, "a", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow(row)


def log_error(errors_path: Path, message: str) -> None:
    errors_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = iso_local(now_local())
    line = f"{stamp}  {message}"
    print(f"[WARN] {line}", file=sys.stderr)
    with open(errors_path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


# --------------------------------------------------------------------------- #
# Snapshot ring buffer
# --------------------------------------------------------------------------- #
def prune_snapshots(snap_dir: Path, max_snapshots: int) -> None:
    """Keep only the newest `max_snapshots` snapshot files (oldest deleted)."""
    if not max_snapshots or max_snapshots <= 0:
        return
    snaps = sorted(
        snap_dir.glob("feed_*"),
        key=lambda p: p.stat().st_mtime,
    )
    excess = len(snaps) - max_snapshots
    for old in snaps[: max(0, excess)]:
        try:
            old.unlink()
        except OSError:
            pass


# --------------------------------------------------------------------------- #
# Watcher
# --------------------------------------------------------------------------- #
class FeedWatcher:
    def __init__(self, args):
        self.source = Path(args.source)
        self.interval = args.interval
        self.out_dir = Path(args.out_dir)
        self.keep_snapshots = args.keep_snapshots
        self.max_snapshots = args.max_snapshots

        self.snap_dir = self.out_dir / "snapshots"
        self.latest_path = self.out_dir / "latest_copy.txt"
        self.csv_path = self.out_dir / "change_log.csv"
        self.errors_path = self.out_dir / "errors.log"

        self.prev = None                 # type: Snapshot | None
        self.prev_change_at = None       # type: datetime | None
        self.intervals = []              # seconds between detected changes
        self.change_count = 0

    # ----- one poll cycle ------------------------------------------------- #
    def poll_once(self) -> None:
        """Stat the original cheaply, copy locally, inspect the copy."""
        # 1) Cheap metadata read of the ORIGINAL (no content open).
        st = self.source.stat()  # raises if missing/unreachable -> caught upstream
        size = st.st_size
        mtime = st.st_mtime

        observed_at = now_local()

        # 2) Copy to the local "latest" file (quick open/read/close).
        #    We always refresh latest_copy.txt so inspection never touches origin.
        safe_copy(self.source, self.latest_path)

        # 3) Inspect the LOCAL copy.
        sha256, line_count = hash_and_count(self.latest_path)

        current = Snapshot(size, mtime, sha256, line_count, observed_at)

        if not current.differs_from(self.prev):
            # No change; nothing to log. (Quiet to keep console readable.)
            return

        # ---- A change (or the first baseline) was detected ---------------- #
        is_baseline = self.prev is None
        seconds_since_prev = ""
        if self.prev_change_at is not None:
            delta = (observed_at - self.prev_change_at).total_seconds()
            seconds_since_prev = f"{delta:.1f}"
            self.intervals.append(delta)

        # Archive a dated snapshot copy (history), if enabled.
        if self.keep_snapshots:
            snap_name = f"feed_{fs_timestamp(observed_at)}.txt"
            try:
                safe_copy(self.latest_path, self.snap_dir / snap_name)
                prune_snapshots(self.snap_dir, self.max_snapshots)
            except OSError as exc:
                log_error(self.errors_path, f"snapshot archive failed: {exc!r}")

        # Append CSV row.
        original_mtime_iso = iso_local(
            datetime.fromtimestamp(mtime).astimezone()
        )
        append_csv_row(
            self.csv_path,
            [
                iso_local(observed_at),
                iso_utc(observed_at),
                original_mtime_iso,
                size,
                sha256,
                line_count,
                seconds_since_prev,
            ],
        )

        # Console summary.
        if is_baseline:
            print(
                f"[BASELINE] {iso_local(observed_at)}  "
                f"size={size}B  lines={line_count}  sha={sha256[:12]}"
            )
        else:
            self.change_count += 1
            delta_str = (
                f"{seconds_since_prev}s "
                f"(~{float(seconds_since_prev) / 60:.1f} min)"
                if seconds_since_prev
                else "n/a"
            )
            print(
                f"[CHANGE #{self.change_count}] {iso_local(observed_at)}  "
                f"size={size}B  lines={line_count}  sha={sha256[:12]}  "
                f"since_prev={delta_str}"
            )

        self.prev = current
        self.prev_change_at = observed_at

    # ----- main loop ------------------------------------------------------ #
    def run(self) -> int:
        ensure_csv_header(self.csv_path)
        print(
            f"Watching: {self.source}\n"
            f"Interval: {self.interval}s   Out: {self.out_dir}\n"
            f"Snapshots: {'on' if self.keep_snapshots else 'off'}"
            + (
                f" (ring buffer {self.max_snapshots})"
                if self.keep_snapshots and self.max_snapshots
                else ""
            )
            + "\nPress Ctrl+C to stop.\n"
        )
        try:
            while True:
                try:
                    self.poll_once()
                except FileNotFoundError:
                    log_error(
                        self.errors_path,
                        f"source not found / share unreachable: {self.source}",
                    )
                except PermissionError:
                    # Likely locked mid-write; retry next interval.
                    log_error(
                        self.errors_path,
                        f"permission/lock error (file mid-write?): {self.source}",
                    )
                except OSError as exc:
                    log_error(self.errors_path, f"transient OS error: {exc!r}")
                except Exception as exc:  # never crash the loop
                    log_error(self.errors_path, f"unexpected error: {exc!r}")

                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.shutdown_summary()
        return 0

    # ----- summary -------------------------------------------------------- #
    def shutdown_summary(self) -> None:
        print("\n--- Shutdown summary ---")
        print(f"Changes detected (excl. baseline): {self.change_count}")
        if self.intervals:
            mn = min(self.intervals)
            mx = max(self.intervals)
            med = statistics.median(self.intervals)
            print(
                f"Interval between changes (s): "
                f"min={mn:.1f}  median={med:.1f}  max={mx:.1f}  "
                f"(median ~{med / 60:.1f} min)"
            )
        else:
            print("No change intervals recorded yet.")
        print(f"CSV log: {self.csv_path}")
        print("------------------------")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Monitor a Caterpillar ERP order-feed file on a Windows "
        "share to verify update cadence. Copies locally before inspecting; "
        "never holds the original open.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--source",
        required=True,
        help=r"UNC path to the feed file, e.g. "
        r"\\b8nas01.brazil.cat.com\accfiles\B8HK\12345.txt",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=60.0,
        help="Polling interval in seconds.",
    )
    p.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parent),
        help="Output dir for snapshots/, change_log.csv, errors.log.",
    )
    snap = p.add_mutually_exclusive_group()
    snap.add_argument(
        "--keep-snapshots",
        dest="keep_snapshots",
        action="store_true",
        help="Archive a dated copy on every change (default).",
    )
    snap.add_argument(
        "--no-snapshots",
        dest="keep_snapshots",
        action="store_false",
        help="Do NOT archive every change (still keeps latest copy + CSV).",
    )
    p.set_defaults(keep_snapshots=True)
    p.add_argument(
        "--max-snapshots",
        type=int,
        default=0,
        help="Ring-buffer cap on snapshot files (0 = unlimited).",
    )
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.interval <= 0:
        print("--interval must be > 0", file=sys.stderr)
        return 2
    return FeedWatcher(args).run()


if __name__ == "__main__":
    raise SystemExit(main())
