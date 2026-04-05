#!/usr/bin/env python3
"""ipa-fe-syllabus-ver9-2.md から「用語例」を抽出し、用語集用 Markdown 断片を標準出力する。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYLLABUS = ROOT / "data" / "corpus" / "ipa-fe-syllabus-ver9-2.md"


def _norm(s: str) -> str:
    s = re.sub(r"[\u3000\s]+", " ", s.strip())
    s = re.sub(r"([\u3040-\u9fff])\s+([\u3040-\u9fff])", r"\1\2", s)
    return s.strip()


def _split_terms(blob: str) -> list[str]:
    blob = _norm(blob)
    if not blob:
        return []
    parts = re.split(r"[，、](?![^（]*[））])", blob)
    out: list[str] = []
    for p in parts:
        t = _norm(p)
        t = re.sub(r"^[（(].*?[）)]\s*", "", t)
        if not t or len(t) > 100:
            continue
        if "Copyright" in t or "http" in t.lower() or t.startswith("<!--"):
            continue
        bad_frag = (
            "当該小分類",
            "修得すべき用語",
            "人材像に照らして",
            "その幅と深さを大きく示す",
            "修得項目とともに具体的に示す",
            "キーワード例当該",
        )
        if any(b in t for b in bad_frag):
            continue
        if re.match(r"^[-\d]+$", t):
            continue
        out.append(t)
    return out


def _major_region(line: str) -> str | None:
    if "◆テクノロジ系◆" in line or line.strip() == "テクノロジ系":
        return "tech"
    if "◆マネジメント系◆" in line or line.strip() == "マネジメント系":
        return "mgmt"
    if "◆ストラテジ系◆" in line or line.strip() == "ストラテジ系":
        return "strat"
    return None


def extract_terms_by_region(text: str) -> dict[str, set[str]]:
    lines = text.splitlines()
    region = "tech"
    by_region: dict[str, set[str]] = {"tech": set(), "mgmt": set(), "strat": set()}
    i = 0
    while i < len(lines):
        ln = lines[i]
        mreg = _major_region(ln)
        if mreg:
            region = mreg
        if "用語例" in ln and not ln.strip().startswith(">"):
            if "当該小分類" in ln:
                i += 1
                continue
            chunk_lines: list[str] = []
            if "用語例" in ln:
                after = ln.split("用語例", 1)[1].strip()
                after = re.sub(r"^[：:]\s*", "", after)
                if after:
                    chunk_lines.append(after)
            i += 1
            while i < len(lines):
                nl = lines[i].strip()
                if not nl:
                    break
                if nl.startswith("<!--"):
                    break
                if nl.startswith("【") and "目標" in nl:
                    break
                if re.match(r"^（[0-9]+）", nl):
                    break
                if re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩]", nl):
                    break
                if re.match(r"^[-\d]+\.\s", nl) and "用語例" not in nl:
                    break
                if nl.startswith("大分類") or nl.startswith("中分類"):
                    break
                if nl.startswith("Copyright"):
                    break
                if "用語例" in nl:
                    rest = nl.split("用語例", 1)[1].strip()
                    rest = re.sub(r"^[：:]\s*", "", rest)
                    if rest:
                        chunk_lines.append(rest)
                else:
                    chunk_lines.append(nl)
                i += 1
            blob = " ".join(chunk_lines)
            for t in _split_terms(blob):
                by_region[region].add(t)
            continue
        i += 1
    return by_region


def _wrap_terms(terms: list[str], per_line: int = 14) -> list[str]:
    lines_out: list[str] = []
    for j in range(0, len(terms), per_line):
        chunk = terms[j : j + per_line]
        lines_out.append("・" + " ・".join(chunk))
    return lines_out


def main() -> None:
    if not SYLLABUS.is_file():
        print(f"Missing {SYLLABUS}", file=sys.stderr)
        sys.exit(1)
    text = SYLLABUS.read_text(encoding="utf-8")
    by_r = extract_terms_by_region(text)

    titles = {
        "tech": "## テクノロジ系｜シラバス「用語例」索引",
        "mgmt": "## マネジメント系｜シラバス「用語例」索引",
        "strat": "## ストラテジ系｜シラバス「用語例」索引",
    }
    for key in ("tech", "mgmt", "strat"):
        print(titles[key])
        print()
        print(
            "IPA 基本情報技術者試験シラバス Ver.9.2（`ipa-fe-syllabus-ver9-2.md` 由来）の"
            "「用語例」を機械抽出し、重複を除いて整理したキーワード一覧です。"
            "各用語の定義・出題の深さは**公式 PDF**を正としてください。"
        )
        print()
        terms = sorted(by_r[key], key=lambda x: (x.lower(), x))
        for line in _wrap_terms(terms):
            print(line)
        print()


if __name__ == "__main__":
    main()
