#!/usr/bin/env python3
"""akbh1_calib.py -- 与香港教育大学"梵漢對勘雙語語料庫"（俱舍论部分）比对玄奘译语，作为校准。

Usage: python3 -I akbh1_calib.py EDUHK_DIR AKBH1_DIR PAGEMAP OUT_TSV
  EDUHK_DIR：已下载的页面（不可信数据，只当文本读）
  PAGEMAP：页码范围→单位，如 "1-24:U01,25-38:U02,39-44:U03,45-51:U04,52-100:U05"
做法：对勘块每组四行（梵、真谛、玄奘、语法）按显示宽度（全角=2）对列，
  把玄奘行的词归到起始列不大于它的梵文词下；再到本方同一单位的实例里找同一梵文词，比较汉译。
结果：一致 / 不同 / 我方缺；只在本地比对，不转载对方数据。
"""
import csv
import glob
import html
import os
import re
import sys
import unicodedata


def width(ch):
    return 2 if unicodedata.east_asian_width(ch) in ('W', 'F') else (0 if unicodedata.combining(ch) else 1)


def tokens(line):
    out, col, cur, start = [], 0, '', 0
    for ch in line:
        if ch == '\t':
            if cur:
                out.append((start, cur)); cur = ''
            col = (col // 8 + 1) * 8
            continue
        if ch.isspace():
            if cur:
                out.append((start, cur)); cur = ''
            col += width(ch)
            continue
        if not cur:
            start = col
        cur += ch
        col += width(ch)
    if cur:
        out.append((start, cur))
    return out


def norm(s):
    s = unicodedata.normalize('NFC', s.lower())
    s = re.sub(r'[^a-zāīūṛṝḷṃḥṅñṭḍṇśṣ]', '', s)
    return s


STRIP = re.compile(r'(asya|ānāṃ|ānām|ebhyaḥ|ebhiḥ|eṇa|ena|āya|ayā|āyāḥ|eṣu|ataḥ|atā|aḥ|āḥ|aṃ|am|āt|ād|ena|ī|ā|a|e|i|u|o|ḥ|ṃ|m)$')


def stem(s):
    s = norm(s)
    for _ in range(2):
        s2 = STRIP.sub('', s)
        if len(s2) < 3:
            break
        s = s2
    return s


GRAM = re.compile(r'[陽中陰][單雙複]|\bind\b|釋|ppp|ptc|abs|ger|inf')
LATIN = re.compile(r'[a-zāīūṛṝṃḥṅñṭḍṇśṣ]{2,}')
CJK = re.compile(r'[\u4e00-\u9fff]')


def pairs(path):
    """按行的角色切组：含拉丁字母、无汉字 → 梵文行；其后两行非语法的汉字行依次为真谛、玄奘。"""
    t = open(path, encoding='utf-8', errors='replace').read()
    out = []
    for pre in re.findall(r'<pre>(.*?)</pre>', t, flags=re.S):
        ls = [l for l in html.unescape(re.sub(r'<[^>]+>', '', pre)).split('\n') if l.strip()]
        i = 0
        while i < len(ls):
            if LATIN.search(ls[i]) and not CJK.search(ls[i]):
                zh = []
                j = i + 1
                while j < len(ls) and len(zh) < 2 and not (LATIN.search(ls[j]) and not CJK.search(ls[j])):
                    if CJK.search(ls[j]) and not GRAM.search(ls[j]):
                        zh.append(ls[j])
                    j += 1
                if len(zh) == 2:
                    sk, xz = tokens(ls[i]), tokens(zh[1])
                    for c, z in xz:
                        owner = [x for x in sk if x[0] <= c + 1]
                        out.append((owner[-1][1] if owner else sk[0][1], z))
                i = j
            else:
                i += 1
    merged = []
    for tok, z in out:
        if merged and merged[-1][0] == tok:
            merged[-1] = (tok, merged[-1][1] + ' ' + z)
        else:
            merged.append((tok, z))
    return merged


VAR = str.maketrans({'毗': '毘', '湣': '愍', '雲': '云', '迴': '回'})


def agree(o, z):
    """字集合比较（对方按梵文词序排汉字，与汉文语序可能不同）；先归一异体字及对方的繁简误转（雲何→云何）。"""
    a, b = set(o.translate(VAR)), set(z.translate(VAR))
    return bool(a) and bool(b) and (a <= b or b <= a)


def main(edir, adir, pmap, out):
    ranges = []
    for part in pmap.split(','):
        r, u = part.split(':')
        a, b = r.split('-')
        ranges.append((int(a), int(b), u))
    occ = {}
    for f in glob.glob(os.path.join(adir, 'occ', '*.tsv')):
        u = os.path.basename(f)[:-4]
        occ[u] = list(csv.DictReader(open(f, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    rows, stat = [], {'一致': 0, '不同': 0, '我方缺': 0}
    for a, b, u in ranges:
        recs = [r for r in occ.get(u, []) if r['xz']]
        for p in range(a, b + 1):
            f = os.path.join(edir, 'p%04d.html' % p)
            if not os.path.exists(f):
                continue
            for tok, z in pairs(f):
                zc = re.sub(r'[\s…\.．]', '', z)
                zc = re.sub(r'[0-9①-⑳]', '', zc)
                if not zc or not norm(tok):
                    continue
                st = stem(tok)
                if len(st) < 4:
                    cand = [r for r in recs if norm(r['lemma']) == norm(tok) or stem(r['lemma']) == st]
                else:
                    cand = [r for r in recs if st in norm(r['lemma']) or st in norm(r['skt'])]
                if not cand:
                    rows.append([u, 'p%d' % p, tok, zc, '', '', '我方缺']); stat['我方缺'] += 1
                    continue
                ours = [r['xz'].replace('…', '') for r in cand]
                ok = [o for o in ours if agree(o, zc)]
                v = '一致' if ok else '不同'
                stat[v] += 1
                rows.append([u, 'p%d' % p, tok, zc, '／'.join(dict.fromkeys(ours)),
                             '／'.join(dict.fromkeys(r['oid'] for r in cand)), v])
    with open(out, 'w', encoding='utf-8') as f:
        f.write('unit\tpage\teduhk_skt\teduhk_xz\tours_xz\tours_oid\tverdict\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    tot = sum(stat.values())
    print('对方词对 %d：一致 %d（%.0f%%），不同 %d，我方缺 %d' % (
        tot, stat['一致'], 100 * stat['一致'] / tot, stat['不同'], stat['我方缺']))


if __name__ == '__main__':
    main(*sys.argv[1:5])
