#!/usr/bin/env python3
"""Build the PnP code-sample indexes from each sample's assets/sample.json.

Only the sample.json files are fetched (sparse, blobless, depth-1 clone), so this takes seconds even though the
sample repos are several GB. Pass repo=path pairs to use existing local clones instead.

Usage: python3 scripts/sync-samples.py [webparts=/path/to/sp-dev-fx-webparts ...]
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from synclib import REFS, Changes, upstream_commit

SAMPLE_REPOS = {
    "webparts": "pnp/sp-dev-fx-webparts",
    "extensions": "pnp/sp-dev-fx-extensions",
    "aces": "pnp/sp-dev-fx-aces",
}
SAMPLES = REFS / "samples"


def clone(repo, dest):
    def git(*args, cwd=None):
        subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)

    git("clone", "--depth", "1", "--filter=blob:none", "--sparse", f"https://github.com/{repo}.git", str(dest))
    git("sparse-checkout", "set", "--no-cone", "/samples/*/[Aa]ssets/[Ss]ample.json", cwd=dest)


def sample_files(checkout):
    """Each sample's assets/sample.json, matched case-insensitively (a few samples use Assets/)."""
    return sorted(p for p in (checkout / "samples").glob("*/*/*")
                  if p.parent.name.lower() == "assets" and p.name.lower() == "sample.json")


def one_line(text):
    return " ".join(str(text or "").split())


def sample_row(path):
    """Return the index row for one sample.json, or None if it can't be parsed."""
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        sample = data[0] if isinstance(data, list) else data
        meta = {str(m.get("key", "")).upper(): m.get("value") for m in sample.get("metadata") or []}
    except (OSError, ValueError, AttributeError, IndexError, KeyError) as e:
        print(f"warning: skipping {path}: {e}", file=sys.stderr)
        return None

    facts = [one_line(meta.get("SAMPLE-TYPE")), one_line(meta.get("CLIENT-SIDE-DEV"))]
    if meta.get("SPFX-VERSION"):
        facts.append(f"SPFx {one_line(meta['SPFX-VERSION'])}")
    if sample.get("updateDateTime"):
        facts.append(f"updated {one_line(sample['updateDateTime'])[:10]}")
    if meta.get("PNPCONTROLS"):
        facts.append(f"PnP controls: {one_line(meta['PNPCONTROLS'])}")
    title = one_line(sample.get("title")) or path.parent.parent.name
    url = one_line(sample.get("url"))
    return f"- {title} — {' · '.join(f for f in facts if f)} — {one_line(sample.get('shortDescription'))} — {url}"


def sync_repo(name, repo, checkout, changes, keep):
    rows = [row for path in sample_files(checkout) if (row := sample_row(path))]
    index = SAMPLES / f"{name}.md"
    header = (f"# Samples: {repo}\n\nOne line per sample: title — type · framework · SPFx version · updated"
              " — description — URL. Index only; the code lives on GitHub.\n\n")
    changes.write(index, (header + "\n".join(rows) + "\n").encode("utf-8"))
    keep.add(index)
    print(f"{name:12} {len(rows):5} samples")
    sha, date = upstream_commit(checkout)
    return f"{repo}: {sha} ({date})"


def main():
    local = dict(arg.split("=", 1) for arg in sys.argv[1:])
    unknown = set(local) - set(SAMPLE_REPOS)
    if unknown:
        sys.exit(f"Unknown sample repo(s): {', '.join(sorted(unknown))}. Known: {', '.join(SAMPLE_REPOS)}")

    changes = Changes()
    keep = set()
    sources = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, repo in SAMPLE_REPOS.items():
            checkout = Path(local[name]).resolve() if name in local else Path(tmp) / name
            if name not in local:
                clone(repo, checkout)
            sources.append(sync_repo(name, repo, checkout, changes, keep))

    changes.prune(SAMPLES, keep | {SAMPLES / "SOURCE"})
    changes.report()
    (SAMPLES / "SOURCE").write_text("\n".join(sources) + "\n", encoding="utf-8")
    for line in sources:
        print(f"Source: {line}")


if __name__ == "__main__":
    main()
