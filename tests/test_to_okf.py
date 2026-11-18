#!/usr/bin/env python3
"""Tests for to_okf.py — llm-wiki → OKF v0.2 mapping (stdlib unittest)."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import to_okf  # noqa: E402


class TestWikilinks(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        for rel, title in [
            ("entities/instruments/hammond-b3.md", "Hammond B-3"),
            ("entities/players/jimmy-smith.md", "Jimmy Smith"),
            ("index.md", "B3Wiki Index"),
        ]:
            p = os.path.join(self.root, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(f"---\ntitle: {title}\n---\nbody\n")
        self.slug_map = to_okf.build_slug_map(self.root)

    def test_aliased_link(self):
        out = to_okf.rewrite_wikilinks(
            "the [[hammond-b3|Hammond B-3]] rocks", "entities/players/x.md", self.slug_map, self.root
        )
        self.assertEqual(out, "the [Hammond B-3](/entities/instruments/hammond-b3.md) rocks")

    def test_bare_link_uses_title(self):
        out = to_okf.rewrite_wikilinks("see [[hammond-b3]]", "entities/players/x.md", self.slug_map, self.root)
        self.assertEqual(out, "see [Hammond B-3](/entities/instruments/hammond-b3.md)")

    def test_path_style_from_root(self):
        out = to_okf.rewrite_wikilinks(
            "- [[instruments/hammond-b3|Hammond B-3]] - x", "index.md", self.slug_map, self.root
        )
        self.assertEqual(out, "- [Hammond B-3](/entities/instruments/hammond-b3.md) - x")

    def test_relative_parent_link(self):
        out = to_okf.rewrite_wikilinks(
            "Main catalog: [[../index|index.md]]", "entities/players/_index.md", self.slug_map, self.root
        )
        self.assertEqual(out, "Main catalog: [index.md](/index.md)")

    def test_broken_link_tolerated(self):
        out = to_okf.rewrite_wikilinks("see [[refunds]]", "concepts/x.md", self.slug_map, self.root)
        self.assertEqual(out, "see [refunds](/refunds.md)")


class TestCitations(unittest.TestCase):
    def test_markers_numbered_and_deduped(self):
        body = "A.^[raw/articles/a.md] B.^[raw/articles/b.md] C.^[raw/articles/a.md]"
        new, order = to_okf.extract_citations(body)
        self.assertEqual(new, "A.[1] B.[2] C.[1]")
        self.assertEqual(order, ["raw/articles/a.md", "raw/articles/b.md"])

    def test_citations_section(self):
        text = to_okf.citations_section(
            ["raw/articles/a.md"], {"raw/articles/a.md": "Wikipedia: A"}
        )
        self.assertIn("# Citations", text)
        self.assertIn("[1] [Wikipedia: A](/raw/articles/a.md)", text)


class TestFrontmatter(unittest.TestCase):
    def test_page_mapping(self):
        fm = {
            "title": "Jimmy Smith", "created": "2026-10-20", "updated": "2026-10-20",
            "type": "entity", "tags": ["person", "music"],
            "sources": ["raw/articles/wikipedia-jimmy-smith.md",
                        "https://en.wikipedia.org/wiki/Jimmy_Smith"],
            "confidence": "high", "died": "2005-02-08",
        }
        raw_meta = {"raw/articles/wikipedia-jimmy-smith.md":
                    {"ingested": "2026-10-20", "source_url": "https://x/y"}}
        out = to_okf.map_page_frontmatter(fm, "Player", "Jazz organist.", raw_meta)
        self.assertEqual(out["type"], "Player")
        self.assertEqual(out["description"], "Jazz organist.")
        self.assertEqual(out["timestamp"], "2026-10-20T00:00:00Z")
        self.assertEqual(out["generated"],
                         {"by": "process:b3wiki-agent", "at": "2026-10-20T00:00:00Z"})
        s0, s1 = out["sources"]
        self.assertEqual(s0["resource"], "/raw/articles/wikipedia-jimmy-smith.md")
        self.assertEqual(s0["last_modified"], "2026-10-20T00:00:00Z")
        self.assertEqual(s1["resource"], "https://en.wikipedia.org/wiki/Jimmy_Smith")
        self.assertNotEqual(s0["id"], s1["id"])
        self.assertEqual(out["confidence"], "high")   # extras preserved
        self.assertEqual(out["died"], "2005-02-08")

    def test_raw_mapping(self):
        fm = {"source_url": "https://en.wikipedia.org/wiki/Hammond_organ",
              "ingested": "2026-10-20", "sha256": "abc"}
        out = to_okf.map_raw_frontmatter(fm, "Hammond organ")
        self.assertEqual(out["type"], "Source")
        self.assertEqual(out["resource"], "https://en.wikipedia.org/wiki/Hammond_organ")
        self.assertEqual(out["timestamp"], "2026-10-20T00:00:00Z")
        self.assertEqual(out["sha256"], "abc")

    def test_serialize_roundtrip(self):
        fm = {"type": "Player", "title": "X", "timestamp": "2026-10-20T00:00:00Z",
              "sources": [{"resource": "/raw/a.md", "id": "a"}]}
        page = to_okf.serialize(fm, "# X\n\nbody\n")
        import yaml
        yaml_text, body = to_okf.split_frontmatter(page)
        self.assertEqual(yaml.safe_load(yaml_text), fm)
        # split contract (SaussuNet): the blank line after closing --- belongs to the body
        self.assertEqual(body, "\n# X\n\nbody\n")


class TestLog(unittest.TestCase):
    def test_group_by_date(self):
        md = (
            "# B3Wiki Log\n\n"
            "> Format: `## [YYYY-MM-DD] action | subject`\n\n"
            "## [2026-10-20] create | Wiki initialized\n- Domain: x\n\n"
            "## [2026-10-20] ingest | Wikipedia: Leslie\n- Files: a, b\n\n"
            "## [2026-10-21] lint | 0 issues\n"
        )
        out = to_okf.reformat_log(md)
        self.assertEqual(out.count("## 2026-10-20"), 1)
        self.assertIn("* **Create**: Wiki initialized", out)
        self.assertIn("  - Domain: x", out)
        self.assertIn("* **Ingest**: Wikipedia: Leslie", out)
        self.assertIn("## 2026-10-21", out)
        self.assertNotIn("[2026", out)


class TestDescriptions(unittest.TestCase):
    def test_index_descriptions(self):
        body = (
            "- [[players/jimmy-smith|Jimmy Smith]] — Jazz organist.\n"
            "- [[instruments/hammond-b3|Hammond B-3]] - The iconic console.\n"
        )
        d = to_okf.parse_index_descriptions(body)
        self.assertEqual(d["jimmy-smith"], "Jazz organist.")
        self.assertEqual(d["hammond-b3"], "The iconic console.")

    def test_first_sentence_fallback(self):
        body = "# T\n\nBorn **James Oscar Smith** in 1928. Second sentence here.\n"
        self.assertEqual(to_okf.first_sentence(body), "Born **James Oscar Smith** in 1928.")

    def test_lenient_parse_of_invalid_yaml(self):
        fm = to_okf.parse_lenient('title: "Brother" Jack McDuff\ntags: [music, person]\n')
        self.assertEqual(fm["title"], '"Brother" Jack McDuff')
        self.assertEqual(fm["tags"], ["music", "person"])


class TestNewsletter(unittest.TestCase):
    def test_no_frontmatter_page(self):
        out = to_okf.map_newsletter_frontmatter("# The Organ Donor\n\n*Vol. 43*", "261021-B3Wiki-newsletter")
        self.assertEqual(out["type"], "Newsletter")
        self.assertEqual(out["title"], "The Organ Donor")
        self.assertEqual(out["timestamp"], "2026-10-21T00:00:00Z")


class TestConvertEndToEnd(unittest.TestCase):
    def test_mini_bundle(self):
        root = tempfile.mkdtemp()
        files = {
            "log.md": "# Log\n\n> Format: `## [YYYY-MM-DD] action | subject`\n\n"
                      "## [2026-10-20] create | Wiki initialized\n- Domain: x\n",
            "index.md": "# Index\n\n- [[players/a|A]] — A page.\n",
            "entities/players/a.md": "---\ntitle: A\ntype: entity\ntags: [person]\n"
                                     "sources: [raw/articles/r.md]\n---\n\nSee [[r]].\n",
            "raw/articles/r.md": "---\nsource_url: https://x.org\ningested: 2026-10-19\n"
                                 "sha256: abc\n---\n\n# R source\n",
        }
        for rel, text in files.items():
            p = os.path.join(root, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(text)
        to_okf.convert(root)
        log = open(os.path.join(root, "log.md")).read()
        self.assertIn("## 2026-10-20", log)          # regression: log must not be emptied
        self.assertIn("* **Create**: Wiki initialized", log)
        page = open(os.path.join(root, "entities/players/a.md")).read()
        self.assertIn("type: Player", page)
        self.assertIn("[R source](/raw/articles/r.md)", page)
        self.assertIn("# Citations", page)
        root_index = open(os.path.join(root, "index.md")).read()
        self.assertIn("okf_version: '0.2'", root_index)


if __name__ == "__main__":
    unittest.main()
