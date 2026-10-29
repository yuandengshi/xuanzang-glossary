#!/usr/bin/env python3
"""akbh1_prep.py -- 俱舍论界品试点：把梵本（GRETIL）、玄奘（T1558）、真谛（T1559）切成句、颂单位。

Usage: python3 -I akbh1_prep.py GRETIL_XML T1558_TXT T1559_TXT OUTDIR
输出：
  skt_sent.tsv   梵文单位：sid、Pradhan 页|行、是否本颂(V)、所属颂号、文本
  xz_lines.tsv   玄奘逐行：行号、文本（只取界品）
  pm_lines.tsv   真谛逐行
  skt_verses.tsv / xz_verses.tsv / pm_verses.tsv   三方的颂文单位，供人工对齐颂号
"""
import os
import re
import sys
import unicodedata

VAKK = re.compile(r'//\s*VAkK_(\d+)\.(\d+)\s*//', re.I)


def skt(path):
    """解析 GRETIL TEI XML：每个 <p> 是 Pradhan 本的一个页|行单位；加粗部分是本颂。
    本颂片段归属到其后最近的 VAkK 编号。"""
    x = open(path, encoding='utf-8').read()
    a = x.index('prathamaṃ kośasthānam')
    b = x.index('prathamaṃ kośasthānaṃ samāptam', a)
    out = []
    for body in re.findall(r'<p>(.*?)</p>', x[a:b + 200], flags=re.S):
        m = re.match(r'\s*\[(\d{3}\|\d{2})(?:-(\d{3}\|\d{2}))?\]', body)
        ref = (m.group(1) + ('-' + m.group(2) if m.group(2) else '')) if m else ''
        body = body[m.end():] if m else body
        bold = bool(re.search(r'rend="bold"', body))
        txt = re.sub(r'<[^>]+>', ' ', body)
        txt = unicodedata.normalize('NFC', re.sub(r'\s+', ' ', txt).strip())
        if not txt:
            continue
        vk = VAKK.search(txt)
        out.append([ref, 'V' if bold else '', vk.group(1) + '.' + vk.group(2) if vk else '', txt])
    # 本颂片段归属到其后最近的颂号
    nxt = ''
    for r in reversed(out):
        if r[2]:
            nxt = r[2]
        if r[1] == 'V':
            r[2] = nxt
    return out


def cb(path, start, end):
    rows = []
    on = False
    for ln in open(path, encoding='utf-8'):
        n, t = ln.rstrip('\n').split('|', 1)
        if n == start:
            on = True
        if on:
            rows.append([n, t])
        if n == end:
            break
    return rows


def verses(rows, open_mark, close_mark, first=None):
    """按"頌曰/偈曰 … 論曰/釋曰"切出颂文单位（标记可跨行），记下起始行号。"""
    txt, owner = '', []
    for n, t in rows:
        txt += t
        owner += [n] * len(t)
    out = [first] if first else []
    for m in re.finditer(open_mark + '[：:]?(.*?)' + close_mark, txt, flags=re.S):
        out.append([owner[m.start(1)] if m.start(1) < len(owner) else owner[-1], m.group(1).strip('：: ')])
    return out


def w(path, header, rows):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\t'.join(header) + '\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')


def main(gt, t1558, t1559, od):
    os.makedirs(od, exist_ok=True)
    s = skt(gt)
    w(os.path.join(od, 'skt_sent.tsv'), ['sid', 'pradhan', 'verse', 'karika', 'text'],
      [['S%04d' % i] + r for i, r in enumerate(s, 1)])
    w(os.path.join(od, 'skt_verses.tsv'), ['sid', 'pradhan', 'verse', 'karika', 'text'],
      [['S%04d' % i] + r for i, r in enumerate(s, 1) if r[1] == 'V'])
    xz = cb(t1558, '0001a07', '0013b09')
    pm = cb(t1559, '0161c06', '0173a03')
    w(os.path.join(od, 'xz_lines.tsv'), ['line', 'text'], xz)
    w(os.path.join(od, 'pm_lines.tsv'), ['line', 'text'], pm)
    w(os.path.join(od, 'xz_verses.tsv'), ['line', 'text'],
      verses(xz, '頌曰', '論曰', first=['0001a08', xz[1][1] + xz[2][1]]))
    w(os.path.join(od, 'pm_verses.tsv'), ['line', 'text'], verses(pm, '偈曰', '釋曰'))
    print('skt units', len(s), 'verse pieces', sum(1 for r in s if r[1] == 'V'))
    print('xz lines', len(xz), 'pm lines', len(pm))


if __name__ == '__main__':
    main(*sys.argv[1:5])
