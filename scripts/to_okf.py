#!/usr/bin/env python3
"""to_okf.py — convert B3Wiki (llm-wiki house style) to OKF v0.3 in place.

Mapping (see OKF-MAPPING.md):
  - type: derived from directory (entities/players -> Player, concepts -> Concept, ...)
  - updated -> generated.at (last meaningful change, §5.2); created kept as extra
  - legacy v0.1 `timestamp` key is NOT emitted (Appendix B fallback only)
  - sources: [paths|urls] -> v0.3 sources: [{resource, id, last_modified}] (§5.1)
  - ^[raw/...] provenance markers -> [^id] footnotes keyed to sources[].id (§5.1);
    no `# Citations` body section (v0.1 form superseded, §13.1)
  - [[wikilinks]] -> bundle-root markdown links [text](/path.md) (§6)
  - _index.md -> index.md; root index.md gains `okf_version: "0.3"` (§8.1)
  - log.md `## [date] action | subject` -> grouped `## YYYY-MM-DD`, newest first (§9)
  - raw/ files gain type: Source + resource: <source_url>
"""
from __future__ import annotations

import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okflint import split_frontmatter  # noqa: E402

SKIP_DIRS = {".git", "scripts", "assets", "tests", "__pycache__"}
OKF_VERSION = "0.3"

DIR_TYPES = {
    "entities/players": "Player",
    "entities/people": "Person",
    "entities/manufacturers": "Manufacturer",
    "entities/labels": "Label",
    "entities/bands": "Band",
    "entities/albums": "Album",
    "entities/instruments": "Instrument",
    "entities/references": "Reference",
    "concepts": "Concept",
    "comparisons": "Comparison",
    "queries": "Query",
}
META_TYPES = {"SCHEMA.md": "Schema", "AGENTS.md": "Agent Guide", "README.md": "Readme",
              "OKF-MAPPING.md": "Mapping Doc"}

WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]")
FOOTNOTE = re.compile(r"\^\[([^\]]+)\]")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$")
INDEX_DESC = re.compile(r"^- \[\[([^\]|]+)(?:\|[^\]]*)?\]\]\s*(?:—|-)\s*(.+)$", re.M)

GENERATED_BY = "process:b3wiki-agent"


def to_dt(value) -> str:
    s = str(value).strip()
    if DATE_RE.match(s):
        return s + "T00:00:00Z"
    return s  # already ISO with offset, or left as-is


def stem(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def url_slug(url: str) -> str:
    last = url.rstrip("/").rsplit("/", 1)[-1]
    s = re.sub(r"[^a-z0-9]+", "-", last.lower()).strip("-")
    return s or "url"


def uniq(base: str, used: set) -> str:
    cand, n = base, 2
    while cand in used:
        cand = f"{base}-{n}"
        n += 1
    used.add(cand)
    return cand


def first_h1(body: str) -> str:
    m = re.search(r"^# (.+)$", body, re.M)
    return m.group(1).strip() if m else ""


def first_sentence(body: str) -> str:
    for line in body.splitlines():
        l = line.strip()
        if not l or l.startswith(("#", ">", "|", "<!--")):
            continue
        m = re.match(r"^(.+?[.!?])(?:\s|$)", l)
        return (m.group(1) if m else l)[:200]
    return ""


def parse_lenient(yaml_text: str) -> dict:
    """Line-based fallback for hand-written frontmatter that is not valid
    YAML (e.g. `title: "Brother" Jack McDuff`). Values stay raw strings;
    `[a, b]` becomes a list."""
    out: dict = {}
    for line in yaml_text.splitlines():
        if not line.strip() or line.startswith(("#", " ", "\t")):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            out[key.strip()] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        else:
            out[key.strip()] = value
    return out


def read_page(root: str, rel: str):
    raw = open(os.path.join(root, rel), encoding="utf-8").read()
    fm_text, body = split_frontmatter(raw)
    if not fm_text:
        return {}, body
    try:
        return (yaml.safe_load(fm_text) or {}), body
    except yaml.YAMLError:
        return parse_lenient(fm_text), body


def build_slug_map(root: str) -> dict:
    """slug -> {"path": rel, "title": str}. Includes index.md/log.md slugs
    (wikilinks like [[../index]] resolve by last segment)."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".md") or fn == "_index.md":
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/")
            if rel in META_TYPES:
                continue
            fm, body = read_page(root, rel)
            title = str(fm.get("title") or first_h1(body) or stem(fn))
            s = stem(fn)
            if s in out:
                print(f"WARN slug collision: {s}: {out[s]['path']} vs {rel}")
                continue
            out[s] = {"path": rel, "title": title}
    return out


def build_raw_meta(root: str) -> dict:
    out = {}
    raw_root = os.path.join(root, "raw")
    if not os.path.isdir(raw_root):
        return out
    for dirpath, _, filenames in os.walk(raw_root):
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/")
            fm, _ = read_page(root, rel)
            out[rel] = fm
    return out


def rewrite_wikilinks(body: str, current_rel: str, slug_map: dict, root: str) -> str:
    by_path = {v["path"]: v["title"] for v in slug_map.values()}

    def repl(m):
        target, alias = m.group(1).strip(), m.group(2)
        path = None
        if "/" in target:
            t = target[:-3] if target.endswith(".md") else target
            base_dir = os.path.dirname(current_rel)
            cand = os.path.normpath(os.path.join(base_dir, t + ".md")).replace(os.sep, "/")
            if os.path.exists(os.path.join(root, cand)):
                path = cand
            else:
                last = t.rsplit("/", 1)[-1]
                if last in slug_map:
                    path = slug_map[last]["path"]
        elif target in slug_map:
            path = slug_map[target]["path"]
        if path is None:
            return f"[{alias or target}](/{target}.md)"  # broken link tolerated (§6.1)
        text = alias or by_path.get(path) or stem(path)
        return f"[{text}](/{path})"

    return WIKILINK.sub(repl, body)


def build_sources(fm_sources: list, markers: list, raw_meta: dict):
    """v0.3 §5.1: unified sources[] with stable ids.

    Returns (entries, id_of) where id_of maps each source string (raw path
    or URL) to its entry id, so body markers can cite [^id] footnotes.
    Frontmatter `sources` come first, then body-only markers, deduped."""
    entries, used, id_of = [], set(), {}
    seen_keys = set()
    ordered = [str(s).strip() for s in fm_sources]
    ordered += [str(m).strip() for m in markers]
    for s in ordered:
        if not s or s in seen_keys:
            continue
        seen_keys.add(s)
        if s.startswith("raw/") or s.startswith("/raw/"):
            rel = s.lstrip("/")
            entry = {"resource": "/" + rel, "id": uniq(stem(rel), used)}
            ing = (raw_meta.get(rel) or {}).get("ingested")
            if ing:
                entry["last_modified"] = to_dt(ing)
        else:
            entry = {"resource": s, "id": uniq(url_slug(s), used)}
        id_of[s] = entry["id"]
        entries.append(entry)
    return entries, id_of


def attribute_footnotes(body: str, id_of: dict, titles: dict) -> str:
    """v0.3 §5.1 per-claim attribution: `^[raw/x.md]` markers become
    [^id] footnotes keyed to sources[].id, with definitions appended at
    the end (first-appearance order). No `# Citations` section (§13.1)."""
    used: list[str] = []

    def repl(m):
        p = m.group(1)
        fid = id_of.get(p) or id_of.get(p.lstrip("/"))
        if fid is None:
            return m.group(0)  # unknown source: leave marker for the linter
        if fid not in used:
            used.append(fid)
        return f"[^{fid}]"

    new = FOOTNOTE.sub(repl, body)
    if not used:
        return new
    new = new.rstrip("\n") + "\n"
    lines = [""]
    for fid in used:
        label = next((k for k, v in id_of.items() if v == fid), fid)
        lines.append(f"[^{fid}]: {titles.get(label, fid)}")
    new += "\n".join(lines) + "\n"
    return new


RESERVED_KEYS = {"type", "title", "description", "tags", "timestamp", "sources", "generated"}


def map_page_frontmatter(fm: dict, page_type: str, desc: str, src_entries: list) -> dict:
    out: dict = {"type": page_type}
    if fm.get("title"):
        out["title"] = fm["title"]
    if desc:
        out["description"] = desc
    if fm.get("tags"):
        out["tags"] = fm["tags"]
    if src_entries:
        out["sources"] = src_entries
    # §5.2: generated.at = last meaningful change to the content
    gen_at = to_dt(fm.get("updated") or fm.get("created") or "")
    if gen_at:
        out["generated"] = {"by": GENERATED_BY, "at": gen_at}
    for k, v in fm.items():  # preserve extras (confidence, born, died, ...)
        if k not in RESERVED_KEYS and k not in out:
            out[k] = v
    return out


def map_raw_frontmatter(fm: dict, title: str) -> dict:
    out: dict = {"type": "Source"}
    if title:
        out["title"] = title
    if fm.get("source_url"):
        out["resource"] = fm["source_url"]
    if fm.get("ingested"):
        out["generated"] = {"by": GENERATED_BY, "at": to_dt(fm["ingested"])}
    for k in ("source_url", "ingested", "sha256"):
        if k in fm:
            out[k] = fm[k]
    for k, v in fm.items():
        if k not in RESERVED_KEYS and k not in out:
            out[k] = v
    return out


def map_newsletter_frontmatter(body: str, stem_name: str) -> dict:
    out: dict = {"type": "Newsletter"}
    out["title"] = first_h1(body) or stem_name
    m = re.match(r"(\d{2})(\d{2})(\d{2})-", stem_name)
    if m:
        ts = f"20{m.group(1)}-{m.group(2)}-{m.group(3)}T00:00:00Z"
        out["generated"] = {"by": GENERATED_BY, "at": ts}
    return out


def serialize(fm: dict, body: str) -> str:
    yaml_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=1000)
    out = "---\n" + yaml_text + "---\n"
    if not body.startswith("\n"):
        out += "\n"
    return out + body


def reformat_log(md: str) -> str:
    lines = md.splitlines()
    head, i = [], 0
    while i < len(lines) and not lines[i].startswith("## "):
        head.append(lines[i])
        i += 1
    head = [
        "> Format: `## YYYY-MM-DD` headings, most recent first (OKF §9)."
        if l.startswith("> Format:")
        else "> Reverse-chronological record of all wiki actions (newest first)."
        if l.startswith("> Chronological record")
        else l
        for l in head
    ]
    entries = []
    cur = None
    for line in lines[i:]:
        m = re.match(r"^## \[?(\d{4}-\d{2}-\d{2})\]?\s*(.*)$", line)
        if m:
            date, rest = m.group(1), m.group(2).strip()
            action, subject = rest.split("|", 1) if "|" in rest else ("", rest)
            cur = {"date": date, "action": action.strip(), "subject": subject.strip(), "sub": []}
            entries.append(cur)
        elif cur is not None and line.strip():
            cur["sub"].append(line.rstrip())
    groups: dict = {}
    for e in entries:
        groups.setdefault(e["date"], []).append(e)
    out = head + [""]
    for date in sorted(groups, reverse=True):  # antichronological (OKF §9)
        es = groups[date]
        out += [f"## {date}", ""]
        for e in es:
            act = e["action"].capitalize()
            out.append(f"* **{act}**: {e['subject']}" if act else f"* {e['subject']}")
            out += ["  " + s for s in e["sub"]]
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def parse_index_descriptions(body: str) -> dict:
    out = {}
    for m in INDEX_DESC.finditer(body):
        target, desc = m.group(1), m.group(2).strip()
        out[target.rsplit("/", 1)[-1][:-3] if target.endswith(".md") else target.rsplit("/", 1)[-1]] = desc
    return out


def dir_type(rel: str) -> str:
    parent = os.path.dirname(rel)
    if parent in DIR_TYPES:
        return DIR_TYPES[parent]
    return (parent.rsplit("/", 1)[-1] or "Concept").capitalize()


def convert(root: str):
    slug_map = build_slug_map(root)
    raw_meta = build_raw_meta(root)
    raw_titles = {rel: (first_h1(read_page(root, rel)[1]) or stem(rel)) for rel in raw_meta}

    root_index_body = ""
    ri = os.path.join(root, "index.md")
    if os.path.exists(ri):
        root_index_body = split_frontmatter(open(ri, encoding="utf-8").read())[1]
    index_desc = parse_index_descriptions(root_index_body)

    n = 0
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            fm, body = read_page(root, rel)

            if fn == "_index.md":
                new = rewrite_wikilinks(body, rel, slug_map, root)
                with open(os.path.join(dirpath, "index.md"), "w", encoding="utf-8") as f:
                    f.write(new)
                os.remove(path)
            elif fn == "index.md":
                new = rewrite_wikilinks(body, rel, slug_map, root)
                if rel == "index.md":
                    new = serialize({
                        "okf_version": OKF_VERSION,
                        "title": "B3Wiki",
                        "description": ("An OKF knowledge bundle about the Hammond "
                                        "organ, born as a Karpathy-style llm-wiki."),
                        "license": "CC-BY-SA-4.0",
                    }, new)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
            elif fn == "log.md":
                text = open(path, encoding="utf-8").read()
                with open(path, "w", encoding="utf-8") as f:
                    f.write(reformat_log(text))
            elif rel in META_TYPES:
                if str(fm.get("type", "")).strip():
                    pass  # curated doc frontmatter: keep verbatim (§4 "do not
                    # re-serialize unchanged values"); docs are not converted
                else:
                    fm2 = {"type": META_TYPES[rel], "title": first_h1(body) or stem(fn)}
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(serialize(fm2, body))
            elif rel.startswith("raw/"):
                fm2 = map_raw_frontmatter(fm, first_h1(body) or stem(fn))
                with open(path, "w", encoding="utf-8") as f:
                    f.write(serialize(fm2, body))
            elif rel.startswith("content/"):
                fm2 = map_newsletter_frontmatter(body, stem(fn))
                new = rewrite_wikilinks(body, rel, slug_map, root)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(serialize(fm2, new))
            else:
                markers = [m for m in FOOTNOTE.findall(body)]
                src_entries, id_of = build_sources(fm.get("sources") or [], markers, raw_meta)
                body2 = attribute_footnotes(body, id_of, raw_titles)
                body2 = rewrite_wikilinks(body2, rel, slug_map, root)
                desc = index_desc.get(stem(fn)) or first_sentence(body2)
                fm2 = map_page_frontmatter(fm, dir_type(rel), desc, src_entries)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(serialize(fm2, body2))
            n += 1
    print(f"converted {n} markdown files")


if __name__ == "__main__":
    convert(sys.argv[1] if len(sys.argv) > 1 else ".")
