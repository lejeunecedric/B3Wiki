# B3Wiki Schema

## Domain
A knowledge base about the **Hammond organ** — its history, technology (tonewheels, drawbars, vibrato/chorus, percussion), the Leslie speaker ecosystem, key players (Laurens Hammond, Donald Leslie), iconic artists (Jimmy Smith and the jazz organ tradition), and the modern clonewheel era. English-language wiki.

**Purpose:** first-hand compiled knowledge over vendor docs; one page = one clear lesson or entity. Sources are ingested verbatim into `raw/` and synthesized here.

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `tonewheel-generator.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`
- **Provenance markers:** on pages synthesizing 3+ sources, append `^[raw/articles/source-file.md]` to paragraphs whose claims trace to a specific source. Optional on single-source pages.

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
confidence: high | medium | low   # optional
contested: true                    # optional, unresolved contradictions
---
```

### raw/ Frontmatter
```yaml
---
source_url: https://example.com/article
ingested: YYYY-MM-DD
sha256: <hex digest of the body below the frontmatter>
---
```

## Tag Taxonomy
- `company` — Hammond Organ Company, Suzuki, CBS, Electro Music
- `person` — inventors, engineers, musicians
- `instrument` — specific organ models (B-3, Model A, A-100, ...)
- `gear` — speakers and accessories (Leslie cabinets, tone cabinets)
- `technology` — tonewheel, drawbars, vibrato/chorus, percussion, synthesis
- `history` — dates, timelines, market/industry events
- `music` — genres, playing styles, notable recordings
- `modern` — clonewheels, digital emulations, current products
- `label` — record labels dedicated to organ music
- `comparison` — side-by-side analyses
- `query` — filed query results
- `source` — note about an ingested source

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions
- **Split a page** when it exceeds ~200 lines
- **Archive** superseded pages to `_archive/` and remove from index

## Entity Pages
Entities live in `entities/` **subfolders by kind**:
- `entities/instruments/` — organs, speakers, clonewheels (Korg CX-3, Roland VK series, Nord C2D…)
- `entities/players/` — musicians
- `entities/manufacturers/` — companies (Hammond, Suzuki, Korg, Roland, Clavia…)
- `entities/bands/` — organ-led bands (JTQ, The Link Quartet…)
- `entities/labels/` — record labels dedicated to organ music (Hammondbeat, Scufflin'…)
- `entities/people/` — inventors, engineers, non-player figures

One page per notable entity (person, company, instrument model, product line). Overview, key facts/dates, relationships via `[[wikilinks]]`, sources.

## Concept Pages
One page per concept (tonewheel generator, drawbars, harmonic percussion, vibrato/chorus scanner, Doppler effect in the Leslie). Definition, how it works, why it matters, related concepts.

## Comparison Pages
Side-by-side analyses in table form (e.g., B-3 vs. clonewheel emulations), with verdict/synthesis and sources.

## Update Policy
1. Newer sources generally supersede older ones
2. Genuinely contradictory claims: note both with dates and sources
3. Mark `contradictions:` in frontmatter and flag for review
