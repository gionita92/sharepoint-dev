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

## Use it locally

```sh
claude --plugin-dir /path/to/spfx-docs-plugin
```

Then just ask an SPFx question, or use `/spfx-docs how do I add a property pane to a web part?`.

## Update the docs

```sh
cd ../sp-dev-docs && git pull && cd -
python3 scripts/sync-docs.py ../sp-dev-docs     # the path defaults to ../sp-dev-docs
```

## Sharing later

Push this folder to a GitHub repo and add `.claude-plugin/marketplace.json` at the repo root, listing this plugin.
Others can then run `/plugin marketplace add <owner>/<repo>` and `/plugin install spfx-docs@<marketplace>`.

## License

The documentation content is © Microsoft and licensed under
[Creative Commons Attribution 4.0](skills/sharepoint-docs/references/LICENSE). Keep this attribution when you
redistribute the plugin.
