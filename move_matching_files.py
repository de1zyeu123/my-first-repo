#!/usr/bin/env python3
"""Move files whose names contain a keyword into a dedicated folder.

Usage:
    python move_matching_files.py /path/to/main keyword

The script searches recursively through the target directory (including all
subdirectories) for files whose names include the provided keyword. Matching
files are moved into a folder inside the target directory that shares the name
of the keyword (creating it if it does not already exist).
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import Iterable, Iterator


def iter_matching_files(base_dir: Path, keyword: str, exclude: Path) -> Iterator[Path]:
    """Yield files whose names contain ``keyword`` (case-insensitive).

    Args:
        base_dir: Directory to walk.
        keyword: Keyword to match within file names.
        exclude: Directory to skip (e.g., destination folder).
    """

    keyword_lower = keyword.lower()
    for dirpath, _, filenames in os.walk(base_dir):
        current_dir = Path(dirpath)
        try:
            current_dir.relative_to(exclude)
        except ValueError:
            pass
        else:
            # Skip walking inside the destination folder to prevent moving
            # files we already relocated.
            continue

        for name in filenames:
            if keyword_lower in name.lower():
                yield current_dir / name


def unique_destination(dest_dir: Path, name: str) -> Path:
    """Return a destination path that avoids overwriting existing files."""

    candidate = dest_dir / name
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1
    while True:
        numbered = dest_dir / f"{stem}_{counter}{suffix}"
        if not numbered.exists():
            return numbered
        counter += 1


def move_files(paths: Iterable[Path], dest_dir: Path) -> list[tuple[Path, Path]]:
    """Move each file in ``paths`` into ``dest_dir``.

    Returns a list of (source, destination) tuples describing the moves.
    """

    moves: list[tuple[Path, Path]] = []
    for src in paths:
        dest = unique_destination(dest_dir, src.name)
        shutil.move(str(src), dest)
        moves.append((src, dest))
    return moves


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        type=Path,
        help="Directory to search for matching files.",
    )
    parser.add_argument(
        "keyword",
        help="Keyword to look for in file names. Matching is case-insensitive.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report files that would be moved without moving them.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = args.target.expanduser().resolve()

    if not base_dir.exists() or not base_dir.is_dir():
        raise SystemExit(f"Target directory '{base_dir}' does not exist or is not a directory.")

    keyword = args.keyword.strip()
    if not keyword:
        raise SystemExit("Keyword must not be empty.")

    dest_dir = base_dir / keyword
    dest_dir.mkdir(exist_ok=True)

    matches = list(iter_matching_files(base_dir, keyword, dest_dir))

    if not matches:
        print(f"No files containing '{keyword}' were found under {base_dir}.")
        return

    if args.dry_run:
        print("Dry run: the following files would be moved:")
        for path in matches:
            print(f" - {path}")
        return

    moves = move_files(matches, dest_dir)
    print(f"Moved {len(moves)} file(s) into '{dest_dir}'.")
    for src, dest in moves:
        print(f" - {src} -> {dest}")


if __name__ == "__main__":
    main()
