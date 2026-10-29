#!/usr/bin/env python3
"""akbh1_eduhk_map.py -- 把香港教育大学语料库的页面自动对到本方单位（按每页梵文行与本方梵文句的词形重合度）。

Usage: python3 -I akbh1_eduhk_map.py EDUHK_DIR AKBH1_DIR FIRST LAST [START_UNIT]
输出：akbh1_calib.py 用的 PAGEMAP 串（如 "101-120:U06,121-140:U07"），以及无法确定的页。
"""
import glob
import html
import json
import os
import re
import sys
import unicodedata


def norm(s):
    return re.sub(r'[^a-zāīūṛṝḷṃḥṅñṭḍṇśṣ]', '', unicodedata.normalize('NFC', s.lower()))


def page_skt(path):
    """优先取页面"梵語"栏（带连声的原句，与 GRETIL 句子形式一致）；没有时退回对勘块中的梵文行。"""
    t = open(path, encoding='utf-8', errors='replace').read()
    x = html.unescape(re.sub(r'<[^>]+>', '\n', t))
    m = re.search(r'梵語\s*(.*?)\s*真諦譯', x, flags=re.S)
    if m and re.search(r'[a-zāīūṛṃḥśṣ]{3,}', m.group(1)):
        return re.sub(r'\s+', ' ', m.group(1))
    out = []
    for pre in re.findall(r'<pre>(.*?)</pre>', t, flags=re.S):
        for l in html.unescape(re.sub(r'<[^>]+>', '', pre)).split('\n'):
            if re.search(r'[a-zāīūṛṃḥśṣ]{3,}', l) and not re.search(r'[一-鿿]', l):
                out.append(l)
    return ' '.join(out)


def main(edir, adir, first, last, start_unit=None):
    units = json.load(open(os.path.join(adir, 'units.json'), encoding='utf-8'))
    order = [u['unit'] for u in units]
    sents = [(order.index(u['unit']), norm(s['text'])) for u in units for s in u['skt']]
    res, cur = [], (order.index(start_unit) if start_unit else None)
    for p in range(int(first), int(last) + 1):
        f = os.path.join(edir, 'p%04d.html' % p)
        if not os.path.exists(f):
            continue
        toks = [norm(x) for x in re.split(r'[\s/|]+', page_skt(f).replace('-', '')) if len(norm(x)) >= 4][:12]
        if not toks:
            res.append((p, None)); continue
        # 单位只能顺序前进（当前单位到其后三个单位之间），同分取靠前的
        best, bu = 0, None
        for ui, s in sents:
            if cur is not None and not (cur <= ui <= cur + 3):
                continue
            sc = sum(1 for t in toks if t[:-1] in s)
            if sc > best or (sc == best and bu is not None and ui < bu):
                best, bu = sc, ui
        if bu is not None and best >= max(2, len(toks) // 3):
            cur = bu
            res.append((p, order[bu]))
        else:
            res.append((p, None))
    # 无法确定的页沿用前一页的单位；再压缩为区间
    last_u, ranges, unknown = None, [], []
    for p, u in res:
        if u is None:
            unknown.append(p); u = last_u
        if u is None:
            continue
        if ranges and ranges[-1][2] == u and ranges[-1][1] == p - 1:
            ranges[-1][1] = p
        else:
            ranges.append([p, p, u])
        last_u = u
    print(','.join('%d-%d:%s' % (a, b, u) for a, b, u in ranges))
    print('未能确定、沿用前页的：', unknown, file=sys.stderr)


if __name__ == '__main__':
    main(*sys.argv[1:6])
