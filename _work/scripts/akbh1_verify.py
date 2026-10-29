#!/usr/bin/env python3
"""akbh1_verify.py -- 核验对应实例：梵文原形、玄奘译语、真谛译语是否确实出现在所标出处。

Usage: python3 -I akbh1_verify.py AKBH1_DIR [OCC_TSV ...]
  不给 OCC_TSV 时核验 AKBH1_DIR/occ/ 下全部 .tsv
规则（见《体例草案》五）：
  skt 必须是 sid 所指梵文句的子串（NFC）；
  xz/pm 按"…"分段，每段须出现在所标行与下一行拼成的窗口中，且第一段须起于所标行。
输出：错误清单；返回码 = 错误条数（0 为全部通过）。
"""
import csv
import glob
import os
import sys
import unicodedata

TYPES = {'对译', '意译', '音译', '增译', '省译', '拆译', '合译', '语法', '梵本缺文'}


def nfc(s):
    return unicodedata.normalize('NFC', s)


def lines(path):
    rows = [(r['line'], r['text']) for r in csv.DictReader(open(path, encoding='utf-8'), delimiter='\t',
                                                            quoting=csv.QUOTE_NONE)]
    idx = {n: i for i, (n, _) in enumerate(rows)}
    return rows, idx


def found(rows, idx, ln, s):
    if ln not in idx:
        return '行号 %s 不存在' % ln
    i = idx[ln]
    cur = rows[i][1]
    win = cur + (rows[i + 1][1] if i + 1 < len(rows) else '')
    parts = [p for p in s.split('…') if p]
    p0 = win.find(parts[0])
    if p0 < 0 or p0 >= len(cur):
        return '"%s" 不在 %s 起始处（窗口：%s）' % (parts[0], ln, win)
    for p in parts[1:]:
        if p not in win:
            return '"%s" 不在 %s–次行窗口内' % (p, ln)
    return ''


def main(d, files):
    skt = {r['sid']: nfc(r['text']) for r in csv.DictReader(open(os.path.join(d, 'skt_sent.tsv'), encoding='utf-8'),
                                                             delimiter='\t', quoting=csv.QUOTE_NONE)}
    xz, xi = lines(os.path.join(d, 'xz_lines.tsv'))
    pm, pi = lines(os.path.join(d, 'pm_lines.tsv'))
    files = files or sorted(glob.glob(os.path.join(d, 'occ', '*.tsv')))
    n = bad = 0
    seen = set()
    for f in files:
        for r in csv.DictReader(open(f, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE):
            n += 1
            errs = []
            if r['oid'] in seen:
                errs.append('oid 重复')
            seen.add(r['oid'])
            if r['type'] not in TYPES:
                errs.append('type 不合法：%s' % r['type'])
            if r['sid'] not in skt:
                errs.append('sid 不存在')
            elif r['skt'] and nfc(r['skt']) not in skt[r['sid']]:
                errs.append('skt "%s" 不在 %s：%s' % (r['skt'], r['sid'], skt[r['sid']][:120]))
            if r['type'] in ('增译', '梵本缺文') and r['skt']:
                errs.append('%s不应有 skt' % r['type'])
            if r['type'] == '省译' and r['xz']:
                errs.append('省译不应有 xz')
            if r['type'] not in ('增译', '梵本缺文') and not r['skt']:
                errs.append('缺 skt')
            if r['type'] != '省译':
                if not r['xz'] or not r['xz_line']:
                    errs.append('缺 xz 或 xz_line')
                else:
                    e = found(xz, xi, r['xz_line'], r['xz'])
                    if e:
                        errs.append('玄奘：' + e)
            if r['pm']:
                e = found(pm, pi, r['pm_line'], r['pm'])
                if e:
                    errs.append('真谛：' + e)
            if errs:
                bad += 1
                print('%s\t%s' % (r['oid'], '；'.join(errs)))
    print('核验 %d 条，错误 %d 条' % (n, bad))
    return min(bad, 255)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2:]))
