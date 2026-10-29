#!/usr/bin/env python3
"""inv_lancaster.py -- 从 Lancaster《高丽大藏经解题目录》抓取玄奘译本的梵名、藏名、东北目录号、同本异译。

Usage: python3 -I inv_lancaster.py INDEX_TAISHO_HTML CACHE_DIR KAIYUAN_TSV OUT.tsv
  CACHE_DIR：K 页缓存目录（不可信数据，只读取文本）
输出 TSV：T号、K号、梵名(i)、梵名异称(5 var.)、藏名(ii)、Tohoku、译出年、cf.(K→T)、K页URL
"""
import html
import os
import re
import sys
import time
import urllib.request

BASE = 'http://www.acmuller.net/descriptive_catalogue/files/'
# 開元錄有、CBETA 不归玄奘名下的两部
EXTRA = {'能斷金剛般若波羅蜜多經': '220-09', '大菩薩藏經': '310-12'}


def t_index(path):
    t = open(path, encoding='utf-8', errors='replace').read()
    m = {}
    for tn, body in re.findall(r'<p>T ([0-9]+(?:-[0-9]+)?)(?:&#160;)+\s*(.*?)</p>', t):
        m[tn] = re.findall(r'href="\.\./files/(k[0-9-]+\.html)"', body)
    return m


def fetch(page, cache):
    fp = os.path.join(cache, page)
    if not os.path.exists(fp):
        with urllib.request.urlopen(BASE + page, timeout=60) as r:
            data = r.read()
        open(fp, 'wb').write(data)
        time.sleep(0.5)
    return open(fp, encoding='utf-8', errors='replace').read()


def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def parse(page_html):
    x = text(page_html)
    skt = re.search(r'\(i\)\s*(.*?)\s*\((?:ii|iii)\)', x)
    tib = re.search(r'\(ii\)\s*(.*?)\s*\(iii\)', x)
    to = re.findall(r'To\. ?([0-9]+(?:-[0-9]+)?[a-z]?)', x)
    cf = re.search(r'\(1\) cf\.?\s*(.*?)\s*\(2\)', x)
    cfk = re.findall(r'K\.\s*([0-9]+(?:\([0-9]+\))?)', cf.group(1)) if cf else []
    var = re.search(r'\(5\) var\.\s*(.*?)\s*(?:\([0-9]\)|[0-9]\. T|Next Entry)', x)
    date = re.search(r'Translation by Hs\u00fcan-tsang:.*?\((?:[A-Z][a-z]+ [0-9]+[a-z]*, )?A\.D\. ?([0-9]{3})', x)
    return {'skt': skt.group(1).strip(' .') if skt else '',
            'tib': tib.group(1).strip(' .') if tib else '',
            'to': ','.join(to), 'cfk': cfk,
            'var': var.group(1).strip(' .') if var else '',
            'year': date.group(1) if date else ''}


def main(idx, cache, kytsv, out):
    os.makedirs(cache, exist_ok=True)
    tmap = t_index(idx)
    k2t = {}
    for tn, pages in tmap.items():
        for p in pages:
            k2t.setdefault(p, tn)
    rows = []
    for line in open(kytsv, encoding='utf-8').read().splitlines()[1:]:
        c = line.split('\t')
        tno = c[3][1:].lstrip('0') if c[3].startswith('T') else EXTRA.get(c[1], '')
        if not tno:
            continue
        for p in tmap.get(tno, []):
            d = parse(fetch(p, cache))
            cft = []
            for k in d['cfk']:
                kp = 'k%04d' % int(re.match(r'[0-9]+', k).group())
                sub = re.search(r'\(([0-9]+)\)', k)
                kp += ('-%02d' % int(sub.group(1)) if sub else '') + '.html'
                cft.append('K%s=T%s' % (k, k2t.get(kp, '?')))
            rows.append(['T' + tno, p[:-5].upper(), d['skt'], d['var'], d['tib'], d['to'], d['year'], ';'.join(cft), BASE + p])
    with open(out, 'w', encoding='utf-8') as f:
        f.write('T\tK\t梵名\t梵名异称\t藏名\tTohoku\t译出年\tcf\tURL\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    print(len(rows), 'rows')


if __name__ == '__main__':
    main(*sys.argv[1:5])
