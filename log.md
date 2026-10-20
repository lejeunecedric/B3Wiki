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
- Total pages: 11 -> 19.


## [2026-10-20] lint | orphan + index-completeness fix
- comparisons/b3-vs-a100 and comparisons/b3-vs-c3 had been added previously with no inbound links and no index entry (both flagged as orphans).
- Added ## Comparisons section to index.md with one-line summaries.
- Appended inbound [[wikilinks]] from entities/instruments/hammond-b3.md.
- Re-run lint: 0 broken wikilinks, 0 orphans, 0 thin pages, all tags in taxonomy. Page count: 22.

## [2026-10-20] create | Comparison pages: Hammond models and rivals
- comparisons/b3-vs-c3.md — same generator, different cabinet; covers B-2/C-2 and RT-3 lineage
- comparisons/b3-vs-a100.md — self-contained B-3 with internal amp/speakers
- comparisons/b3-vs-combo-organs.md — B-3 vs Vox Continental & Farfisa Compact/FAST (web research: Wikipedia Vox Continental, Farfisa)
- comparisons/b3-vs-clonewheels.md — B-3 vs Korg CX-3 (1979/2001), Roland VK-7, Nord C series, Hammond-Suzuki XK-3/New B-3 (web research: Wikipedia Korg CX-3, Nord C Series)
- index.md: added the two missing comparison entries; page count 22 -> 24

## [2026-10-20] create | 5 entity pages + 1 query page
- Files created: entities/players/jimmy-mcgriff.md, entities/players/dr-lonnie-smith.md, entities/players/jon-lord.md, entities/players/brian-auger.md, entities/labels/hammondbeat.md (new labels/ subfolder), queries/b3-beyond-jimmy-smith.md
- Sources used: wikipedia-jimmy-mcgriff, wikipedia-dr-lonnie-smith, wikipedia-jon-lord, wikipedia-brian-auger, wikipedia-hammondbeat; query page synthesizes NPR Blog Supreme, vinyldiscovery, organissimo BFT-66 with provenance markers
- index.md updated (Players, new Labels section, Queries)

## [2026-10-20] ingest | Doctor Mix + 4 Wikipedia player articles
- raw/articles/doctormix-rarest-hammond.md (sha256 a3e7e265...) — Brian Auger's stealth C3, Keyboard Specialties, Lombardi, 50/60 Hz
- raw/articles/wikipedia-john-medeski.md, wikipedia-joey-defrancesco.md, wikipedia-barbara-dennerlein.md, wikipedia-booker-t-jones.md

## [2026-10-20] create | 6 pages: portables concept, Lombardi, 4 modern players
- concepts/portable-hammonds.md — factory portables (Hammond Portable B-3mk2, 2019 Porta-B, per NAMM 2019 demos/b3guys) vs chops (Keyboard Specialties stealth organ, Bertram music Germany [confidence: low, classified-listing evidence only], Oakland Chop tradition); the 50/60 Hz cycle problem; ~425 lb weight
- entities/people/renato-lombardi.md — Italian engineer: resistor fix (~¼ output level), free PA stacks ("I already sold this three times"), built Auger's amp, fitted replacement power unit after the 220V socket accident
- entities/players/john-medeski.md, joey-defrancesco.md (incl. acquisition of Jon Lord's modified Hammond per Wikipedia Hammond organ article citing Vail 2002), barbara-dennerlein.md, booker-t-jones.md
- Updated: entities/players/brian-auger.md (new "The Italian sound" section), queries/b3-beyond-jimmy-smith.md (open threads: wild-bill-davis and joey-defrancesco now exist; Jack McDuff still pending), index.md (Players/People/Concepts sections)
- Total pages: 30 -> 36

## [2026-10-20] lint | wikilink + index check

## [2026-10-20] create | Landmark Hammond albums query
- queries/hammond-landmark-albums.md — Deep Purple (Lord: In Rock/Fireball/Machine Head/Burn, Marshall-driven C-3), ELP (Emerson: debut/Tarkus/Trilogy/Brain Salad Surgery, L-100 + Moog), Mother Earth (disambiguated: US Tracy Nelson band, organist Mark Naftalin, confidence low-medium; British band = 1990s acid jazz, Bryn Barklam), Santana (Rolie: 1969/Abraxas/III).
- Raw ingested: 10 files in raw/articles/ (9 wikipedia-*, rockasteria-mother-earth-living-with-animals) with source_url/ingested/sha256 frontmatter.
- entities/players/jon-lord.md: added Discography highlights line linking the query.
- index.md: Queries entry added; page count fixed to actual (38 .md pages).
- Lint: 0 broken wikilinks; query page has 3+ inbound links. Pre-existing orphans (booker-t-jones, barbara-dennerlein, b3-vs-combo-organs) left for the in-flight agent owning them.
- Re-run lint: 0 broken wikilinks, 0 orphans, 0 pages missing from index, all tags in taxonomy.
- One pre-existing false positive noted: path-style [[comparisons/...|alias]] links in hammond-b3.md resolve correctly.
- Page count verified by find: 37 (index updated 36 -> 37).

## [2026-10-20] ingest | Eddy Louiss (Wikipedia FR + EN) + revival-scene sources
- raw/articles/wikipedia-eddy-louiss.md (sha256 f5e2e06dbd5c…; fr-Wiki main, en-Wiki stub confirms)
- raw/articles/wikipedia-james-taylor-quartet.md (9b65cd5a9723…)
- raw/articles/linkquartet-lastfm-apollonegri.md (d74395a7629e…; Last.fm wiki + apollonegri.com + IAJO)
- raw/articles/men-from-spectre-allmusic-discogs.md (40bc5baf6f7c…)
- raw/articles/leslie-overdrive-blog-allmusic.md (7c2714aa028d…)

## [2026-10-20] create | Eddie→Eddy Louiss + Hammondbeat/acid-jazz revival wave
- entities/players/eddy-louiss.md (note: the correct spelling is "Eddy", b. 1941 not 1943 per both Wikipedias; task brief's "1943–2015" and Eddy Mitchell claim were wrong — he is famous for 13 years with Claude Nougaro; "Eddie Louiss Project"/"Organ Explosion" albums not found in either Wikipedia discography)
- entities/bands/ (new subfolder, added to SCHEMA.md): james-taylor-quartet.md, link-quartet.md, men-from-spectre.md (contradicted country: DE vs CH, flagged), leslie-overdrive.md
- entities/players/paolo-negri.md
- Files updated: entities/labels/hammondbeat.md (Roster section + wikilinks, sources bumped), queries/b3-beyond-jimmy-smith.md (channel 3 expanded; acid-jazz wave covered; Jack McDuff still pending), index.md (Bands subsection, 2 new Players, count 37→47)
- Not given pages (weak single-source): Phat Fred, Sven Hammond Soul, The Special Agents, Low Fidelity Jet-Set Orchestra, The Dansettes etc. — listed roster-only on the label page
- Lint: 0 broken wikilinks, 0 orphans (meta-file "[[wikilinks]]" literals in log/SCHEMA/README are false positives). Page count 37→47 (wiki .md excl raw).

## [2026-10-20] ingest | modern organ scene sources (5)
- raw/articles/wikipedia-delvon-lamarr-organ-trio.md (sha256 8d50b28a3b9c…)
- raw/articles/wikipedia-cookin-on-3-burners.md (sha256 e61253dd7b18…)
- raw/articles/flophouse-the-pulitzers-honk-honk.md (sha256 63aa33545207…)
- raw/articles/bandcampdaily-parlor-greens-emeralds.md (sha256 5641a7739b59…)
- raw/articles/sfjazz-cory-henry-funk-apostles.md (sha256 c3c1b6830ad7…)

## [2026-10-20] create | The modern organ scene (7 pages)
- entities/bands/delvon-lamarr-organ-trio.md, entities/players/delvon-lamarr.md
- entities/bands/parlor-greens.md, entities/players/jimmy-james.md — user's "Jimmy James new trio" confirmed: Parlor Greens (Colemine, 2025, Emeralds)
- entities/bands/the-pulitzers.md — VERIFIED but corrected: Dutch (not French) Hammond funk quartet, Frank Montis, Honk Honk (Zip Records, 2023)
- entities/players/cory-henry.md (Cory Henry & The Funk Apostles, Divine Time 2025)
- entities/bands/cookin-on-3-burners.md ("This Girl"/Kungs; Cookin' the Books 2025)
- queries/modern-organ-scene.md — synthesis: labels (Colemine/Karma Chief, Zip, Soul Messin'), streaming/KEXP discovery, 60s-trio differences
- index.md: 7 new entries; page count 47 -> 54
