#!/usr/bin/env python3
"""akbh1_morph_todo.py -- 列出需要（补）标形态的记录，附梵文句，供编写形态对照表。

Usage: python3 -I akbh1_morph_todo.py AKBH1_DIR UNIT [UNIT ...] [--all]
  默认只列不合规的记录；--all 列出全部名词类、动词记录（便于统一重标）。
  包括 occ/ 与 occ_extra/（存档例句也要标）。输出 TSV：oid、问题、skt、lemma、pos、xz、末成分、梵文句
  "末成分"栏：复合词记录列出它的末成分（→ U12-009），末成分记录列出它所属的复合词（← U12-012）；
  两者的性数格必须相同。
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import morph  # noqa: E402


def main(d, units, all_):
    skt = {r['sid']: r['text'] for r in csv.DictReader(open(os.path.join(d, 'skt_sent.tsv'), encoding='utf-8'),
                                                        delimiter='\t', quoting=csv.QUOTE_NONE)}
    print('oid\t问题\tskt\tlemma\tpos\txz\t末成分\t梵文句')
    for u in units:
        for sub in ('occ', 'occ_extra'):
            f = os.path.join(d, sub, u + '.tsv')
            if not os.path.exists(f):
                continue
            rows = list(csv.DictReader(open(f, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
            rel = {}
            for m, c in morph.final_members(rows):
                rel.setdefault(m['oid'], []).append('← ' + c['oid'])
                rel.setdefault(c['oid'], []).append('→ ' + m['oid'])
            for r in rows:
                pb = morph.problem(r['pos'], r['type'], r['lemma'])
                head = r['pos'].split(' ')[0] if r['pos'] else ''
                if pb or (all_ and (head in morph.NOMINAL or head == 'v.') and r['type'] not in ('增译', '梵本缺文')):
                    print('\t'.join([r['oid'], pb or '—', r['skt'], r['lemma'], r['pos'], r['xz'],
                                     ' '.join(rel.get(r['oid'], [])) or '—', skt.get(r['sid'], '')]))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--all']
    main(args[0], args[1:], '--all' in sys.argv)
