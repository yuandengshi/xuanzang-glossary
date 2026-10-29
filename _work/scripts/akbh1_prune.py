#!/usr/bin/env python3
"""akbh1_prune.py -- 全局执行"虚词、语法形式每种对应只收一两例"（《体例草案》第六节）。

Usage: python3 -I akbh1_prune.py AKBH1_DIR [--dry]
  按单位顺序，每个（词目, 译语）只留前两例；省译每个词目只留一例。
  多出的记录移到 AKBH1_DIR/occ_extra/ 存档（不删除，以后需要频次时可以恢复）。
  note 中标"待核"的记录一律保留，不占两例的名额；复合词的成分（pos 含"成分"，如 tad-vijñāna 的 tad）是复合词分析的
  一部分，也不裁、不占名额。
"""
import csv
import glob
import os
import sys
from collections import defaultdict

FW = {'ca', 'vā', 'api', 'eva', 'iti', 'tu', 'hi', 'na', 'punar', 'tarhi', 'atha', 'athavā', 'kila', 'khalu', 'tāvat',
      'yathā', 'tathā', 'evam', 'iva', 'atas', 'tatas', 'yatas', 'tatra', 'atra', 'yatra', 'iha', 'yadi', 'cet', 'yadā',
      'tadā', 'tad', 'etad', 'idam', 'adas', 'yad', 'kim', 'katama', 'katara', 'kaścit', 'ah', 'tadyathā', 'nāma',
      'kāmam', 'yasmāt', 'tasmāt', 'as', 'kiṃ tarhi', 'kiṃ kāraṇam', 'tathā hi', 'na tu', 'yāvat … tāvat',
      'santi … yeṣām', 'yad … tad', 'kim … nāma',
      # 子代理 E、G 一致按虚词处理的（2026-10-29 补入）
      'kati', 'yāvat', 'nanu', 'api tu', 'evaṃ tarhi', 'kiṃcit', 'kadācit'}


def is_fw(r):
    return r['pos'].startswith('gram') or r['lemma'].startswith('-') or r['lemma'] in FW


def main(d, dry):
    files = sorted(glob.glob(os.path.join(d, 'occ', 'U*.tsv')))
    count = defaultdict(int)
    kept = moved = 0
    for f in files:
        hdr = open(f, encoding='utf-8').readline().rstrip('\n').split('\t')
        rows = list(csv.DictReader(open(f, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
        keep, extra = [], []
        for r in rows:
            if is_fw(r) and '待核' not in r['note'] and '成分' not in r['pos']:  # 待核的留给用户审；复合词成分不裁
                k = (r['lemma'], r['xz'] if r['type'] != '省译' else '（省译）')
                count[k] += 1
                lim = 1 if r['type'] == '省译' else 2
                if count[k] > lim:
                    extra.append(r); continue
            keep.append(r)
        kept += len(keep); moved += len(extra)
        if dry or not extra:
            continue
        with open(f, 'w', encoding='utf-8') as fo:
            fo.write('\t'.join(hdr) + '\n')
            for r in keep:
                fo.write('\t'.join(r[h] for h in hdr) + '\n')
        os.makedirs(os.path.join(d, 'occ_extra'), exist_ok=True)
        xf = os.path.join(d, 'occ_extra', os.path.basename(f))
        old = set()
        if os.path.exists(xf):
            old = {r['oid'] for r in csv.DictReader(open(xf, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
        new = not os.path.exists(xf)
        with open(xf, 'a', encoding='utf-8') as fo:
            if new:
                fo.write('\t'.join(hdr) + '\n')
            for r in extra:
                if r['oid'] not in old:
                    fo.write('\t'.join(r[h] for h in hdr) + '\n')
    print('%s保留 %d 条，移入存档 %d 条' % ('（试算）' if dry else '', kept, moved))


if __name__ == '__main__':
    main(sys.argv[1], '--dry' in sys.argv[2:])
