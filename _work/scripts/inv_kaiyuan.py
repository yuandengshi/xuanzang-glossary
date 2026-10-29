#!/usr/bin/env python3
"""inv_kaiyuan.py -- 把《开元录》卷八玄奘译经目录与 CBETA API 的玄奘作品列表对齐。

Usage: python3 -I inv_kaiyuan.py T2154.txt works_A000294.json OUT.tsv
  T2154.txt: B_cbeta.py 的输出（行号|文字）
输出 TSV：开元录序号、开元录题名、开元录卷数、CBETA 编号、CBETA 题名、CBETA 卷数、备注
"""
import json
import re
import sys

CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}


def cn2int(s):
    s = s.replace('一百', '百') if s.startswith('一百') else s
    n, cur = 0, 0
    for ch in s:
        if ch in CN:
            cur = CN[ch]
        elif ch == '十':
            n += (cur or 1) * 10; cur = 0
        elif ch == '百':
            n += (cur or 1) * 100; cur = 0
    return n + cur


def kaiyuan_list(path):
    lines = [l.rstrip('\n').split('|', 1) for l in open(path, encoding='utf-8')]
    text = ''.join(t for _, t in lines)
    m = re.search(r'可為萬代錧轄矣。(大般若.*?)右七十六部一千三百四十七卷', text)
    body = m.group(1)
    items = re.findall(r'(.+?)([一二三四五六七八九十百]+)卷', body)
    return [(t, cn2int(n)) for t, n in items]


def norm(t):
    t = re.sub(r'（.*?）', '', t).replace('瑠', '琉')
    for a, b in [('呪五首經', '呪五首'), ('佛地經', '佛說佛地經'),
                 ('攝大乘論世親釋', '攝大乘論釋'), ('攝大乘論無性釋', '攝大乘論釋'),
                 ('唯識三十論', '唯識三十論頌'), ('阿毘達磨顯宗論', '阿毘達磨藏顯宗論')]:
        if t == a:
            t = b
    return t


def main(kpath, jpath, out):
    kl = kaiyuan_list(kpath)
    works = json.load(open(jpath, encoding='utf-8'))['results']
    tw = [w for w in works if w['canon'] == 'T']
    used = set()
    rows = []
    for i, (t, n) in enumerate(kl, 1):
        nt = norm(t)
        cands = [w for w in tw if w['title'] == nt and w['work'] not in used]
        if nt == '攝大乘論釋':
            cands = [w for w in cands if ('世親' in w['byline']) == ('世親' in t)]
        if cands:
            w = cands[0]; used.add(w['work'])
            note = '' if w['juan'] == n else '卷數不同'
            rows.append([i, t, n, w['work'], w['title'], w['juan'], note])
        else:
            rows.append([i, t, n, '', '', '', 'CBETA 未歸玄奘名下'])
    for w in tw:
        if w['work'] not in used:
            rows.append(['', '', '', w['work'], w['title'], w['juan'], '開元錄無對應'])
    with open(out, 'w', encoding='utf-8') as f:
        f.write('開元錄序\t開元錄題名\t開元錄卷\tCBETA\tCBETA題名\tCBETA卷\t備注\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('開元錄 %d 部 %d 卷' % (len(kl), sum(n for _, n in kl)))
    for r in rows:
        if r[6]:
            print(r)


if __name__ == '__main__':
    main(*sys.argv[1:4])
