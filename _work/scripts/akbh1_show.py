#!/usr/bin/env python3
"""akbh1_show.py -- 打印一个对齐单位的三方原文（带编号与行号），供编写对应实例时对照。

Usage: python3 -I akbh1_show.py AKBH1_DIR UNIT [UNIT ...]
  梵文：sid、Pradhan 页|行、V=本颂、文本
  玄奘、真谛：逐行"行号|文字"（单位边界所在的行整行列出）
"""
import json
import re
import sys


def main(d, units):
    U = {u['unit']: u for u in json.load(open(d + '/units.json', encoding='utf-8'))}
    for name in units:
        u = U[name]
        print('=' * 20, name, '颂', u['karika'])
        for s in u['skt']:
            print('%s [%s]%s %s' % (s['sid'], s['pradhan'], ' V' if s['verse'] == 'V' else '', s['text']))
        for lab, key in (('玄奘 T1558', 'xz'), ('真谛 T1559', 'pm')):
            print('--', lab)
            for ln, t in re.findall(r'〔([0-9a-z]+)〕([^〔]*)', u[key]):
                print('%s|%s' % (ln, t))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
