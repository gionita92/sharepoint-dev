# spfx-docs: a Claude Code plugin

Gives Claude an offline, searchable copy of the official
[SharePoint developer docs](https://github.com/SharePoint/sp-dev-docs), so it answers SPFx and SharePoint
development questions from the docs and cites the pages it used.

It also:
- detects your project's SPFx version and toolchain (Heft or gulp) when a session starts, so answers match it;
- shows when each cited page was last updated upstream, and flags stale pages on time-sensitive topics;
- points to working [PnP community samples](https://pnp.github.io/) when you want an example;
- reviews SPFx code against the docs with `/spfx-review`, citing a page for every finding.

## What's inside

```
.claude-plugin/plugin.json          plugin manifest
skills/sharepoint-docs/SKILL.md     tells Claude when to use the docs and how to search them
skills/sharepoint-docs/references/  generated content, don't edit by hand
  index/<area>.md                   one line per page: path — title — description — updated date
  docs/<area>/...                   the Markdown/YAML pages, same layout as sp-dev-docs/docs
  includes/...                      shared snippets the pages include
  samples/<repo>.md                 one line per PnP sample: title, type, SPFx version, description, URL
  SOURCE, samples/SOURCE            upstream commits the content was built from
commands/spfx-docs.md               /spfx-docs <question>, for explicit lookups
commands/spfx-review.md             /spfx-review [path | diff], runs the reviewer
agents/spfx-reviewer.md             reviews SPFx code against the docs
hooks/hooks.json                    session-start hook that runs detect-spfx.py
scripts/detect-spfx.py              finds the SPFx version and toolchain in the working directory
scripts/sync-docs.py                rebuilds the docs and indexes from an sp-dev-docs clone
scripts/sync-samples.py             rebuilds the samples index from the PnP sample repos
scripts/synclib.py                  helpers shared by the sync scripts
```

Bundled areas: `spfx`, `general-development`, `declarative-customization`, `solution-guidance`,
`scenario-guidance`, `business-apps`, `design`, `features`, `schema`. To change this list, edit `AREAS` in
`scripts/sync-docs.py` and the area table in `SKILL.md`.

## Install

In Claude Code:

```
/plugin install spfx-docs --marketplace gionita92/sharepoint-dev
```

On older Claude Code versions, add the marketplace first:

```
/plugin marketplace add gionita92/sharepoint-dev
/plugin install spfx-docs@sharepoint-dev
```

In GitHub Copilot CLI:

```sh
copilot plugin marketplace add gionita92/sharepoint-dev
copilot plugin install spfx-docs@sharepoint-dev
```

Then just ask an SPFx question, or use `/spfx-docs how do I add a property pane to a web part?`.
To review code, run `/spfx-review` (whole project), `/spfx-review diff` or `/spfx-review src/webparts/foo`.

The version-detection hook and the reviewer agent are Claude Code features. In other tools that don't run plugin
hooks or agents, the docs skill still works and reads the version from `package.json` itself.

To try a local checkout without installing it: `claude --plugin-dir /path/to/spfx-docs-plugin`.

## Update the docs

The [Sync sp-dev-docs](.github/workflows/sync-docs.yml) workflow runs every Monday (or on demand from the
Actions tab). It syncs the latest `SharePoint/sp-dev-docs` and rebuilds the samples index from the PnP sample
repos. If anything changed, it bumps the patch version and opens a PR on the `sync/sp-dev-docs` branch. Merging that PR releases the update. If the run
flags a new upstream area, add it to `AREAS` or `SKIPPED` in `scripts/sync-docs.py`.

The workflow needs "Allow GitHub Actions to create and approve pull requests" turned on under
Settings → Actions → General.

To sync by hand:

```sh
cd ../sp-dev-docs && git pull && cd -
python3 scripts/sync-docs.py ../sp-dev-docs     # the path defaults to ../sp-dev-docs
python3 scripts/sync-samples.py                 # fetches only the sample.json files, takes seconds
```

`sync-docs.py` needs a clone with full git history to fill in the `updated` dates; with a `--depth 1` clone it
warns and leaves them out. `sync-samples.py` accepts `webparts=<path>` (also `extensions=`, `aces=`) to use
local clones of the sample repos instead of fetching.

## Releasing an update

After a manual sync or a skill change, bump `version` in both `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json`, then commit and push. Installed copies pick up the new version on
`/plugin marketplace update sharepoint-dev`.

## License

The documentation content is © Microsoft and licensed under
[Creative Commons Attribution 4.0](skills/sharepoint-docs/references/LICENSE). Keep this attribution when you
redistribute the plugin. The samples index holds only titles, descriptions and links to the PnP sample repos;
the sample code stays in those repos under their own licenses.
