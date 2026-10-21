#!/usr/bin/env python3
"""Copy the chosen sp-dev-docs areas into the skill and rebuild the per-area indexes.

Usage: python3 scripts/sync-docs.py [path-to-sp-dev-docs-clone]
"""
import shutil
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


def sync_area(src_docs, area):
    src = src_docs / area
    dest = REFS / "docs" / area
    rows = []
    for path in sorted(src.rglob("*")):
        if not path.is_file() or path.suffix not in DOC_SUFFIXES:
            continue
        rel = path.relative_to(src_docs)
        target = REFS / "docs" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        if path.name in NOT_INDEXED:
            continue
        title, description = read_meta(path)
        row = f"- docs/{rel.as_posix()} — {title or path.stem}"
        if description:
            row += f" — {description}"
        rows.append(row)

    index = REFS / "index" / f"{area}.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    header = f"# Index: {area}\n\nOne line per page: path (relative to references/) — title — description.\n\n"
    index.write_text(header + "\n".join(rows) + "\n", encoding="utf-8")
    return len(rows), sum(1 for _ in dest.rglob("*") if _.is_file())


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

    for sub in ("docs", "index", "includes"):
        shutil.rmtree(REFS / sub, ignore_errors=True)

    total = 0
    for area in AREAS:
        indexed, copied = sync_area(src_docs, area)
        total += copied
        print(f"{area:28} {copied:5} files  {indexed:5} indexed")

    shutil.copytree(source / "includes", REFS / "includes")
    shutil.copy2(source / "LICENSE", REFS / "LICENSE")
    print(f"{'includes':28} {sum(1 for p in (REFS / 'includes').rglob('*') if p.is_file()):5} files")
    print(f"Total docs: {total}  ->  {REFS}")

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
