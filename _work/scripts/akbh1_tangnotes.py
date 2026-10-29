#!/usr/bin/env python3
"""akbh1_tangnotes.py -- 从唐代注疏中抽出"梵云/此云/唐言/舊云…訛也"一类梵汉对照自注。

Usage: python3 -I akbh1_tangnotes.py OUT.tsv SRC:LABEL:VOL:FILE:START:END [...]
  FILE 为 B_cbeta.py 的输出（行号|文字）；START/END 为该书的起止行号（含）
  例：T1821:光記:41:T1821.txt:0001a03:0055c15
输出 TSV：source、ref（T41.1a05）、term（"此云/此譯/唐言/此翻/此名"后的汉译）、skt_tr（"梵云/正言/應云/舊云"后的音写）、text
"""
import re
import sys

# 只收真正的梵汉对照用语；"此云何""此言""應言"等泛用语不收
PAT = re.compile(r'梵[云言語名本]|唐[言云]|此[翻譯]|此云(?!何)|舊[云曰譯]|訛[也略]')
TERM = re.compile(r'(?:此譯云|此翻為|此云(?!何)|此[翻譯名]|唐[言云])[：:]?([^，。；、？！「」『』（）《》\s]{1,8})')
TR = re.compile(r'(?:梵[云言語名]|梵本應[云言]|正[言云]|舊[云曰]|舊譯(?:名|為)?)[：:]?([^，。；、？！「」『』（）《》\s]{1,12})')


def sents(path, start, end):
    on, buf = False, []
    for ln in open(path, encoding='utf-8'):
        n, t = ln.rstrip('\n').split('|', 1)
        if n == start:
            on = True
        if on:
            buf.append((n, t))
        if n == end:
            break
    s, owner = '', []
    for n, t in buf:
        s += t
        owner += [n] * len(t)
    out, a = [], 0
    for m in re.finditer(r'[。；？]', s):
        out.append((owner[a] if a < len(owner) else buf[-1][0], s[a:m.end()]))
        a = m.end()
    return out


def main(out, specs):
    rows = []
    for sp in specs:
        src, label, vol, path, start, end = sp.split(':')
        for ln, t in sents(path, start, end):
            if not PAT.search(t):
                continue
            term = '；'.join(dict.fromkeys(TERM.findall(t)))
            tr = '；'.join(dict.fromkeys(TR.findall(t)))
            ref = 'T%s.%d%s' % (vol, int(ln[:4]), ln[4:]) if src.startswith('T') else '%s.%s' % (src, ln)
            rows.append([label, ref, term, tr, t.strip()])
    with open(out, 'w', encoding='utf-8') as f:
        f.write('source\tref\tterm\tskt_tr\ttext\n')
        for r in rows:
            f.write('\t'.join(x.replace('\t', ' ') for x in r) + '\n')
    print(len(rows), 'notes')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
