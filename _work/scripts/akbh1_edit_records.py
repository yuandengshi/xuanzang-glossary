#!/usr/bin/env python3
"""akbh1_edit_records.py -- 改已有记录的个别栏目，改后按 akbh1_verify.py 与形态规则核验整条记录。

Usage: python3 -I akbh1_edit_records.py AKBH1_DIR EDITS.tsv [--dry]
EDITS.tsv 栏目：oid field value（带表头，Tab 分隔）。field 可以是 skt、lemma、pos、note、type、xz、xz_line、pm、pm_line
（oid、sid 不能改）。同一条的几处改动一并套用后再核验；任何一条不合格，整批都不写入。只读写涉及的单位。
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import akbh1_verify as V  # noqa: E402
import morph  # noqa: E402

FIELDS = ('skt', 'lemma', 'pos', 'note', 'type', 'xz', 'xz_line', 'pm', 'pm_line')


def tsv(p):
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))


def main(d, edits, dry):
    skt = {r['sid']: V.nfc(r['text']) for r in tsv(os.path.join(d, 'skt_sent.tsv'))}
    xz, xi = V.lines(os.path.join(d, 'xz_lines.tsv'))
    pm, pi = V.lines(os.path.join(d, 'pm_lines.tsv'))
    want = {}
    for e in tsv(edits):
        want.setdefault(e['oid'].strip(), []).append((e['field'].strip(), e['value'].strip()))
    units = sorted({o.split('-')[0] for o in want})
    errs, changed, files = [], [], {}
    for u in units:
        for sub in ('occ', 'occ_extra'):
            f = os.path.join(d, sub, u + '.tsv')
            if os.path.exists(f):
                files[f] = tsv(f)
    seen = set()
    for f, rows in files.items():
        for r in rows:
            eds = want.get(r['oid'])
            if not eds:
                continue
            seen.add(r['oid'])
            bad = [fld for fld, _ in eds if fld not in FIELDS]
            if bad:
                errs.append('%s：栏目 %s 不能改' % (r['oid'], '、'.join(bad))); continue
            new = dict(r)
            for fld, val in eds:
                new[fld] = val
            e = []
            if new['type'] not in V.TYPES:
                e.append('type 不合法')
            if new['type'] not in ('增译', '梵本缺文') and (not new['skt'] or V.nfc(new['skt']) not in skt.get(r['sid'], '')):
                e.append('skt "%s" 不在 %s' % (new['skt'], r['sid']))
            if new['type'] == '省译' and new['xz']:
                e.append('省译不应有 xz')
            if new['type'] != '省译':
                m = V.found(xz, xi, new['xz_line'], new['xz']) if new['xz'] and new['xz_line'] else '缺 xz 或 xz_line'
                if m:
                    e.append('玄奘：' + m)
            if new['pm']:
                m = V.found(pm, pi, new['pm_line'], new['pm'])
                if m:
                    e.append('真谛：' + m)
            mp = morph.problem(new['pos'], new['type'], new['lemma'])
            if mp:
                e.append('形态：%s（%s）' % (new['pos'], mp))
            if e:
                errs.append('%s：%s' % (r['oid'], '；'.join(e))); continue
            for fld, val in eds:
                if r[fld] != val:
                    changed.append('%s %s：%s → %s' % (r['oid'], fld, r[fld], val))
                    r[fld] = val
    for o in sorted(set(want) - seen):
        errs.append('%s：找不到' % o)
    for e in errs:
        print('不合格', e)
    if errs:
        print('有 %d 处不合格，整批未写入' % len(errs)); return 1
    for c in changed:
        print(('（试算）' if dry else '') + c)
    if not dry:
        for f, rows in files.items():
            hdr = open(f, encoding='utf-8').readline().rstrip('\n').split('\t')
            with open(f, 'w', encoding='utf-8') as fo:
                fo.write('\t'.join(hdr) + '\n')
                for r in rows:
                    fo.write('\t'.join(r[h] for h in hdr) + '\n')
    print('%s改 %d 处' % ('（试算）' if dry else '', len(changed)))
    return 0


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--dry']
    sys.exit(main(args[0], args[1], '--dry' in sys.argv))
