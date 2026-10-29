#!/usr/bin/env python3
"""akbh1_morph_apply.py -- 套用形态对照表：只改 pos 一栏，其余字段一概不动。

Usage: python3 -I akbh1_morph_apply.py AKBH1_DIR MAP.tsv [MAP2.tsv ...] [--dry]
  MAP.tsv：两栏 oid、pos（带表头），一行一条；oid 可在 occ/ 或 occ_extra/ 中。
  新 pos 必须合形态标注规则（morph.py），否则拒绝并列出；对照表里找不到的 oid 也列出。
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import morph  # noqa: E402


def main(d, maps, dry):
    want = {}
    for m in maps:
        for r in csv.DictReader(open(m, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE):
            want[r['oid'].strip()] = r['pos'].strip()
    done, bad, seen = 0, [], set()
    # 只读写对照表涉及的单位，几个代理分单位同时套用时不会读到别人写到一半的文件
    units = sorted({o.split('-')[0] for o in want})
    for f in [os.path.join(d, sub, u + '.tsv') for sub in ('occ', 'occ_extra') for u in units]:
        if not os.path.exists(f):
            continue
        hdr = open(f, encoding='utf-8').readline().rstrip('\n').split('\t')
        rows = list(csv.DictReader(open(f, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
        ch = False
        for r in rows:
            if r['oid'] not in want:
                continue
            seen.add(r['oid'])
            new = want[r['oid']]
            pb = morph.problem(new, r['type'], r['lemma'])
            if pb:
                bad.append('%s：%s（%s）' % (r['oid'], new, pb)); continue
            if new != r['pos']:
                r['pos'] = new; ch = True; done += 1
        if ch and not dry:
            with open(f, 'w', encoding='utf-8') as fo:
                fo.write('\t'.join(hdr) + '\n')
                for r in rows:
                    fo.write('\t'.join(r[h] for h in hdr) + '\n')
    miss = sorted(set(want) - seen)
    for b in bad:
        print('拒绝', b)
    for m in miss:
        print('找不到', m)
    print('%s改 pos %d 条；拒绝 %d；找不到 %d' % ('（试算）' if dry else '', done, len(bad), len(miss)))
    return 1 if bad or miss else 0


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--dry']
    sys.exit(main(args[0], args[1:], '--dry' in sys.argv))
