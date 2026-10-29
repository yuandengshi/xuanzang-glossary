#!/usr/bin/env python3
"""akbh1_lint.py -- 按《体例草案》第五、六节检查对应实例的切分（核验出处之外的体例检查）。

Usage: python3 -I akbh1_lint.py OCC_TSV [...]
对照规范词目表（align/lemmas.tsv）：异写报 ERROR，未登记的新词目报 WARN。
ERROR：必须改；WARN：逐条复查，确属该词本身的译法可以保留（如 vaiyarthya → 無用、heya → 所斷）。
"""
import csv
import os
import re
import sys
from collections import defaultdict

IDIOM = {'kiṃ kāraṇam', 'kiṃ kāraṇam', 'kiṃ tarhi', 'tathā hi', 'na tu', 'pṛthak', 'santi … yeṣām', 'yad … tad', 'yāvat … tāvat',
         'kim … nāma', 'uktaṃ bhavati', 'na śakyam punar', 'oṃ namo buddhāya', 'tadyathā', 'athavā'}
NEGLEM = re.compile(r'^(a-|an-|na\b|nir|vi|dur|niḥ|a$)|^a[^ā]|^an|vaiyarthya|vaikalya|vigama|nirodha|antareṇa|vinā|varj|heya|tyāga|kṣaya|prahāṇa')
VERB = ('v.', 'ptc.', 'abs.', 'inf.')


def lemma_table(f):
    """读规范词目表（align/lemmas.tsv）：返回（已登记词目集合, 异写→标准写法）。"""
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(f)))), 'lemmas.tsv')
    if not os.path.exists(p):
        return None, {}
    rows = list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    known = {r['lemma'] for r in rows}
    var = {}
    for r in rows:
        for v in filter(None, (x.strip() for x in r['variants'].split('；'))):
            if v not in known:
                var[v] = r['lemma']
    return known, var


def main(files):
    nerr = nwarn = 0
    known, var = lemma_table(files[0]) if files else (None, {})
    seen = defaultdict(list)
    for f in files:
        for r in csv.DictReader(open(f, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE):
            o, x, l, p, t, sk = r['oid'], r['xz'], r['lemma'], r['pos'], r['type'], r['skt']
            msgs = []
            if l and l in var:
                msgs.append(('ERROR', '词目写法不合规范词目表：应作 %s' % var[l]))
            elif l and known is not None and l not in known:
                msgs.append(('WARN', '新词目，规范词目表未登记（确认写法后运行 akbh1_lemmas.py 登记）'))
            if (' + ' in p or ' + ' in l) and l not in IDIOM:
                msgs.append(('ERROR', '两个以上的词并成一条（pos/lemma 含"+"）：应拆开'))
            if t in ('增译', '梵本缺文') or not x:
                pass
            else:
                if re.search('[不非無未]', x) and not NEGLEM.search(l) and not p.startswith('gram') and l not in IDIOM:
                    msgs.append(('WARN', '译语含否定字，词目本身是否含否定？'))
                if p.startswith(VERB) and re.search('[我當已欲令]', x):
                    msgs.append(('WARN', '动词译语含"我當已欲令"：人称、时态、完成、使役应另记为语法形式'))
                if '諸' in x and not re.match(r'(sarva|yad|bahu|-)', l) and not p.startswith('gram'):
                    msgs.append(('WARN', '译语含"諸"：复数应另记'))
                if x.endswith('故') and not p.startswith(('gram', 'ind', 'pron')):
                    msgs.append(('WARN', '译语以"故"结尾：第五格/原因应另记'))
            if p.startswith(('ind', 'pron')) or p.startswith('gram') or l.startswith('-'):
                seen[(l, x or '（未译）')].append(o)
            for lev, m in msgs:
                print('%s\t%s\t%s | %s | %s | %s' % (lev, o, m, sk, l, x))
                nerr += lev == 'ERROR'
                nwarn += lev == 'WARN'
    for k, v in seen.items():
        if len(v) > 2:
            print('INFO\t%s\t虚词/语法形式"%s → %s"有 %d 例（合并后统一裁剪到两例）：%s' % (v[0], k[0], k[1], len(v), ' '.join(v)))
    print('ERROR %d，WARN %d' % (nerr, nwarn))
    return min(nerr, 255)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
