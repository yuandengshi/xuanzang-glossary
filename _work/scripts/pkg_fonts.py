#!/usr/bin/env python3
"""pkg_fonts.py -- 为离线资料包生成字体：按包内页面与数据实际用到的字，抽取 Noto 子集；Gentium 原样附带。

Usage: _work/.venv/bin/python pkg_fonts.py FONT_SRC_DIR PKG_DIR
  FONT_SRC_DIR：下载的字体原文件（_work/src/fonts）
  PKG_DIR：资料包目录；读取其中所有 .html、.js 收集用字，写出 PKG_DIR/fonts/
需要 fontTools、brotli（装在 _work/.venv 中）。
许可：Noto（OFL，无保留字体名）可子集化；Gentium Book Plus 有保留字体名"Gentium""SIL"，
      按 OFL 不得以原名发布修改版，故原样附带、不做子集化。
"""
import glob
import os
import shutil
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

NOTO = [('NotoSerifSC', 'notoserifsc__NotoSerifSC[wght].ttf', 'Noto Serif SC'),
        ('NotoSerifTC', 'notoseriftc__NotoSerifTC[wght].ttf', 'Noto Serif TC'),
        ('NotoSansSC', 'notosanssc__NotoSansSC[wght].ttf', 'Noto Sans SC')]
GENTIUM = [('GentiumBookPlus-Regular.ttf', 'normal', 400), ('GentiumBookPlus-Italic.ttf', 'italic', 400),
           ('GentiumBookPlus-Bold.ttf', 'normal', 700), ('GentiumBookPlus-BoldItalic.ttf', 'italic', 700)]


def used_chars(pkg):
    chars = set()
    for f in glob.glob(os.path.join(pkg, '**', '*.html'), recursive=True) + \
            glob.glob(os.path.join(pkg, '**', '*.js'), recursive=True):
        chars |= set(open(f, encoding='utf-8').read())
    # 常用标点与数字总是带上
    chars |= set('０１２３４５６７８９，。、；：？！「」『』（）《》〈〉…—·“”‘’［］｛｝～')
    chars |= {chr(c) for c in range(0x20, 0x7f)}
    return chars


def main(src, pkg):
    out = os.path.join(pkg, 'fonts')
    os.makedirs(out, exist_ok=True)
    chars = used_chars(pkg)
    cjk = sorted(c for c in chars if ord(c) >= 0x2e80)
    print('收集用字：共 %d，其中汉字及全角符号 %d' % (len(chars), len(cjk)))
    css = []
    for name, fn, family in NOTO:
        f = TTFont(os.path.join(src, fn))
        cmap = f.getBestCmap()
        want = [ord(c) for c in chars if ord(c) in cmap]
        missing = [c for c in cjk if ord(c) not in cmap]
        opts = subset.Options()
        opts.flavor = 'woff2'
        opts.layout_features = ['*']
        opts.name_IDs = ['*']
        opts.notdef_outline = True
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=want)
        sub.subset(f)
        path = os.path.join(out, name + '.woff2')
        f.flavor = 'woff2'
        f.save(path)
        print('%s：%d 字，%.0f KB；该字体缺 %d 字（由其他字体补）' % (name, len(want), os.path.getsize(path) / 1024, len(missing)))
        css.append("@font-face{font-family:'%s';src:url('%s.woff2') format('woff2');font-weight:100 900;font-style:normal;font-display:swap}"
                   % (family, name))
    for fn, style, w in GENTIUM:
        shutil.copy(os.path.join(src, 'gentiumbookplus__' + fn), os.path.join(out, fn))
        css.append("@font-face{font-family:'Gentium Book Plus';src:url('%s') format('truetype');font-weight:%d;font-style:%s;font-display:swap}"
                   % (fn, w, style))
    shutil.copy(os.path.join(src, 'notoserifsc__OFL.txt'), os.path.join(out, 'OFL-Noto.txt'))
    shutil.copy(os.path.join(src, 'gentiumbookplus__OFL.txt'), os.path.join(out, 'OFL-Gentium.txt'))
    open(os.path.join(out, 'fonts.css'), 'w', encoding='utf-8').write('\n'.join(css) + '\n')
    tot = sum(os.path.getsize(p) for p in glob.glob(os.path.join(out, '*')))
    print('fonts/ 合计 %.1f MB' % (tot / 1024 / 1024))


if __name__ == '__main__':
    main(*sys.argv[1:3])
