#!/usr/bin/env python3
"""akbh1_review.py -- 生成《待核清单》：标"待核"的对应、梵本缺文（自动），人工整理的梵本问题（review_notes.md），
以及形态标注存疑（pos 带 "(?)"，含存档例句；自动）。

Usage: python3 -I akbh1_review.py AKBH1_DIR OUT_MD
"""
import csv
import glob
import os
import sys


def tsv(p):
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))


def pref(p):
    try:
        pg, ln = p.split('-')[0].split('|')
        return '%d.%d' % (int(pg), int(ln))
    except (ValueError, IndexError):
        return p or '?'


def tref(ln):
    return '%d%s' % (int(ln[:4]), ln[4:]) if ln else ''


def esc(s):
    return s.replace('|', '｜')


def main(d, out):
    skt = {r['sid']: r for r in tsv(os.path.join(d, 'skt_sent.tsv'))}
    occ = []
    for f in sorted(glob.glob(os.path.join(d, 'occ', 'U*.tsv'))):
        u = os.path.basename(f)[:-4]
        for r in tsv(f):
            r['unit'] = u
            occ.append(r)
    pend = [r for r in occ if '待核' in r['note']]
    lac = [r for r in occ if r['type'] == '梵本缺文']
    L = ['# 俱舍论·界品 待核清单', '',
         '由七批子代理编写、主会话合并时汇总。第一、二部分从实例数据自动生成；第三部分以下据各批汇报整理。'
         '出处写法：P = Pradhan 本页.行；T = 大正藏 T29 页栏行（玄奘 T1558）；真谛出处同（T1559）。', '',
         '## 一、待核的对应（%d 条）' % len(pend), '',
         '| 编号 | 出处 | 梵文 | 词目 | 玄奘 | 真谛 | 说明 |', '|---|---|---|---|---|---|---|']
    for r in pend:
        s = skt[r['sid']]
        L.append('| %s | P %s · T %s | %s | %s | %s | %s | %s |' % (
            r['oid'], pref(s['pradhan']), tref(r['xz_line']), esc(r['skt']) or '—', esc(r['lemma']) or '—',
            esc(r['xz']) or '（未译）', esc(r['pm']) or '—', esc(r['note'])))
    L += ['', '## 二、梵本缺文（%d 处）' % len(lac), '',
          '两个汉译都有、现存梵本没有的内容，疑玄奘、真谛所据梵本有之。', '',
          '| 编号 | 梵文句 | 玄奘 | 真谛 | 说明 |', '|---|---|---|---|---|']
    for r in lac:
        L.append('| %s | %s（P %s） | %s（T %s） | %s | %s |' % (
            r['oid'], r['sid'], pref(skt[r['sid']]['pradhan']), esc(r['xz']), tref(r['xz_line']),
            esc(r['pm']) or '—', esc(r['note'])))
    L += ['', open(os.path.join(d, 'review_notes.md'), encoding='utf-8').read().rstrip('\n')]
    morph = [r for sub in ('occ', 'occ_extra') for f in sorted(glob.glob(os.path.join(d, sub, 'U*.tsv')))
             for r in tsv(f) if '(?)' in r['pos']]
    L += ['', '## 八、形态存疑（%d 条）' % len(morph), '',
          '性、数、格或时态据词形和上下文仍不能确定的，取了最可能的一种，pos 末尾加 (?)。', '',
          '| 编号 | 梵文 | 词目 | 形态 | 玄奘 | 说明 |', '|---|---|---|---|---|---|']
    for r in sorted(morph, key=lambda r: r['oid']):
        L.append('| %s | %s | %s | %s | %s | %s |' % (r['oid'], esc(r['skt']) or '—', esc(r['lemma']) or '—',
                 esc(r['pos']), esc(r['xz']) or '（未译）', esc(r['note']) or '—'))
    L.append('')
    open(out, 'w', encoding='utf-8').write('\n'.join(L))
    print('待核 %d 条，梵本缺文 %d 处，形态存疑 %d 条' % (len(pend), len(lac), len(morph)))


if __name__ == '__main__':
    main(*sys.argv[1:3])
