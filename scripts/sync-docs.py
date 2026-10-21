#!/usr/bin/env python3
"""Sync the chosen sp-dev-docs areas into the skill and rebuild the per-area indexes.

Only files whose content changed are written; files removed upstream are deleted.

Usage: python3 scripts/sync-docs.py [path-to-sp-dev-docs-clone]
"""
import subprocess
import sys
from pathlib import Path

AREAS = [
    "spfx",
    "general-development",
    "declarative-customization",
    "solution-guidance",
    "scenario-guidance",
    "business-apps",
    "design",
    "features",
    "schema",
]
# Upstream folders we deliberately leave out; anything not here or in AREAS triggers a warning.
SKIPPED = {"apis", "breadcrumb", "community", "embedded", "images", "sp-add-ins", "sp-add-ins-modernize",
           "training", "transform"}
DOC_SUFFIXES = {".md", ".yml"}
NOT_INDEXED = {"toc.yml", "index.yml", "breadcrumb.yml"}

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
REFS = PLUGIN_ROOT / "skills" / "sharepoint-docs" / "references"


def read_meta(path):
    """Return (title, description) from markdown frontmatter or YamlMime metadata."""
    title = description = ""
    with path.open(encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if i > 40:
                break
            stripped = line.strip()
            if not title and stripped.startswith("title:"):
                title = stripped[len("title:"):].strip().strip("'\"")
            elif not description and stripped.startswith("description:"):
                description = stripped[len("description:"):].strip().strip("'\"")
            if title and description:
                break
    return title, description


class Changes:
    """Tracks which files under references/ were added, updated or removed."""

    def __init__(self):
        self.added, self.updated, self.removed = [], [], []

    def __len__(self):
        return len(self.added) + len(self.updated) + len(self.removed)

    def write(self, target, data):
        """Write bytes to target unless it already has exactly that content."""
        exists = target.is_file()
        if exists and target.read_bytes() == data:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        (self.updated if exists else self.added).append(target.relative_to(REFS).as_posix())

    def prune(self, root, keep):
        """Delete files under root that aren't in keep, then any directories left empty."""
        if not root.is_dir():
            return
        for path in sorted(root.rglob("*")):
            if path.is_file() and path not in keep:
                path.unlink()
                self.removed.append(path.relative_to(REFS).as_posix())
        for path in sorted(root.rglob("*"), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()


def sync_area(src_docs, area, changes, keep):
    src = src_docs / area
    rows = []
    copied = 0
    for path in sorted(src.rglob("*")):
        if not path.is_file() or path.suffix not in DOC_SUFFIXES:
            continue
        rel = path.relative_to(src_docs)
        target = REFS / "docs" / rel
        changes.write(target, path.read_bytes())
        keep.add(target)
        copied += 1
        if path.name in NOT_INDEXED:
            continue
        title, description = read_meta(path)
        row = f"- docs/{rel.as_posix()} — {title or path.stem}"
        if description:
            row += f" — {description}"
        rows.append(row)

    index = REFS / "index" / f"{area}.md"
    header = f"# Index: {area}\n\nOne line per page: path (relative to references/) — title — description.\n\n"
    changes.write(index, (header + "\n".join(rows) + "\n").encode("utf-8"))
    keep.add(index)
    return len(rows), copied


def upstream_commit(source):
    """Return (sha, commit date) of the clone's HEAD, or ("unknown", "unknown") if it isn't a git checkout."""
    try:
        out = subprocess.run(["git", "-C", str(source), "log", "-1", "--format=%H %cs"],
                             capture_output=True, text=True, check=True).stdout.split()
        return out[0], out[1]
    except (OSError, subprocess.CalledProcessError, IndexError):
        return "unknown", "unknown"


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else PLUGIN_ROOT.parent / "sp-dev-docs"
    source = source.resolve()
    src_docs = source / "docs"
    if not src_docs.is_dir():
        sys.exit(f"Not an sp-dev-docs clone (no docs/ folder): {source}")

    changes = Changes()
    keep = set()
    total = 0
    for area in AREAS:
        indexed, copied = sync_area(src_docs, area, changes, keep)
        total += copied
        print(f"{area:28} {copied:5} files  {indexed:5} indexed")

    includes = 0
    for path in sorted((source / "includes").rglob("*")):
        if path.is_file():
            target = REFS / "includes" / path.relative_to(source / "includes")
            changes.write(target, path.read_bytes())
            keep.add(target)
            includes += 1
    changes.write(REFS / "LICENSE", (source / "LICENSE").read_bytes())
    print(f"{'includes':28} {includes:5} files")

    for sub in ("docs", "index", "includes"):
        changes.prune(REFS / sub, keep)
    print(f"Total docs: {total}  ->  {REFS}")

    for label, paths in (("added", changes.added), ("updated", changes.updated), ("removed", changes.removed)):
        for p in paths:
            print(f"  {label:8} {p}")
    print(f"Changes: {len(changes.added)} added, {len(changes.updated)} updated, {len(changes.removed)} removed")

    sha, date = upstream_commit(source)
    (REFS / "SOURCE").write_text(
        f"repo: https://github.com/SharePoint/sp-dev-docs\ncommit: {sha}\ndate: {date}\n", encoding="utf-8")
    print(f"Source: sp-dev-docs@{sha[:7]} ({date})")

    new_areas = sorted(p.name for p in src_docs.iterdir() if p.is_dir() and p.name not in set(AREAS) | SKIPPED)
    for name in new_areas:
        print(f"warning: new upstream area docs/{name}/ is not bundled; add it to AREAS or SKIPPED",
              file=sys.stderr)


if __name__ == "__main__":
    main()
