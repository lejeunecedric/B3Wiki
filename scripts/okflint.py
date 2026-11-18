#!/usr/bin/env python3
"""okflint.py — OKF v0.1/v0.2 conformance checker (spec §9 + v0.2 tightenings).

Rules (errors):
  E1  every non-reserved .md has a parseable YAML frontmatter block
  E2  every frontmatter has a non-empty `type`
  E3  index.md carries no frontmatter (root index.md may, okf_version only)
  E4  log.md date headings use `## YYYY-MM-DD`

Rules (warnings — v0.2 trust layer shape):
  W1  generated/verified actors: human:<id>, process:<id> or <producer>/<version>
  W2  every timestamp-valued trust key is ISO 8601 with explicit UTC offset
  W3  sources[] entries are mappings with a non-empty `resource`

Info: broken bundle-relative links are counted, never failed (§5.3: broken
links are a feature).

Exit code: 1 if any error, else 0.
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import sys

import yaml

RESERVED = {"index.md", "log.md"}
SKIP_DIRS = {".git", "scripts", "assets", "__pycache__", "node_modules"}

ISO_OFFSET = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)
ACTOR = re.compile(r"^(human|process):[^\s]+$|^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")
LOG_HEADING = re.compile(r"^## (\S.*)$")
DATE_OK = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MD_LINK = re.compile(r"\]\((/[^)\s]+)\)")


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
                if not (rel == "index.md"):
                    errors.append(f"E3 {rel}: index/log.md must carry no frontmatter")
                else:
                    try:
                        fm = yaml.safe_load(fm_text) or {}
                        extra = [k for k in fm if k != "okf_version"]
                        if extra:
                            warnings.append(
                                f"W0 {rel}: root index frontmatter keys beyond okf_version: {extra}"
                            )
                    except yaml.YAMLError as e:
                        errors.append(f"E1 {rel}: unparseable frontmatter: {e}")
            if base == "log.md":
                for line in body.splitlines():
                    m = LOG_HEADING.match(line)
                    if m and not DATE_OK.match(m.group(1).strip()):
                        errors.append(
                            f"E4 {rel}: log date heading must be '## YYYY-MM-DD', got '## {m.group(1)}'"
                        )
        else:
            if fm_text is None:
                errors.append(f"E1 {rel}: missing/unterminated YAML frontmatter")
            else:
                try:
                    fm = yaml.safe_load(fm_text) or {}
                    if not isinstance(fm, dict):
                        errors.append(f"E1 {rel}: frontmatter is not a mapping")
                        fm = {}
                except yaml.YAMLError as e:
                    errors.append(f"E1 {rel}: unparseable frontmatter: {e}")
                    fm = {}
                if not str(fm.get("type", "")).strip():
                    errors.append(f"E2 {rel}: frontmatter missing non-empty 'type'")
                # v0.2 trust layer shape
                gen = fm.get("generated")
                if gen is not None:
                    if not isinstance(gen, dict) or not gen.get("by"):
                        errors.append(f"E5 {rel}: generated must be a mapping with 'by'")
                    else:
                        if not ACTOR.match(str(gen["by"])):
                            warnings.append(f"W1 {rel}: generated.by actor shape: {gen['by']}")
                        _ts(gen.get("at"), "generated.at", rel, warnings)
                for v in fm.get("verified") or []:
                    if not isinstance(v, dict) or not v.get("by"):
                        errors.append(f"E5 {rel}: verified[] entries need 'by'")
                    else:
                        if not ACTOR.match(str(v["by"])):
                            warnings.append(f"W1 {rel}: verified.by actor shape: {v['by']}")
                        _ts(v.get("at"), "verified[].at", rel, warnings)
                for s in fm.get("sources") or []:
                    if not isinstance(s, dict) or not str(s.get("resource", "")).strip():
                        errors.append(f"W3->E {rel}: sources[] entries need a resource")
                    else:
                        _ts(s.get("last_modified"), "sources[].last_modified", rel, warnings)
                if fm.get("stale_after") is not None:
                    _ts(fm["stale_after"], "stale_after", rel, warnings)
                if fm.get("timestamp") is not None and not isinstance(
                    fm["timestamp"], str
                ):
                    warnings.append(f"W2 {rel}: timestamp should be an ISO string")

        # collect link targets for the broken-link info count
        for m in MD_LINK.finditer(body):
            link_targets.add(m.group(1))
        if fm_text is not None and rel == "index.md":
            pass

    # broken bundle-relative links (info only)
    broken = []
    for target in sorted(link_targets):
        if not target.startswith("/"):
            continue
        if not os.path.exists(os.path.join(root, target.lstrip("/"))):
            broken.append(target)
    if broken:
        infos.append(f"INFO {len(broken)} broken bundle-relative links (allowed by §5.3)")
    return errors, warnings, infos, broken


def _ts(value, field, rel, warnings):
    if value is None:
        return
    if not isinstance(value, str) or not ISO_OFFSET.match(value):
        warnings.append(f"W2 {rel}: {field} must be ISO 8601 with UTC offset, got {value!r}")


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
