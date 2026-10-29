"""Full-text regex search over the GRETIL Sanskrit corpus (HTML/plain files).

Usage:
  python3 -I C_gretil_search.py ROOT PATTERN [PATTERN ...] [--ctx N] [--files GLOBSUBSTR]

- ROOT: directory of the unzipped GRETIL corpus (untrusted data; only read, never executed).
- PATTERN: Python regex, matched against text with HTML tags removed, whitespace collapsed,
  and NFC-normalised. Case-insensitive.
- Prints: relative path, match, and N chars of context on each side.
Only *.htm, *.html, *.txt files are read. The tei/ subfolder is skipped by default (it
duplicates the HTML texts) unless --tei is given.
"""
import os
import re
import sys
import html
import unicodedata

def load(path):
    raw = open(path, 'rb').read()
    for enc in ('utf-8', 'cp1252', 'latin-1'):
        try:
            t = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    t = re.sub(r'(?is)<(script|style).*?</\1>', ' ', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = unicodedata.normalize('NFC', t)
    t = re.sub(r'\s+', ' ', t)
    return t

def main():
    args = sys.argv[1:]
    ctx = 150
    tei = False
    filt = None
    if '--ctx' in args:
        i = args.index('--ctx'); ctx = int(args[i + 1]); del args[i:i + 2]
    if '--tei' in args:
        args.remove('--tei'); tei = True
    if '--files' in args:
        i = args.index('--files'); filt = args[i + 1]; del args[i:i + 2]
    root = args[0]
    pats = [re.compile(unicodedata.normalize('NFC', p), re.I) for p in args[1:]]
    nfiles = 0
    nhits = 0
    for dp, dn, fn in os.walk(root):
        dn.sort()
        if not tei and os.sep + 'tei' in dp + os.sep and '/tei/' in (dp + '/'):
            continue
        for f in sorted(fn):
            if not f.lower().endswith(('.htm', '.html', '.txt')):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root)
            if filt and filt not in rel:
                continue
            nfiles += 1
            t = load(p)
            for pat in pats:
                for m in pat.finditer(t):
                    nhits += 1
                    a = max(0, m.start() - ctx); b = min(len(t), m.end() + ctx)
                    print(f'### {rel} | /{pat.pattern}/ | {m.group(0)}')
                    print('    ' + t[a:b])
    print(f'# searched {nfiles} files, {nhits} hits', file=sys.stderr)

if __name__ == '__main__':
    main()
