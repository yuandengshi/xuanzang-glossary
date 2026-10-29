#!/usr/bin/env python3
"""akbh1_units.py -- 按 units_map.tsv 把梵本、玄奘、真谛切成对齐单位，输出 JSON 和三方对照本（md）。

Usage: python3 -I akbh1_units.py AKBH1_DIR OUT_JSON OUT_MD
单位边界：玄奘按第 k 个"頌曰"、真谛按对应的"偈曰"，在字符位置上切分（不是按整行）。
文本中用〔0001b03〕标出大正藏行首。
"""
import csv
import json
import re
import sys


def load_lines(path):
    return [(r['line'], r['text']) for r in csv.DictReader(open(path, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)]


def stream(lines):
    """拼成带行号标记的串，并记录每个"正文字符"在串中的位置。"""
    s, pos = '', []
    for n, t in lines:
        s += '〔%s〕' % n
        for ch in t:
            pos.append(len(s))
            s += ch
    plain = ''.join(t for _, t in lines)
    return s, pos, plain


def cut_points(plain, pos, mark, picks):
    ms = [m.start() for m in re.finditer(mark, plain)]
    return [0 if p is None else pos[ms[p - 1]] for p in picks]


def main(d, out_json, out_md):
    units = list(csv.DictReader(open(d + '/units_map.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    skt = list(csv.DictReader(open(d + '/skt_sent.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    xs, xpos, xplain = stream(load_lines(d + '/xz_lines.tsv'))
    ps, ppos, pplain = stream(load_lines(d + '/pm_lines.tsv'))
    pmv = list(csv.DictReader(open(d + '/pm_verses.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    # 玄奘：第 1 单位从头起，其后第 u 单位从第 (u-1) 个"頌曰"起
    xcut = cut_points(xplain, xpos, r'頌\s*曰', [None] + list(range(1, len(units))))
    # 真谛：单位起点 = 对应的第 p 个"偈曰"
    pidx = []
    for u in units:
        k = [i for i, r in enumerate(pmv, 1) if r['line'] == u['pm_line'] and r['text'] == u['pm_verse']]
        pidx.append(k[0] if k else None)
    pcut = cut_points(pplain, ppos, r'偈\s*曰', [None] + pidx[1:])
    sids = [s['sid'] for s in skt]
    scut = [sids.index(u['skt_sid']) for u in units]
    out = []
    for i, u in enumerate(units):
        xe = xcut[i + 1] if i + 1 < len(units) else len(xs)
        pe = pcut[i + 1] if i + 1 < len(units) else len(ps)
        se = scut[i + 1] if i + 1 < len(units) else len(skt)
        xz = xs[xcut[i]:xe]
        if not xz.startswith('〔'):
            xz = '〔%s〕' % re.findall(r'〔([0-9a-z]+)〕', xs[:xcut[i] + 1])[-1] + xz
        pm = ps[pcut[i]:pe]
        if not pm.startswith('〔'):
            pm = '〔%s〕' % re.findall(r'〔([0-9a-z]+)〕', ps[:pcut[i] + 1])[-1] + pm
        out.append({'unit': u['unit'], 'karika': u['karika'], 'xz': xz, 'pm': pm,
                    'skt': skt[scut[i]:se]})
    json.dump(out, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    L = ['# 俱舍论·界品 梵汉三方对照（工作底本）', '',
         '梵本：GRETIL 本（Pradhan 1975 为底本，Hackett & Lusthaus 修订），[页|行] 为 Pradhan 本页行；**粗体**为本颂。',
         '玄奘：T1558 卷1–2；真谛：T1559 卷1–2；〔0001a08〕为大正藏第 29 册页栏行。', '']
    for u in out:
        L += ['## %s（颂 %s）' % (u['unit'], u['karika']), '', '**梵**', '']
        for s in u['skt']:
            t = s['text']
            L.append('- `%s` [%s] %s' % (s['sid'], s['pradhan'], '**%s**' % t if s['verse'] == 'V' else t))
        L += ['', '**玄奘**', '', u['xz'], '', '**真谛**', '', u['pm'], '']
    open(out_md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(len(out), 'units;', 'skt', sum(len(u['skt']) for u in out), 'sentences')


if __name__ == '__main__':
    main(*sys.argv[1:4])
