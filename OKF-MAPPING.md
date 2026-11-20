---
type: Mapping Doc
title: llm-wiki → OKF v0.3 mapping (B3Wiki exercise)
description: Decision record of the B3Wiki conversion, the seed for native OKF support in SaussuNet.
generated:
  by: human:cedric
  at: '2026-11-20T00:00:00Z'
---

# llm-wiki → OKF v0.3

Exercise: convert B3Wiki (llm-wiki house style) to OKF with
`scripts/to_okf.py`, validated by `scripts/okflint.py` (spec §11 conformance
+ trust-layer shape). Converted to v0.2 on 2026-11-18 (161 files, 0 errors);
re-passed to **v0.3** on 2026-11-20 (169 files, 0 errors, 0 warnings).

## What v0.3 changed here (§13)

- **Per-claim attribution (§5.1)**: `^[raw/x.md]` markers now become
  `[^id]` Markdown footnotes keyed to `sources[].id`, with definitions
  appended at the end. The v0.2 output's numbered `[n]` + `# Citations`
  body section was the v0.1 form (§13.1/B.1) — dropped.
- **Legacy `timestamp` key dropped**: v0.3 §5.2 gives `generated.at` one
  meaning — last meaningful change — so `updated` → `generated.at`
  (was: `updated` → `timestamp`, `created` → `generated.at`). `created`
  and `updated` remain as extension keys.
- **Path resolution (§6.2, breaking)**: all emitted links and path fields
  already used a leading `/` (bundle root), so nothing to migrate; the
  linter now warns on bare `sources[].resource` paths that do not resolve
  from their file's directory.
- **Conformance relaxed (§11.1/§3.2)**: a `.md` without frontmatter or
  `type` is no longer an error — it is simply not a concept. okflint
  demotes this to warning W4. `OKF-MAPPING.md` itself now stays an
  unconverted doc (§3.2 explicitly allows it).
- **Timestamps (§5)**: date-only values are valid again (start of day,
  UTC); a date-time without offset stays invalid. The converter still
  emits full `…T00:00:00Z`.
- **Root `index.md` (§8.1)**: now carries `title`, `description` and
  `license: CC-BY-SA-4.0` alongside `okf_version: "0.3"`.
- **Actors (§7)**: `team:` scheme accepted by the linter.
- **Log order (§9)**: newest-first date groups are now linted (was already
  the converter's behavior).

## Frontmatter mapping

| llm-wiki | OKF v0.3 | Rule |
|---|---|---|
| `type: entity` + folder | `type: Player\|Person\|Instrument\|Manufacturer\|Label\|Band\|Album\|Reference\|Concept\|Comparison\|Query\|Newsletter\|Source` | type derived from directory — OKF wants descriptive types |
| `title` | `title` | kept |
| (index.md entry / first sentence) | `description` | one-line summary, §4.1 recommended |
| `updated` | `generated.at` (+ kept as extension key) | last meaningful change (§5.2); actor `process:b3wiki-agent` |
| `created` | kept as extension key | no longer mapped to `generated.at` |
| `sources: [raw/…, url]` | `sources: [{resource, id, last_modified}]` | raw paths → bundle path + `last_modified` from `ingested`; ids unique per page |
| `tags`, `confidence`, `contested`, `contradictions`, `born/died/released/founded` | kept verbatim | §4.1: consumers must preserve unknown keys |
| raw/: `source_url`, `ingested`, `sha256` | `resource`, `generated.at` from `ingested`, kept `sha256` | raw pages become `type: Source` concepts |

**Honesty rule:** `verified`, `status`, `stale_after` are NOT emitted — no
evidence to back them. Trust fields are claims; never fabricate them.

## Body mapping

- `[[slug|text]]` → `[text](/bundle/rel/path.md)`; bare `[[slug]]` uses the
  target's title as link text. Unresolvable → `[slug](/slug.md)` (broken
  links are a feature, §6.1).
- `^[raw/articles/x.md]` provenance markers → `[^id]` footnotes keyed to
  the matching `sources[].id` (§5.1), definitions appended at the end in
  first-appearance order, deduplicated. Pages without markers record
  provenance in `sources[]` only — no forced body citations.
- `description` for entity pages is taken from the root `index.md` entry
  (the wiki already curated one-liners); fallback = first sentence.

## File-level mapping

- `_index.md` → `index.md` (no frontmatter); root `index.md` gains
  `okf_version: "0.3"` + bundle metadata (§8.1) — the only place
  frontmatter is allowed in an index.
- `log.md`: `## [date] action | subject` → entries grouped under
  `## YYYY-MM-DD` headings, newest first (§9).
- `SCHEMA.md`/`AGENTS.md`/`README.md`/`OKF-MAPPING.md` are curated docs:
  once they carry a `type`, the converter leaves them untouched (§4:
  do not re-serialize unchanged values).

## Lessons for SaussuNet (native OKF)

1. Conformance is cheap under v0.3: parseable frontmatter is the only hard
   requirement; `type` is required only for something to *be* a concept.
   Adding OKF mode is mostly a frontmatter serializer + link-style switch.
2. The llm-wiki `sources` + `^[…]` provenance model maps 1:1 onto OKF
   `sources[]` + `[^id]` footnotes — generate footnotes keyed by id, never
   positional numbering (agents rewrite bodies; positions rot silently).
3. Real-world frontmatter is dirty (`title: "Brother" Jack McDuff`): parse
   lenient, serialize strict.
4. `description` should become a first-class pipeline output (the LLM writes
   it), not something consumers have to derive.
5. `generated.by` per producer (`process:saussunet/<version>`) is the natural
   provenance stamp for the writer.
6. Emit bundle-root paths (`/…`) in links and path fields: v0.3 §6.2 resolves
   bare paths from the *file's* directory — the one v0.2→v0.3 breaking change
   that can silently mis-resolve.

## Known follow-ups

- `SCHEMA.md`/`AGENTS.md` prose still describes llm-wiki conventions (wikilinks,
  `_index.md`); rewrite if this branch ever lands.
- `scripts/lint.py` (llm-wiki linter) is stale post-conversion; `okflint.py`
  replaces it.
- Dangling source `raw/forums/organissimo-bft66-hammond-b3.md` (referenced by
  a query page, never ingested) and 2 external site-relative links — tolerated
  by §6.1.
