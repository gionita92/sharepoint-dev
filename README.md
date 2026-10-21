# spfx-docs: a Claude Code plugin

Gives Claude an offline, searchable copy of the official
[SharePoint developer docs](https://github.com/SharePoint/sp-dev-docs), so it answers SPFx and SharePoint
development questions from the docs and cites the pages it used.

## What's inside

```
.claude-plugin/plugin.json          plugin manifest
skills/sharepoint-docs/SKILL.md     tells Claude when to use the docs and how to search them
skills/sharepoint-docs/references/  the docs themselves (generated, don't edit by hand)
  index/<area>.md                   one line per page: path — title — description
  docs/<area>/...                   the Markdown/YAML pages, same layout as sp-dev-docs/docs
  includes/...                      shared snippets the pages include
commands/spfx-docs.md               /spfx-docs <question>, for explicit lookups
scripts/sync-docs.py                rebuilds references/ from a local sp-dev-docs clone
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

To try a local checkout without installing it: `claude --plugin-dir /path/to/spfx-docs-plugin`.

## Update the docs

The [Sync sp-dev-docs](.github/workflows/sync-docs.yml) workflow runs every Monday (or on demand from the
Actions tab). It runs the sync against the latest `SharePoint/sp-dev-docs`, and if anything changed it bumps the
patch version and opens a PR on the `sync/sp-dev-docs` branch. Merging that PR releases the update. If the run
flags a new upstream area, add it to `AREAS` or `SKIPPED` in `scripts/sync-docs.py`.

The workflow needs "Allow GitHub Actions to create and approve pull requests" turned on under
Settings → Actions → General.

To sync by hand:

```sh
cd ../sp-dev-docs && git pull && cd -
python3 scripts/sync-docs.py ../sp-dev-docs     # the path defaults to ../sp-dev-docs
```

`skills/sharepoint-docs/references/SOURCE` records which sp-dev-docs commit the bundle came from.

## Releasing an update

After a manual sync or a skill change, bump `version` in both `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json`, then commit and push. Installed copies pick up the new version on
`/plugin marketplace update sharepoint-dev`.

## License

The documentation content is © Microsoft and licensed under
[Creative Commons Attribution 4.0](skills/sharepoint-docs/references/LICENSE). Keep this attribution when you
redistribute the plugin.
