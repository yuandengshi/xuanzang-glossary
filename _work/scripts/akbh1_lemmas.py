#!/usr/bin/env python3
"""akbh1_lemmas.py -- 维护规范词目表（_work/align/lemmas.tsv），全书各文本共用。

Usage: python3 -I akbh1_lemmas.py ALIGN_DIR [--init]
  --init：由现有数据建表（状态记"已登记"）
  不带参数：更新出现次数与主要译法；数据中出现的新词目追加为"新增"，需人工确认写法后把状态改为"已登记"
各栏：lemma、class（词类）、count（出现次数，含存档）、renderings（主要译法）、variants（异写，由
akbh1_normalize.py 的规则推出；数据中出现异写，体例自查报错）、status、note。
"""
import csv
import datetime
import glob
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import akbh1_normalize as N  # noqa: E402

COLS = ['lemma', 'class', 'count', 'renderings', 'variants', 'status', 'note']


def scan(align):
    cnt, cls, rend = Counter(), defaultdict(Counter), defaultdict(Counter)
    for f in glob.glob(os.path.join(align, '*', 'occ', 'U*.tsv')) + glob.glob(os.path.join(align, '*', 'occ_extra', 'U*.tsv')):
        for r in csv.DictReader(open(f, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE):
            l = r['lemma']
            if not l:
                continue
            cnt[l] += 1
            cls[l][r['pos'].split(' ')[0] if not r['pos'].startswith('gram') else 'gram.'] += 1
            rend[l][r['xz'] or '（未译）'] += 1
    return cnt, cls, rend


def variants(l):
    """由统一写法的规则反推可能的异写。"""
    inv = defaultdict(set)
    for a, b in N.LEX.items():
        inv[b].add(a)
    for a, b in N.MEMBER.items():
        inv[b].add(a)
    out = set(inv.get(l, ()))
    parts = l.split('-')
    for i, p in enumerate(parts):
        for v in inv.get(p, ()):
            out.add('-'.join(parts[:i] + [v] + parts[i + 1:]))
    if 'manas-vijñāna' in l:
        out.add(l.replace('manas-vijñāna', 'manovijñāna'))
    if 'cakṣus-vijñāna' in l:
        out.add(l.replace('cakṣus-vijñāna', 'cakṣurvijñāna'))
    if l.startswith(('a-', 'an-')) and '-' in l:
        out.add(l.replace('-', '', 1))
    out.discard(l)
    return sorted(out)


def main(align, init):
    path = os.path.join(align, 'lemmas.tsv')
    old = {}
    if os.path.exists(path) and not init:
        old = {r['lemma']: r for r in csv.DictReader(open(path, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
    cnt, cls, rend = scan(align)
    today = datetime.date.today().isoformat()
    rows, new = [], []
    for l in sorted(set(cnt) | set(old), key=lambda x: (x.lstrip('-('), x)):
        o = old.get(l, {})
        if l not in cnt and o:
            o = dict(o, count='0'); rows.append(o); continue
        st = o.get('status') or ('已登记' if init else '新增 %s' % today)
        if not o and not init:
            new.append(l)
        rows.append({'lemma': l, 'class': '/'.join(c for c, _ in cls[l].most_common()), 'count': str(cnt[l]),
                     'renderings': '；'.join('%s %d' % (x, n) for x, n in rend[l].most_common(5)),
                     'variants': o.get('variants') or '；'.join(variants(l)), 'status': st, 'note': o.get('note', '')})
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\t'.join(COLS) + '\n')
        for r in rows:
            f.write('\t'.join(r.get(c, '').replace('\t', ' ') for c in COLS) + '\n')
    print('词目 %d 个；本次新增 %d 个%s' % (len(rows), len(new), ('：' + '、'.join(new[:30])) if new else ''))


if __name__ == '__main__':
    main(sys.argv[1], '--init' in sys.argv[2:])
