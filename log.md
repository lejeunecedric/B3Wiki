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
