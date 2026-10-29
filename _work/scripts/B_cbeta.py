#!/usr/bin/env python3
"""B_cbeta.py -- flatten a CBETA P5 XML file to plain text with Taisho line refs,
and optionally KWIC-search it.

Usage:
  python3 -I B_cbeta.py DATA_XML                 -> print "p.col.line|text" lines
  python3 -I B_cbeta.py DATA_XML REGEX [...] [--ctx N]  -> KWIC with line refs
Reads the XML as text only (regex based, no external entity resolution).
"""
import re
import sys


def flatten(xml):
    # drop header
    body = xml.split("<body>", 1)[-1]
    # remove notes / app variants (keep lemma), cb:mulu, etc.
    body = re.sub(r"<note\b[^>]*>.*?</note>", "", body, flags=re.S)
    body = re.sub(r"<rdg\b[^>]*>.*?</rdg>", "", body, flags=re.S)
    body = re.sub(r"<cb:mulu\b[^>]*>.*?</cb:mulu>", "", body, flags=re.S)
    body = re.sub(r"<cb:docNumber>.*?</cb:docNumber>", "", body, flags=re.S)
    # gaiji: keep the <g> text if present
    body = re.sub(r"<g\b[^>]*ref=\"#([^\"]+)\"[^>]*/>", r"[\1]", body)
    # mark line beginnings
    body = re.sub(r"<lb\b[^>]*\bn=\"([0-9a-z]+)\"[^>]*/>", r"\n@@\1@@", body)
    body = re.sub(r"<pb\b[^>]*/>", "", body)
    body = re.sub(r"<juan\b[^>]*fun=\"open\"[^>]*>", "\n【卷】", body)
    body = re.sub(r"<[^>]+>", "", body)
    out = []
    for line in body.split("\n"):
        m = re.match(r"@@([0-9a-z]+)@@(.*)", line)
        if m:
            out.append((m.group(1), m.group(2).strip()))
        elif line.strip():
            if out:
                out[-1] = (out[-1][0], out[-1][1] + line.strip())
    return out


def main(argv):
    if not argv:
        print(__doc__); return 1
    path = argv[0]
    ctx = 2
    pats = []
    i = 1
    while i < len(argv):
        if argv[i] == "--ctx":
            ctx = int(argv[i + 1]); i += 2; continue
        pats.append(argv[i]); i += 1
    xml = open(path, encoding="utf-8", errors="replace").read()
    lines = flatten(xml)
    if not pats:
        for n, t in lines:
            print("%s|%s" % (n, t))
        return 0
    for p in pats:
        rx = re.compile(p)
        print("=" * 10, p)
        hits = 0
        for k, (n, t) in enumerate(lines):
            win = "".join(x[1] for x in lines[k:k + 2])
            if rx.search(t) or (rx.search(win) and not rx.search(lines[k + 1][1] if k + 1 < len(lines) else "")):
                hits += 1
                lo, hi = max(0, k - ctx), min(len(lines), k + ctx + 1)
                print("--- " + lines[k][0])
                for j in range(lo, hi):
                    print("   %s|%s" % lines[j])
        print("[%d hits]" % hits)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
