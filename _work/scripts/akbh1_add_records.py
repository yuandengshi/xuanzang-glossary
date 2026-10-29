#!/usr/bin/env python3
"""akbh1_add_records.py -- 新增对应实例（如补复合词的整词记录），自动编号并核验后插入。

Usage: python3 -I akbh1_add_records.py AKBH1_DIR NEW.tsv [--dry]
NEW.tsv 栏目：before sid skt lemma pos xz_line xz type pm_line pm note（带表头，Tab 分隔）
  before：插在哪条记录之前（同单位 occ/ 中的 oid，一般是复合词的第一个成分）；新记录取该单位下一个空号。
核验同 akbh1_verify.py（skt 是梵文句的子串；xz、pm 按"…"分段出现在所标行起的两行窗口里），
pos 须合形态规则（morph.py）。任何一条不合格，整批都不写入。
"""
import csv
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import akbh1_verify as V  # noqa: E402
import morph  # noqa: E402

COLS = ['oid', 'sid', 'skt', 'lemma', 'pos', 'xz_line', 'xz', 'type', 'pm_line', 'pm', 'note']


def tsv(p):
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))


def main(d, new, dry):
    skt = {r['sid']: V.nfc(r['text']) for r in tsv(os.path.join(d, 'skt_sent.tsv'))}
    xz, xi = V.lines(os.path.join(d, 'xz_lines.tsv'))
    pm, pi = V.lines(os.path.join(d, 'pm_lines.tsv'))
    adds = tsv(new)
    errs, plan = [], {}
    nextno = {}
    for k, a in enumerate(adds, 2):
        a = {c: (a.get(c) or '').strip() for c in ['before'] + COLS[1:]}
        u = a['before'].split('-')[0]
        f = os.path.join(d, 'occ', u + '.tsv')
        if not os.path.exists(f):
            errs.append('第 %d 行：before %s 的单位不存在' % (k, a['before'])); continue
        if u not in nextno:
            used = [int(re.match(r'\d+', r['oid'].split('-')[1]).group(0)) for sub in ('occ', 'occ_extra')
                    for p in glob.glob(os.path.join(d, sub, u + '.tsv')) for r in tsv(p)]
            nextno[u] = max(used) + 1
        oids = [r['oid'] for r in tsv(f)]
        e = []
        if a['before'] not in oids:
            e.append('before %s 不在 %s' % (a['before'], f))
        if a['type'] not in V.TYPES:
            e.append('type 不合法')
        if a['sid'] not in skt:
            e.append('sid 不存在')
        elif not a['skt'] or V.nfc(a['skt']) not in skt[a['sid']]:
            e.append('skt "%s" 不在 %s' % (a['skt'], a['sid']))
        if a['type'] == '省译':
            if a['xz']:
                e.append('省译不应有 xz')
        else:
            if not a['xz'] or not a['xz_line']:
                e.append('缺 xz 或 xz_line')
            else:
                m = V.found(xz, xi, a['xz_line'], a['xz'])
                if m:
                    e.append('玄奘：' + m)
        if a['pm']:
            m = V.found(pm, pi, a['pm_line'], a['pm'])
            if m:
                e.append('真谛：' + m)
        mp = morph.problem(a['pos'], a['type'], a['lemma'])
        if mp:
            e.append('形态：' + mp)
        if not a['lemma'] or ' + ' in a['lemma']:
            e.append('lemma 为空或含"+"')
        if e:
            errs.append('第 %d 行（%s %s）：%s' % (k, a['before'], a['skt'], '；'.join(e))); continue
        a['oid'] = '%s-%03d' % (u, nextno[u]); nextno[u] += 1
        plan.setdefault(f, []).append(a)
    for e in errs:
        print('不合格', e)
    if errs:
        print('有 %d 行不合格，整批未写入' % len(errs)); return 1
    for f, items in plan.items():
        rows = tsv(f)
        hdr = open(f, encoding='utf-8').readline().rstrip('\n').split('\t')
        out = []
        for r in rows:
            out += [a for a in items if a['before'] == r['oid']]
            out.append(r)
        for a in items:
            print('%s新增 %s（在 %s 前）：%s | %s | %s | %s' % ('（试算）' if dry else '', a['oid'], a['before'], a['skt'], a['lemma'], a['pos'], a['xz'] or '（未译）'))
        if not dry:
            with open(f, 'w', encoding='utf-8') as fo:
                fo.write('\t'.join(hdr) + '\n')
                for r in out:
                    fo.write('\t'.join(r.get(h, '') for h in hdr) + '\n')
    print('%s新增 %d 条' % ('（试算）' if dry else '', sum(len(v) for v in plan.values())))
    return 0


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--dry']
    sys.exit(main(args[0], args[1], '--dry' in sys.argv))
