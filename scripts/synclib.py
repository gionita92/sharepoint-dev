"""Helpers shared by sync-docs.py and sync-samples.py."""
import subprocess
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
REFS = PLUGIN_ROOT / "skills" / "sharepoint-docs" / "references"


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

    def report(self):
        for label, paths in (("added", self.added), ("updated", self.updated), ("removed", self.removed)):
            for p in paths:
                print(f"  {label:8} {p}")
        print(f"Changes: {len(self.added)} added, {len(self.updated)} updated, {len(self.removed)} removed")


def upstream_commit(source):
    """Return (sha, commit date) of the clone's HEAD, or ("unknown", "unknown") if it isn't a git checkout."""
    try:
        out = subprocess.run(["git", "-C", str(source), "log", "-1", "--format=%H %cs"],
                             capture_output=True, text=True, check=True).stdout.split()
        return out[0], out[1]
    except (OSError, subprocess.CalledProcessError, IndexError):
        return "unknown", "unknown"
