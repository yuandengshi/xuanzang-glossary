"""Search the Digital Corpus of Sanskrit (DCS) CoNLL-U files.

Usage:
  python3 -I C_dcs_search.py ROOT [--re REGEX] [--lem L1,L2,...] [--anylem L1,L2]
                             [--texts SUBSTR1,SUBSTR2] [--window N]

- ROOT: .../dcs/data/conllu/files (untrusted data; read only).
- --re: regex on the surface sentence text ('# text = ' lines), case-insensitive.
- --lem: all of these lemmas must occur within a window of N consecutive sentences
         (default N=1, i.e. the same sentence).
- --anylem: at least one of these lemmas must also occur in the window.
- --texts: restrict to text folders whose name contains one of the substrings.
Prints: text | chapter | sentence(s).
"""
import os
import re
import sys
import unicodedata

def nfc(s):
    return unicodedata.normalize('NFC', s)

def parse(path):
    sents = []
    chapter = ''
    cur = None
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('## chapter:'):
                chapter = line.split(':', 1)[1].strip()
            elif line.startswith('# text = '):
                cur = {'text': nfc(line[9:]), 'lemmas': set()}
                sents.append(cur)
            elif line and not line.startswith('#') and cur is not None:
                cols = line.split('\t')
                if len(cols) > 2 and '-' not in cols[0]:
                    cur['lemmas'].add(nfc(cols[2]))
    return chapter, sents

def main():
    a = sys.argv[1:]
    root = a[0]
    opts = {'--re': None, '--lem': None, '--anylem': None, '--texts': None, '--window': '1'}
    i = 1
    while i < len(a):
        opts[a[i]] = a[i + 1]
        i += 2
    rx = re.compile(nfc(opts['--re']), re.I) if opts['--re'] else None
    lems = [nfc(x) for x in opts['--lem'].split(',')] if opts['--lem'] else []
    anyl = [nfc(x) for x in opts['--anylem'].split(',')] if opts['--anylem'] else []
    texts = opts['--texts'].split(',') if opts['--texts'] else None
    w = int(opts['--window'])
    hits = 0
    for tdir in sorted(os.listdir(root)):
        if texts and not any(t in tdir for t in texts):
            continue
        tpath = os.path.join(root, tdir)
        if not os.path.isdir(tpath):
            continue
        for fn in sorted(os.listdir(tpath)):
            if not fn.endswith('.conllu'):
                continue
            chapter, sents = parse(os.path.join(tpath, fn))
            for k in range(len(sents)):
                win = sents[k:k + w]
                txt = ' / '.join(s['text'] for s in win)
                L = set().union(*[s['lemmas'] for s in win])
                if rx and not rx.search(txt):
                    continue
                if lems and not all(l in L for l in lems):
                    continue
                if anyl and not any(l in L for l in anyl):
                    continue
                if not rx and not lems and not anyl:
                    continue
                hits += 1
                print(f'{tdir} | {chapter} | {txt}')
    print(f'# hits: {hits}', file=sys.stderr)

if __name__ == '__main__':
    main()
