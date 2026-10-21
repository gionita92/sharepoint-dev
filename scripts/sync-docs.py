#!/usr/bin/env python3
"""Sync the chosen sp-dev-docs areas into the skill and rebuild the per-area indexes.

Only files whose content changed are written; files removed upstream are deleted. Each index row carries the
page's last upstream commit date, so the clone needs its git history (not a --depth 1 clone).

Usage: python3 scripts/sync-docs.py [path-to-sp-dev-docs-clone]
"""
import subprocess
import sys
from pathlib import Path

from synclib import PLUGIN_ROOT, REFS, Changes, upstream_commit

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


def last_updated(source):
    """Return {repo-relative path: YYYY-MM-DD of its last commit}, or {} if the clone has no usable history.

    ms.date in the frontmatter is often years behind the real last edit, so this is the freshness signal.
    """
    def git(*args):
        return subprocess.run(["git", "-C", str(source), *args], capture_output=True, text=True, check=True).stdout

    try:
        if git("rev-parse", "--is-shallow-repository").strip() == "true":
            print("warning: sp-dev-docs clone is shallow; index rows will have no updated dates", file=sys.stderr)
            return {}
        log = git("log", "--format=@%cs", "--name-only", "--", "docs", "includes")
    except (OSError, subprocess.CalledProcessError):
        print("warning: sp-dev-docs path is not a git clone; index rows will have no updated dates", file=sys.stderr)
        return {}

    dates = {}
    date = None
    for line in log.splitlines():
        if line.startswith("@"):
            date = line[1:]
        elif line and line not in dates:
            dates[line] = date
    return dates


def sync_area(src_docs, area, changes, keep, dates):
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
        updated = dates.get(f"docs/{rel.as_posix()}")
        if updated:
            row += f" — updated {updated}"
        rows.append(row)

    index = REFS / "index" / f"{area}.md"
    header = (f"# Index: {area}\n\nOne line per page: path (relative to references/) — title — description"
              " — updated <date of the page's last upstream commit>.\n\n")
    changes.write(index, (header + "\n".join(rows) + "\n").encode("utf-8"))
    keep.add(index)
    return len(rows), copied


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else PLUGIN_ROOT.parent / "sp-dev-docs"
    source = source.resolve()
    src_docs = source / "docs"
    if not src_docs.is_dir():
        sys.exit(f"Not an sp-dev-docs clone (no docs/ folder): {source}")

    dates = last_updated(source)
    changes = Changes()
    keep = set()
    total = 0
    for area in AREAS:
        indexed, copied = sync_area(src_docs, area, changes, keep, dates)
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
    changes.report()

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
