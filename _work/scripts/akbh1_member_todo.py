#!/usr/bin/env python3
"""akbh1_member_todo.py -- 找出成分记录不全的复合词，输出 JSON，供补写成分记录。

Usage: python3 -I akbh1_member_todo.py AKBH1_DIR [UNIT ...] > todo.json
复合词记录（pos 以 cpd. 起头、词目带连字符）的词目按连字符拆成成分（否定等前缀 a-/an-/sa-/dur-/su- 并入下一个成分；
后缀 -tva/-tā/-vat/-tas/-ka/-mātra/-artham/-tara/-tama 不算成分）。同句中 skt 落在整词 skt 里的记录，
词目（或其中连续的几段）与成分对得上的，算已有；对不上的单词记录（如分词词目写作词根；不计复合词和不变词）抵给剩下的成分。
仍抵不上的成分就是缺的。每项：unit、sid、cpd（整词记录）、have（已有的成分记录）、missing（缺的成分及其在成分中的序号）、
final（缺的是否末成分）、sentence。
"""
import csv
import glob
import json
import os
import re
import sys

PREF = {'a', 'an', 'sa', 'dur', 'su'}
SUF = {'tva', 'tā', 'vat', 'tas', 'ka', 'mātra', 'artham', 'tara', 'tama'}


def tsv(p):
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))


def norm(x):
    """比较用：去连字符，-an/-as/-us 词干与复合词里的形式视为相同。"""
    x = x.replace('-', '')
    return re.sub(r'(an|as|us|is|at|in)$', lambda m: {'an': 'a', 'as': 'a', 'us': 'u', 'is': 'i', 'at': 'a', 'in': 'i'}[m.group(1)], x)


def units(lemma):
    ps, out, i = lemma.split('-'), [], 0
    while i < len(ps):
        if ps[i] in PREF and i + 1 < len(ps):
            out.append(ps[i] + '-' + ps[i + 1]); i += 2
        else:
            out.append(ps[i]); i += 1
    return out


def main(d, wanted):
    skt = {r['sid']: r['text'] for r in tsv(os.path.join(d, 'skt_sent.tsv'))}
    out = []
    for f in sorted(glob.glob(os.path.join(d, 'occ', 'U*.tsv'))):
        u = os.path.basename(f)[:-4]
        if wanted and u not in wanted:
            continue
        rows = tsv(f)
        for c in rows:
            if not c['pos'].startswith('cpd.') or '-' not in c['lemma'] or c['type'] in ('增译', '梵本缺文') or not c['skt']:
                continue
            us = units(c['lemma'])
            idx = [k for k, x in enumerate(us) if x not in SUF]
            if len(idx) < 2:
                continue
            mem = [m for m in rows if m is not c and m['sid'] == c['sid'] and m['skt'] and m['lemma']
                   and m['type'] not in ('增译', '梵本缺文') and not m['pos'].startswith('gram')
                   and (m['skt'] in c['skt'] or (c['skt'] in m['skt'] and len(m['skt']) <= len(c['skt']) + 3))
                   and units(m['lemma']) != us]
            cov, used = set(), set()
            nu = [norm(x) for x in us]
            for m in mem:
                mu = [norm(x) for x in units(m['lemma'])]
                for k in range(len(nu) - len(mu) + 1):
                    if nu[k:k + len(mu)] == mu:
                        cov.update(range(k, k + len(mu))); used.add(m['oid'])
                        break
                else:
                    # 整段比较（mahābhūta 对 mahā-bhūta）
                    j = ''.join(mu)
                    for a in range(len(nu)):
                        for b in range(a + 1, len(nu) + 1):
                            if ''.join(nu[a:b]) == j:
                                cov.update(range(a, b)); used.add(m['oid'])
                                break
                        if m['oid'] in used:
                            break
            miss = [k for k in idx if k not in cov]
            # 词目对不上的单词记录（分词写作词根等）按次序抵给剩下的成分
            rest = [m for m in mem if m['oid'] not in used and not m['pos'].startswith(('cpd.', 'ind.'))]
            if len(rest) >= len(miss):
                continue
            miss = miss[len(rest):] if rest else miss
            out.append({'unit': u, 'sid': c['sid'], 'sentence': skt.get(c['sid'], ''),
                        'cpd': {k: c[k] for k in ('oid', 'skt', 'lemma', 'pos', 'xz_line', 'xz', 'type', 'pm_line', 'pm', 'note')},
                        'have': [{k: m[k] for k in ('oid', 'skt', 'lemma', 'pos', 'xz', 'type')} for m in mem],
                        'missing': [us[k] for k in miss], 'final': idx[-1] in miss})
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    print('成分记录不全的复合词 %d 个，缺成分 %d 个（其中末成分 %d 个）' % (
        len(out), sum(len(x['missing']) for x in out), sum(x['final'] for x in out)), file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1], set(sys.argv[2:]))
