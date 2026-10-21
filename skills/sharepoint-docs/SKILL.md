---
name: sharepoint-docs
description: Look up official Microsoft SharePoint developer documentation (bundled offline copy of sp-dev-docs). Use for any question about SharePoint Framework (SPFx) — web parts, extensions, Adaptive Card Extensions / Viva Connections, library components, Heft/gulp toolchain, release notes, Teams/Outlook hosting — and about SharePoint list/column/view formatting, list forms, site designs and site scripts, site theming, CAML/schema XML (fields, content types, features, Elements.xml), SharePoint REST/CSOM/JSOM, search, PnP provisioning, web part design guidance, and Power Apps/Power Automate integration with SharePoint.
---

# SharePoint developer docs

You have a local copy of the official SharePoint developer docs (github.com/SharePoint/sp-dev-docs). Answer from
these pages, not from memory. SharePoint APIs and SPFx tooling change between versions, and the docs are the
source of truth.

All paths below are relative to this skill's folder (the folder containing this SKILL.md).

`references/SOURCE` records the sp-dev-docs commit and date this copy was taken from. Read it when the user asks
how current the docs are, or when a question is about something released after that date: if so, say the bundled
docs may predate it.

## Areas

| Area | What's in it | Index |
| --- | --- | --- |
| `spfx` | SharePoint Framework: setup, web parts, extensions, ACEs/Viva Connections, library components, Teams/Office hosting, Heft/gulp toolchain, `release-*.md` notes per version | `references/index/spfx.md` |
| `declarative-customization` | List/column/view formatting JSON, list forms, site designs and site scripts, site theming | `references/index/declarative-customization.md` |
| `design` | UX guidance for web parts: layout, theming, accessibility, titles, empty states | `references/index/design.md` |
| `general-development` | REST/CSOM/JSOM APIs, search, webhooks, auth, workflows, BCS, on-premises dev | `references/index/general-development.md` |
| `solution-guidance` | PnP patterns: provisioning, branding, security, performance, add-in → modern patterns | `references/index/solution-guidance.md` |
| `scenario-guidance` | High-level scenario overviews (ALM, branding, ECM, development models) | `references/index/scenario-guidance.md` |
| `features` | Hub sites, site footer, groupify, embedding pages in Teams | `references/index/features.md` |
| `business-apps` | Power Apps and Power Automate with SharePoint | `references/index/business-apps.md` |
| `schema` | CAML / XML schema reference (Field, ContentType, Feature, Module, View, Query elements) — 1,500 pages, grep only | `references/index/schema.md` |

Not bundled: SharePoint Add-ins, the API reference (`apis`), SharePoint Embedded, training, community, transform.
If the question is about one of those, say the bundled docs don't cover it.

## How to look something up

1. **Search the indexes first.** Each index line is `- <path> — <title> — <description> — updated <date>`. Use Grep with a few
   keywords (case-insensitive) across `references/index/`, or on just the one or two areas that fit the question.
   Try synonyms if the first search misses (for example "property pane" / "web part properties",
   "ACE" / "Adaptive Card Extension").
2. **If the indexes miss, grep the pages.** Run Grep on `references/docs/<area>/` for a specific API name, CLI command,
   JSON property or error message. Use `output_mode: files_with_matches` first, then narrow down.
3. **Read only what you need.** Open the 1–3 most relevant pages (`references/<path>` from the index). For long pages,
   grep for the section heading and read just that part. Never read a whole area or a whole index file
   (except the small ones: business-apps, design, features, scenario-guidance, declarative-customization).
4. **Follow includes and links when they matter.** `[!INCLUDE ...](../../includes/...)` and relative `.md` links
   resolve against the page's own folder within `references/`.
5. **Answer.** Cite the page(s) you used by path with the `updated` date from the index, and quote commands or
   code samples exactly as the docs give them.

## Freshness

The `updated` date in each index row is the page's last upstream commit. Ignore `ms.date` in page frontmatter:
it's often years older than the real last edit. For time-sensitive topics (versions, tooling, setup, deprecations,
retirements), if a page you rely on hasn't been updated in two years or more, say so and suggest checking the
live page. Newer pages win when two pages disagree.

## Code samples

`references/samples/` indexes the PnP community samples, one line per sample: title — type · framework · SPFx
version · updated · PnP controls — description — GitHub URL. There's one file per repo: `webparts.md`,
`extensions.md` (application customizers, field customizers, command sets, form customizers) and `aces.md`
(Adaptive Card Extensions).

- Search them only when an example would help: the user asks for a sample, a starting point, or "how do I build
  X". Don't search them for conceptual or API questions the docs answer.
- Grep with a few keywords (component type, feature, library). Offer the best 1–3 matches with their URLs.
- Only the index is bundled, not the code. Link to the sample, and don't describe its implementation beyond
  the index line unless you fetch it.
- Mention each sample's SPFx version. If it's several minor versions behind the user's project, warn that it may
  need upgrading before it builds.

## SPFx version awareness

- Check which SPFx version the user is on. The plugin's session-start hook usually puts it in context already
  ("SPFx project detected: … uses SPFx x.y.z (Heft|gulp toolchain)"); use that. Otherwise read
  `@microsoft/sp-core-library` in their `package.json`, and ask only if there's no project to read.
- SPFx v1.22.0 and later use the **Heft** toolchain; v1.21.1 and earlier use **gulp**. Many pages have commands for
  both, so give the ones that match the user's version.
- For "what's new" or upgrade questions, read the matching `references/docs/spfx/release-<version>.md`.
  List them with Glob `references/docs/spfx/release-*.md` to find the newest.
- Supported Node.js and TypeScript versions per release are in `references/docs/spfx/compatibility.md`.

## Rules

- Prefer the docs over your own knowledge. If they conflict, follow the docs and point out the difference.
- If the docs don't answer the question, say so plainly, then give your best general guidance and label it that way.
- Don't paste whole pages. Summarize, and include the specific steps or snippets that matter.
