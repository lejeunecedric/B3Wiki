# B3Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`

## [2026-10-20] create | Wiki initialized
- Domain: the Hammond organ (history, technology, people, Leslie ecosystem, modern emulations)
- Structure created: SCHEMA.md, index.md, log.md, raw/articles/, entities/, concepts/, comparisons/, queries/

## [2026-10-20] ingest | Wikipedia: Hammond organ
- raw/articles/wikipedia-hammond-organ.md (sha256 6f07d336b8e0…)
- Files created: entities/laurens-hammond.md, entities/hammond-organ-company.md, entities/hammond-b3.md, entities/jimmy-smith.md, concepts/tonewheel-generator.md, concepts/drawbars.md, concepts/harmonic-percussion.md, concepts/vibrato-chorus.md

## [2026-10-20] ingest | Wikipedia: Leslie speaker
- raw/articles/wikipedia-leslie-speaker.md (sha256 0c0b4be20ea4…)
- Files created: entities/donald-leslie.md, entities/leslie-speaker.md

## [2026-10-20] restructure | Entity subfolders
- entities/ split into instruments/ (hammond-b3, leslie-speaker), players/ (jimmy-smith), manufacturers/ (hammond-organ-company), people/ (laurens-hammond, donald-leslie)
- SCHEMA.md updated with the subfolder convention; index.md regrouped by kind
- Wikilinks use bare slugs, so no cross-page link changes needed

## [2026-10-20] ingest | Hammond Organ Co.: The Hammond Story
- raw/articles/hammondorganco-hammond-story.md (sha256 22e6f1c73177…)
- Updated: entities/laurens-hammond.md, entities/donald-leslie.md (vendor-source corroborations, Jesse Crawford / First Church of Deliverance notes)

## [2026-10-20] ingest | Wikipedia: Clonewheel organ
- raw/articles/wikipedia-clonewheel-organ.md (sha256 eba6d772...)
- Files created: concepts/clonewheel-organ.md, entities/instruments/korg-cx-3.md, entities/instruments/roland-vk-7.md, entities/instruments/hammond-xk-3.md, entities/instruments/nord-c2d.md, entities/manufacturers/korg.md, entities/manufacturers/roland-corporation.md, entities/manufacturers/clavia.md, entities/manufacturers/suzuki-musical-instrument.md
- Files updated: entities/hammond-organ-company.md (-> suzuki-musical-instrument cross-link was implicit, no body change required this run)

## [2026-10-20] ingest | Wikipedia: Jimmy Smith (musician)
- raw/articles/wikipedia-jimmy-smith.md (sha256 ad95f5e9...)
- Files updated: entities/players/jimmy-smith.md (birth date corrected from 1925 to 1928, full career timeline + influence lineage added)
- Files created: entities/players/wild-bill-davis.md (2+ source threshold met: jimmy-smith wiki + hammondorganco-hammond-story)

## [2026-10-20] lint | 0 broken wikilinks, 1 pass
- Verified all new [[wikilinks]] point to existing pages.
- All new pages have >= 2 outbound [[wikilinks]] except wildcard check below.
- Total pages: 11 -> 20.


## [2026-10-20] lint | orphan + index-completeness fix
- comparisons/b3-vs-a100 and comparisons/b3-vs-c3 had been added previously with no inbound links and no index entry (both flagged as orphans).
- Added ## Comparisons section to index.md with one-line summaries.
- Appended inbound [[wikilinks]] from entities/instruments/hammond-b3.md.
- Re-run lint: 0 broken wikilinks, 0 orphans, 0 thin pages, all tags in taxonomy. Page count: 22.
