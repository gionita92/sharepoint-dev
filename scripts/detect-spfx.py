#!/usr/bin/env python3
"""Detect an SPFx project in the working directory and describe it for Claude.

Run by the plugin's SessionStart hook: whatever it prints is added to the session context. Prints nothing when
there's no SPFx project, and never fails, so it can't break a session.

Usage: python3 scripts/detect-spfx.py [--json] [project-dir]
"""
import json
import os
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
RELEASES = PLUGIN_ROOT / "skills" / "sharepoint-docs" / "references" / "docs" / "spfx"
HEFT_PACKAGES = ("@rushstack/heft", "@microsoft/spfx-web-build-rig")
GULP_PACKAGES = ("@microsoft/sp-build-web",)
SKIP_DIRS = {"node_modules", "lib", "dist", "temp", "release", "sharepoint"}


def version_key(version):
    return tuple(int(n) for n in re.findall(r"\d+", version)[:3])


def newest_bundled_release():
    versions = [p.stem[len("release-"):] for p in RELEASES.glob("release-*.md")]
    versions = [v for v in versions if re.fullmatch(r"\d+\.\d+\.\d+", v)]
    return max(versions, key=version_key) if versions else None


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def describe(folder):
    """Return a dict describing the SPFx project in folder, or None if it isn't one."""
    pkg = read_json(folder / "package.json")
    if not isinstance(pkg, dict):
        return None
    deps = {**(pkg.get("dependencies") or {}), **(pkg.get("devDependencies") or {})}
    if not any(name.startswith("@microsoft/sp-") for name in deps):
        return None

    version = re.sub(r"^[^\d]*", "", str(deps.get("@microsoft/sp-core-library", ""))) or None
    if not version:
        yo = read_json(folder / ".yo-rc.json") or {}
        version = (yo.get("@microsoft/generator-sharepoint") or {}).get("version")

    if any(name in deps for name in HEFT_PACKAGES):
        toolchain = "Heft"
    elif any(name in deps for name in GULP_PACKAGES) or (folder / "gulpfile.js").is_file():
        toolchain = "gulp"
    elif version:
        toolchain = "Heft" if version_key(version) >= (1, 22) else "gulp"
    else:
        toolchain = None

    return {"path": folder.as_posix(), "spfx_version": version, "toolchain": toolchain}


def find_projects(root):
    project = describe(root)
    if project:
        return [project]
    projects = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and not child.name.startswith(".") and child.name not in SKIP_DIRS:
            project = describe(child)
            if project:
                projects.append(project)
    return projects


def render(projects, root, newest):
    lines = []
    for p in projects:
        rel = os.path.relpath(p["path"], root)
        where = "./" if rel == "." else f"./{rel}/"
        version = f"SPFx {p['spfx_version']}" if p["spfx_version"] else "an unknown SPFx version"
        toolchain = f" ({p['toolchain']} toolchain)" if p["toolchain"] else ""
        lines.append(f"SPFx project detected: {where} uses {version}{toolchain}.")
    if newest:
        lines.append(f"Newest SPFx release in the bundled sharepoint-docs: {newest}.")
    toolchains = {p["toolchain"] for p in projects if p["toolchain"]}
    if len(toolchains) == 1:
        lines.append(f"Give {toolchains.pop()} commands. Supported Node.js/TypeScript ranges per release are in "
                     "the sharepoint-docs skill's references/docs/spfx/compatibility.md.")
    return "\n".join(lines)


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    root = Path(args[0] if args else os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    projects = find_projects(root)
    newest = newest_bundled_release()
    if "--json" in sys.argv:
        print(json.dumps({"projects": projects, "newest_bundled_release": newest}, indent=2))
    elif projects:
        print(render(projects, root, newest))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # never break the session over detection
        pass
