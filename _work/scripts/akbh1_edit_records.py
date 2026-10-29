#!/usr/bin/env python3
"""akbh1_edit_records.py -- 改已有记录的个别栏目（skt、lemma、pos、note），改前核验。

Usage: python3 -I akbh1_edit_records.py AKBH1_DIR EDITS.tsv [--dry]
EDITS.tsv 栏目：oid field value（带表头，Tab 分隔）。field 只能是 skt、lemma、pos、note。
skt 须是梵文句的子串，pos 须合形态规则；任何一条不合格，整批都不写入。只读写涉及的单位。
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import akbh1_verify as V  # noqa: E402
import morph  # noqa: E402

FIELDS = ('skt', 'lemma', 'pos', 'note')


def tsv(p):
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))


def main(d, edits, dry):
    skt = {r['sid']: V.nfc(r['text']) for r in tsv(os.path.join(d, 'skt_sent.tsv'))}
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
            for fld, val in want.get(r['oid'], ()):
                seen.add(r['oid'])
                if fld not in FIELDS:
                    errs.append('%s：栏目 %s 不能改' % (r['oid'], fld)); continue
                new = dict(r, **{fld: val})
                if fld == 'skt' and V.nfc(val) not in skt.get(r['sid'], ''):
                    errs.append('%s：skt "%s" 不在 %s' % (r['oid'], val, r['sid'])); continue
                mp = morph.problem(new['pos'], new['type'], new['lemma'])
                if mp:
                    errs.append('%s：%s（%s）' % (r['oid'], new['pos'], mp)); continue
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
