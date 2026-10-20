# AGENTS.md — instructions for AI agents working on B3Wiki

You are picking up maintenance of **B3Wiki**, an English-language llm-wiki about the
Hammond organ and associated music. This file is the contract. Follow it.

## 0. Orientation (do this FIRST, every session)

Read, in this order:

1. `SCHEMA.md` — conventions, frontmatter format, tag taxonomy, entity subfolders
2. `index.md` — catalog of every page (page counts, sections)
3. `log.md` — last ~30 entries: what was done recently, what is pending

Rules that come from this orientation:
- **Never create a page that already exists** — extend it and bump its `updated` date.
- **Never modify files in `raw/`** — sources are immutable; corrections go in wiki pages.
- Re-ingest the same URL only after recomputing its sha256 (skip if unchanged, flag drift if changed).

## 1. Repo layout

```
SCHEMA.md      conventions & taxonomy (the law)
index.md       catalog — every page must appear here
log.md         append-only action log: ## [YYYY-MM-DD] action | subject
raw/articles/  immutable ingested web sources
raw/forums/    immutable ingested forum threads
entities/      one page per entity, in subfolders:
               instruments/ players/ manufacturers/ labels/ people/ bands/
concepts/      one page per technology/concept
comparisons/   side-by-side analyses (table + verdict)
queries/       filed syntheses (multi-source answers worth keeping)
assets/        images (credited CC sources only, see README)
```

## 2. Page rules (enforced by lint)

- Frontmatter required: `title, created, updated, type (entity|concept|comparison|query|summary), tags (from SCHEMA taxonomy), sources`. Optional: `confidence: high|medium|low`, `contested: true`.
- File names: lowercase, hyphens, no spaces.
- Minimum **2–3 outbound `[[wikilinks]]`** per page; bare slugs (`[[hammond-b3]]`), no folder prefix needed.
- **Provenance**: on any page synthesizing 2+ sources, append `^[raw/articles/file.md]` (or `raw/forums/...`) to paragraphs whose claims come from a specific source.
- Conflicting sources: keep both, date them, set `confidence: medium|low`, add `contradictions:` frontmatter.
- Every page gets an **External links** section with 2–4 weblinks (Wikipedia, official site, a representative performance/article).
- Pages stay under ~200 lines — split beyond that.
- **Cite images**: Creative Commons or public domain only, with author + license + source URL in `README.md` → Credits. No AI-generated imagery.

## 3. Ingesting a source

1. Save verbatim to `raw/articles/` (or `raw/forums/`), named descriptively.
2. Prepend frontmatter:
   ```yaml
   ---
   source_url: <url>
   ingested: YYYY-MM-DD
   sha256: <sha256 of the body below the frontmatter>
   ---
   ```
3. Create/update entity & concept pages per §2, update `index.md` (sections + page count), append to `log.md`.
4. Reddit blocks scraping (HTTP 403) — don't waste attempts. Good sources: Wikipedia, organissimo.org forum, Sound on Sound, jazzfuel.com, vinyldiscovery.blogspot.com, NPR A Blog Supreme, hammondorganco.com (Hall of Fame, product pages), Bandcamp/Discogs for the modern scene, AllMusic.

## 4. Lint (run before every commit)

Check programmatically (Python + os/re over `*.md`):
1. **Broken wikilinks** — `[[slug]]` whose slug matches no file in entities/concepts/comparisons/queries
2. **Orphans** — pages with no inbound links
3. **Index completeness** — every page appears in `index.md`, page count matches reality
4. **Tags** — every tag exists in the SCHEMA taxonomy

Fix what you find. Log the lint run (`## [date] lint | N issues`).

## 5. Git & pushing

- `main` is the only branch. Work directly on it. **NEVER force-push.**
- The wiki lives in a fresh clone just as well as on the maintainer's machine:
  ```bash
  git clone https://github.com/lejeunecedric/B3Wiki.git
  cd B3Wiki
  git config user.name "lejeunecedric"
  git config user.email "8034084+lejeunecedric@users.noreply.github.com"
  gh auth login          # or: GITHUB_TOKEN in env; then: gh auth setup-git
  ```
  (On the maintainer's host these two `git config` lines + the gh credential helper are already set repo-locally — check `git config --local -l` first.)
- Commit message style: `B3Wiki <what>: <sources/pages>` (see `git log` for examples).
- **Every working session ends with a push.** After pushing, verify:
  `gh api repos/lejeunecedric/B3Wiki/commits/main --jq '.sha[0:7]'`

## 6. Automation context

- A scheduled agent (Hermes cronjob `b3wiki-self-update`, Mondays 09:00 UTC) does: orient → ingest 1–2 sources → cross-reference → weblinks → lint → commit → push. If you are that agent, the same rules apply; your final report states sources ingested, pages created/updated, lint findings, and the push hash.
- Pending/known threads are tracked in `log.md` and in the "Open threads" section of `queries/b3-beyond-jimmy-smith.md` — check them before choosing what to work on.

## 7. House style

- English pages, factual, scannable; one page = one entity/concept/lesson.
- Fun is allowed in the README, not in entity pages.
- When sources contradict folklore (dates, spellings, "everyone knows" stories), the sources win — and the correction gets logged.
