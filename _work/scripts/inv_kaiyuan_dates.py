#!/usr/bin/env python3
"""inv_kaiyuan_dates.py -- 抽出《开元录》卷八玄奘译经目录的结构化条目（题名、卷数、夹注）。

Usage: python3 -I inv_kaiyuan_dates.py T55n2154.xml OUT.tsv
夹注里记有译出时间、地点、笔受者等。
"""
import re
import sys


def clean(s):
    s = re.sub(r'<lb\b[^>]*/>|<pb\b[^>]*/>|<anchor\b[^>]*/>', '', s)
    s = re.sub(r'<app\b[^>]*>.*?<lem\b[^>]*>(.*?)</lem>.*?</app>', r'\1', s, flags=re.S)
    s = re.sub(r'<g\b[^>]*ref="#([^"]+)"[^>]*/>', r'[\1]', s)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', '', s)


def main(path, out):
    x = open(path, encoding='utf-8').read()
    j = x.index('右七十六部一千三百四十七卷')
    i = x.rindex('<item', 0, x.rindex('大般若波羅蜜多經</cb:jl_title>', 0, j))
    seg = x[i:j]
    rows = []
    for k, (ln, body) in enumerate(re.findall(r'<item\b[^>]*xml:id="itemT55p([0-9a-z]+)"[^>]*>(.*?)</item>', seg, flags=re.S), 1):
        title = clean(''.join(re.findall(r'<cb:jl_title>(.*?)</cb:jl_title>', body, flags=re.S)))
        juan = clean(''.join(re.findall(r'<cb:jl_juan\b[^>]*>(.*?)</cb:jl_juan>', body, flags=re.S)))
        note = clean(''.join(re.findall(r'<note place="inline">(.*?)</note>', body, flags=re.S)))
        rows.append([str(k), 'T55.' + ln[:4] + ln[4] + ln[5:7], title, juan, note])
    with open(out, 'w', encoding='utf-8') as f:
        f.write('序\t出處\t題名\t卷\t夾注\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    print(len(rows), 'items')


if __name__ == '__main__':
    main(*sys.argv[1:3])
