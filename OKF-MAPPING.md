---
type: Mapping Doc
title: llm-wiki → OKF v0.2 mapping (B3Wiki exercise)
description: Decision record of the B3Wiki conversion, the seed for native OKF support in SaussuNet.
generated:
  by: human:cedric
  at: '2026-11-18T00:00:00Z'
---

# llm-wiki → OKF v0.2

Exercise: convert B3Wiki (llm-wiki house style) to OKF v0.2 with
`scripts/to_okf.py`, validated by `scripts/okflint.py` (spec §9 conformance
+ v0.2 trust-layer shape). Result: 161 files, 0 errors, 0 warnings.

## Frontmatter mapping

| llm-wiki | OKF v0.2 | Rule |
|---|---|---|
| `type: entity` + folder | `type: Player\|Person\|Instrument\|Manufacturer\|Label\|Band\|Album\|Reference\|Concept\|Comparison\|Query\|Newsletter\|Source` | type derived from directory — OKF wants descriptive types |
| `title` | `title` | kept |
| (index.md entry / first sentence) | `description` | one-line summary, §4.1 recommended |
| `updated` | `timestamp` | `YYYY-MM-DD` → `YYYY-MM-DDT00:00:00Z` |
| `created` | `generated.at` (+ kept as extension key) | actor `process:b3wiki-agent` |
| `sources: [raw/…, url]` | `sources: [{resource, id, last_modified}]` | raw paths → bundle path + `last_modified` from `ingested`; ids unique per page |
| `tags`, `confidence`, `contested`, `contradictions`, `born/died/released/founded` | kept verbatim | §9: consumers must preserve unknown keys |
| raw/: `source_url`, `ingested`, `sha256` | `resource`, `timestamp`, kept `sha256` | raw pages become `type: Source` concepts |

**Honesty rule:** `verified`, `status`, `stale_after` are NOT emitted — no
evidence to back them. Trust fields are claims; never fabricate them.

## Body mapping

- `[[slug|text]]` → `[text](/bundle/rel/path.md)`; bare `[[slug]]` uses the
  target's title as link text. Unresolvable → `[slug](/slug.md)` (broken
  links are a feature, §5.3).
- `^[raw/articles/x.md]` provenance markers → numbered `[n]` + trailing
  `# Citations` section (§8), numbered by first appearance, deduplicated.
  Pages without markers get Citations generated from their raw `sources`.
- `description` for entity pages is taken from the root `index.md` entry
  (the wiki already curated one-liners); fallback = first sentence.

## File-level mapping

- `_index.md` → `index.md` (no frontmatter); root `index.md` gains
  `okf_version: "0.2"` (only place frontmatter is allowed in an index).
- `log.md`: `## [date] action | subject` → entries grouped under
  `## YYYY-MM-DD` headings (§7).
- `SCHEMA.md`/`AGENTS.md`/`README.md` gain `type: Schema|Agent Guide|Readme`
  so the tree is conformant (every non-reserved .md needs frontmatter+type).

## Lessons for SaussuNet (native OKF)

1. Conformance is cheap: frontmatter + non-empty `type` — the writer's
   validator already does harder checks; adding OKF mode is mostly a
   frontmatter serializer + link-style switch.
2. The llm-wiki `sources` + `^[…]` provenance model maps 1:1 onto OKF v0.2
   `sources[]` + `# Citations` — keep generating both.
3. Real-world frontmatter is dirty (`title: "Brother" Jack McDuff`): parse
   lenient, serialize strict.
4. `description` should become a first-class pipeline output (the LLM writes
   it), not something consumers have to derive.
5. `generated.by` per producer (`process:saussunet/<version>`) is the natural
   provenance stamp for the writer.

## Known follow-ups

- `SCHEMA.md`/`AGENTS.md` prose still describes llm-wiki conventions (wikilinks,
  `_index.md`); rewrite if this branch ever lands.
- `scripts/lint.py` (llm-wiki linter) is stale post-conversion; `okflint.py`
  replaces it.
- Dangling source `raw/forums/organissimo-bft66-hammond-b3.md` (referenced by
  a query page, never ingested) and 2 external site-relative links — tolerated
  by §5.3.
