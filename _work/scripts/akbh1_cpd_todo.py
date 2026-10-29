#!/usr/bin/env python3
"""akbh1_cpd_todo.py -- 找出缺整词记录的复合词，输出 JSON，供补写整词记录。

Usage: python3 -I akbh1_cpd_todo.py AKBH1_DIR [UNIT ...] > todo.json
判断：标"成分"的实词记录，句中没有任何复合词记录（cpd. 或带连字符的词目，不标成分）的 skt 包住它，就是"孤立成分"。
从孤立成分起，按句中位置向后接相邻的成分记录（允许连声重叠或相隔一个字母），接到第一个不标"成分"的记录（末成分）为止，
这一串就是一个缺整词记录的复合词。接不到末成分的（末成分没有记录，或标成了"成分"）也列出，final 为空。
每项：unit、sid、skt（复合词在句中的连写形式）、members（按句中次序）、final（末成分 oid）、sentence。
"""
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import morph  # noqa: E402

LEX = morph.NOMINAL + ('ind.',)
BOUND = re.compile(r"[\s/|,;:!?\"“”()\[\]{}.]")
SUFFIX = re.compile(r"[aāiīuū]?(tv|tā|vat|vad|tas|taḥ|to\b|mātr|ka[mṃ]?\b)")   # 派生后缀：链到此为止


def tsv(p):
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))


def spans(chunk, text):
    return [(m.start(), m.end()) for m in re.finditer(re.escape(chunk), text)] if chunk else []


def covering(r):
    # 整词记录；标"成分"的子复合词（如 X-Y 后接 -vat）也包住它下面的成分
    return ('成分' not in r['pos'] and ('-' in r['lemma'] or r['pos'].startswith('cpd.'))) \
        or (r['pos'].startswith('cpd.') and '-' in r['lemma'])


def main(d, units):
    skt = {r['sid']: r['text'] for r in tsv(os.path.join(d, 'skt_sent.tsv'))}
    out = []
    for f in sorted(glob.glob(os.path.join(d, 'occ', 'U*.tsv'))):
        u = os.path.basename(f)[:-4]
        if units and u not in units:
            continue
        rows = [r for r in tsv(f) if r['type'] not in ('增译', '梵本缺文') and r['skt']
                and not r['pos'].startswith('gram') and r['pos'].split(' ')[0] in LEX]
        bysid = {}
        for r in rows:
            bysid.setdefault(r['sid'], []).append(r)
        for sid, rs in bysid.items():
            text = skt.get(sid, '')
            sp = {r['oid']: spans(r['skt'], text) for r in rs}

            cov = [(s, r['oid']) for r in rs if covering(r) for s in sp[r['oid']]]

            def covered(r):
                return any(c[0] <= s[0] and s[1] <= c[1] and o != r['oid'] for s in sp[r['oid']] for c, o in cov)

            def derivative(r):
                # 只有一个词干、后面跟 -tva/-tā/-vat/-tas/-mātra 的派生词，不是复合词
                return any(SUFFIX.match(text[s[1]:s[1] + 6])
                           or re.search(r"(tv|tā|vat|vad|tas|taḥ)", text[s[0]:s[1]][-4:]) for s in sp[r['oid']]) \
                    or '(-vat)' in r['pos']
            orphans = [r for r in rs if '成分' in r['pos'] and not covered(r)]
            used = set()
            for o in orphans:
                if o['oid'] in used:
                    continue
                # 从这个孤立成分的每个出现位置试着向后接链，取最长的一条
                best = None
                for s0 in sp[o['oid']]:
                    chain, end = [(s0, o)], s0[1]
                    # 标 (-vat) 的成分后面是 -vat 后缀，复合词到此为止
                    while (chain[-1][1] is o or '成分' in chain[-1][1]['pos']) and '(-vat)' not in chain[-1][1]['pos'] \
                            and not SUFFIX.match(text[end:end + 6]):
                        nxt = [(s, r) for r in rs if r['oid'] not in {x[1]['oid'] for x in chain}
                               for s in sp[r['oid']] if end - 2 <= s[0] <= end + 1 and s[1] > end
                               and not BOUND.search(text[min(end, s[0]):max(end, s[0])])]
                        if not nxt:
                            break
                        nxt.sort(key=lambda x: (x[0][0], -x[0][1]))
                        chain.append(nxt[0]); end = nxt[0][0][1]
                    if best is None or len(chain) > len(best):
                        best = chain
                # 往前也接：孤立成分前面紧挨着的成分记录（链的起点不一定是第一个孤立成分）
                while True:
                    st = best[0][0][0]
                    prv = [(s, r) for r in rs if '成分' in r['pos'] and r['oid'] not in {x[1]['oid'] for x in best}
                           for s in sp[r['oid']] if st - 1 <= s[1] <= st + 2 and s[0] < st
                           and not BOUND.search(text[min(st, s[1]):max(st, s[1])])]
                    if not prv:
                        break
                    best.insert(0, sorted(prv, key=lambda x: -x[0][1])[0])
                for _, r in best:
                    used.add(r['oid'])
                if len(best) == 1 and derivative(o):
                    continue
                last = best[-1][1]
                fin = last['oid'] if '成分' not in last['pos'] else ''
                a, b = best[0][0][0], best[-1][0][1]
                out.append({'unit': u, 'sid': sid, 'skt': text[a:b], 'final': fin, 'sentence': text,
                            'members': [{k: r[k] for k in ('oid', 'skt', 'lemma', 'pos', 'xz_line', 'xz', 'type', 'pm_line', 'pm', 'note')}
                                        for _, r in best]})
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    print('缺整词记录的复合词 %d 个（其中末成分未定 %d 个）' % (len(out), sum(1 for x in out if not x['final'])), file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1], set(sys.argv[2:]))
