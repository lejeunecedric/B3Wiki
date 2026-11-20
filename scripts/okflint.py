#!/usr/bin/env python3
"""okflint.py — OKF v0.3 conformance checker (spec §11 + §3.2/§5/§8/§9).

Rules (errors — §11.1 bundle conformance):
  E1  a frontmatter block that exists must parse as a YAML mapping
  E2  reserved files: index.md/log.md shape (root index frontmatter keys,
      log date headings `## YYYY-MM-DD`, newest-first order)
  E5  generated must be a mapping with `by`; verified[] entries need `by`+`at`
  E6  sources[] entries are mappings with a non-empty `resource` (§5.1)

Rules (warnings):
  W1  actors: human:/team:/process:<id> or <producer>/<version> (§7)
  W2  timestamp keys (generated.at, verified[].at, stale_after,
      sources[].last_modified) must be RFC 3339: date-only or date-time
      with offset (§5); a date-time without offset is invalid
  W4  .md without frontmatter or without `type`: not a concept (§3.2),
      validators warn, conformance unaffected (§11.1)
  W5  legacy v0.1 forms present: `# Citations` body section or `timestamp`
      frontmatter key (Appendix B fallbacks, superseded)
  W6  sources[].resource bare path that does not resolve from the file's
      directory (§6.2 v0.3 breaking change)
  W7  body footnote [^label] with no matching sources[].id (§5.1);
      duplicate sources[].id

Info: broken bundle-relative links are counted, never failed (§6.1: broken
links are a feature).

Exit code: 1 if any error, else 0.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

import yaml

RESERVED = {"index.md", "log.md"}
SKIP_DIRS = {".git", "scripts", "assets", "__pycache__", "node_modules"}
ROOT_INDEX_KEYS = {"okf_version", "title", "description", "license"}

RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}"
    r"([Tt]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|z|[+-]\d{2}:\d{2})$)?$"
)
ACTOR = re.compile(r"^(human|team|process):[^\s]+$|^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")
LOG_HEADING = re.compile(r"^## (\S.*)$")
DATE_OK = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MD_LINK = re.compile(r"\]\((/?[^\)\s]+)\)")
FN_REF = re.compile(r"\[\^([^\]\s]+)\](?!\s*:)")
CITATIONS_HEADING = re.compile(r"^# Citations\s*$", re.M)
URI_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def split_frontmatter(md: str):
    """Same contract as SaussuNet frontmatter::split — unterminated block
    returns ("", whole)."""
    if not (md.startswith("---\n") or md.startswith("---\r\n")):
        return None, md
    open_end = md.find("\n") + 1
    p = open_end
    while p <= len(md):
        line_end = md.find("\n", p)
        line_end = len(md) if line_end == -1 else line_end + 1
        if md[p : line_end].strip() == "---":
            return md[open_end:p], md[line_end:]
        p = line_end
    return None, md


def _ts(value, field, rel, warnings):
    if value is None:
        return
    if not isinstance(value, str) or not RFC3339.match(value):
        warnings.append(f"W2 {rel}: {field} must be RFC 3339 (date or date-time+offset), got {value!r}")


def check_bundle(root: str):
    errors, warnings, infos = [], [], []
    link_targets = set()
    all_md = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn.endswith(".md"):
                all_md.append(os.path.join(dirpath, fn))

    for path in sorted(all_md):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        base = os.path.basename(path)
        raw = open(path, encoding="utf-8").read()
        fm_text, body = split_frontmatter(raw)

        if base in RESERVED:
            if fm_text is not None:
                if rel != "index.md":
                    errors.append(f"E2 {rel}: index/log.md must carry no frontmatter")
                else:
                    try:
                        fm = yaml.safe_load(fm_text) or {}
                        extra = [k for k in fm if k not in ROOT_INDEX_KEYS]
                        if extra:
                            warnings.append(
                                f"W0 {rel}: root index keys beyond §8.1 set (extension keys allowed): {extra}"
                            )
                        if "okf_version" in fm and str(fm["okf_version"]) not in ("0.1", "0.2", "0.3"):
                            warnings.append(f"W0 {rel}: unknown okf_version {fm['okf_version']!r}")
                    except yaml.YAMLError as e:
                        errors.append(f"E1 {rel}: unparseable frontmatter: {e}")
            if base == "log.md":
                dates = []
                for line in body.splitlines():
                    m = LOG_HEADING.match(line)
                    if not m:
                        continue
                    d = m.group(1).strip()
                    if not DATE_OK.match(d):
                        errors.append(f"E2 {rel}: log date heading must be '## YYYY-MM-DD', got '## {d}'")
                    else:
                        dates.append(d)
                if dates != sorted(dates, reverse=True):
                    warnings.append(f"W0 {rel}: log date groups must be newest-first (§9)")
            continue

        if fm_text is None:
            warnings.append(f"W4 {rel}: no frontmatter — not a concept (§3.2)")
            continue
        try:
            fm = yaml.safe_load(fm_text) or {}
            if not isinstance(fm, dict):
                errors.append(f"E1 {rel}: frontmatter is not a mapping")
                fm = {}
        except yaml.YAMLError as e:
            errors.append(f"E1 {rel}: unparseable frontmatter: {e}")
            fm = {}
        if not str(fm.get("type", "")).strip():
            warnings.append(f"W4 {rel}: no non-empty 'type' — not a concept (§3.2)")

        # trust layer shape (§5)
        gen = fm.get("generated")
        if gen is not None:
            if not isinstance(gen, dict) or not gen.get("by"):
                errors.append(f"E5 {rel}: generated must be a mapping with 'by'")
            else:
                if not ACTOR.match(str(gen["by"])):
                    warnings.append(f"W1 {rel}: generated.by actor shape: {gen['by']}")
                _ts(gen.get("at"), "generated.at", rel, warnings)
        verified = fm.get("verified")
        if isinstance(verified, dict):  # §5.2: bare mapping = one-item list
            verified = [verified]
        for v in verified or []:
            if not isinstance(v, dict) or not v.get("by") or not v.get("at"):
                errors.append(f"E5 {rel}: verified[] entries need 'by' and 'at'")
            else:
                if not ACTOR.match(str(v["by"])):
                    warnings.append(f"W1 {rel}: verified.by actor shape: {v['by']}")
                _ts(v.get("at"), "verified[].at", rel, warnings)
        src_ids = set()
        for s in fm.get("sources") or []:
            if not isinstance(s, dict) or not str(s.get("resource", "")).strip():
                errors.append(f"E6 {rel}: sources[] entries need a resource")
                continue
            _ts(s.get("last_modified"), "sources[].last_modified", rel, warnings)
            sid = s.get("id")
            if sid:
                if sid in src_ids:
                    warnings.append(f"W7 {rel}: duplicate sources[].id {sid!r}")
                src_ids.add(sid)
            res = str(s["resource"])
            if not res.startswith("/") and not URI_SCHEME.match(res):
                # §6.2: bare path resolves from the file's own directory
                here = os.path.normpath(os.path.join(os.path.dirname(path), res))
                if not os.path.exists(here):
                    warnings.append(f"W6 {rel}: sources[].resource {res!r} does not resolve from its directory (§6.2)")
        if fm.get("stale_after") is not None:
            _ts(fm["stale_after"], "stale_after", rel, warnings)
        if "timestamp" in fm:
            warnings.append(f"W5 {rel}: legacy v0.1 `timestamp` key (use generated.at)")
        if CITATIONS_HEADING.search(body):
            warnings.append(f"W5 {rel}: legacy v0.1 `# Citations` body section (use [^id] footnotes)")

        # §5.1: footnotes must join to a sources[].id (ignore inline code
        # spans — docs describe the syntax literally)
        body_text = re.sub(r"`[^`\n]*`", "", body)
        for label in set(FN_REF.findall(body_text)):
            if label not in src_ids:
                warnings.append(f"W7 {rel}: footnote [^{label}] has no matching sources[].id")

        # collect link targets for the broken-link info count
        for m in MD_LINK.finditer(body):
            t = m.group(1)
            if t.startswith("/"):
                link_targets.add(t)
        if fm.get("resource") and str(fm["resource"]).startswith("/") and \
                not os.path.exists(os.path.join(root, str(fm["resource"]).lstrip("/"))):
            link_targets.add(str(fm["resource"]))

    broken = sorted(t for t in link_targets if not os.path.exists(os.path.join(root, t.lstrip("/"))))
    if broken:
        infos.append(f"INFO {len(broken)} broken bundle-relative links (allowed by §6.1)")
    return errors, warnings, infos, broken


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=".")
    args = ap.parse_args()
    errors, warnings, infos, broken = check_bundle(args.root)
    for e in errors:
        print(f"ERROR {e}")
    for w in warnings:
        print(f"WARN  {w}")
    for i in infos:
        print(i)
    print(
        f"\n{len(errors)} error(s), {len(warnings)} warning(s), "
        f"{len(broken)} broken link(s) tolerated."
    )
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
